#!/usr/bin/env python3
"""Build public releases using Python 3.10+ and the standard library only."""

from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import zipfile


ROOT_FILES = {"README.md", "LICENSE", "VERSION", ".gitignore"}
PUBLIC_DIRECTORIES = {"skills", "docs", "examples", "scripts", "tests"}
TEXT_SUFFIXES = {".md", ".txt", ".rst", ".yaml", ".yml", ".py", ".toml", ".json", ".csv", ".tsv"}
EXCLUDED_PARTS = {
    "private", "decisions", ".git", ".agents", ".env", "__pycache__", "dist",
    ".cache", "cache", "caches", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".venv", "venv", "node_modules", "build",
}
SKILL = PurePosixPath("skills/musk-decision")
INLINE_FILES = {
    "SKILL.md": "skill-instructions",
    "references/decision-framework.md": "decision-framework",
    "references/sources.md": "sources",
    "assets/current-state.md": "current-state",
}
# Markdown links are deliberately limited to ordinary inline/reference links.
INLINE_LINK = re.compile(r"(!?\[[^\]\n]*\]\()([^\s)]+)([^)\n]*\))")
REFERENCE_LINK = re.compile(r"^(\s{0,3}\[[^\]\n]+\]:\s*)(\S+)(.*)$", re.MULTILINE)


def _is_excluded(relative: Path) -> bool:
    if relative == Path(".gitignore"):
        return False
    return any(
        part.startswith(".") or part.casefold() in EXCLUDED_PARTS
        for part in relative.parts
    )


def _is_link_or_reparse(path: Path) -> bool:
    """Detect Unix links and Windows reparse points without following them."""
    try:
        entry = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(entry.st_mode) or bool(
        getattr(entry, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _path_traverses_link_or_reparse(path: Path) -> bool:
    return any(_is_link_or_reparse(part) for part in (path, *path.parents))


def _is_public_file(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if _is_excluded(relative):
        return False
    if any(_is_link_or_reparse(root / Path(*relative.parts[:i])) for i in range(1, len(relative.parts) + 1)):
        return False
    if not path.is_file():
        return False
    if len(relative.parts) == 1:
        return relative.name in ROOT_FILES
    return relative.parts[0] in PUBLIC_DIRECTORIES and path.suffix.lower() in TEXT_SUFFIXES


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    if "\0" in text:
        raise ValueError(f"Binary content is not publishable: {path}")
    return text


def _public_paths(root: Path):
    """Prune excluded directories instead of traversing private state."""
    for name in sorted(ROOT_FILES):
        path = root / name
        if _is_public_file(root, path):
            yield path
    for name in sorted(PUBLIC_DIRECTORIES):
        directory = root / name
        if _is_link_or_reparse(directory) or not directory.is_dir():
            continue
        for current, directories, filenames in os.walk(directory, topdown=True, followlinks=False):
            current_path = Path(current)
            directories[:] = sorted(
                name for name in directories
                if not _is_excluded((current_path / name).relative_to(root))
                and not _is_link_or_reparse(current_path / name)
            )
            for filename in sorted(filenames):
                path = current_path / filename
                if _is_public_file(root, path):
                    yield path


def _without_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text.strip()
    lines = text.splitlines()
    for index, line in enumerate(lines[1:], 1):
        if line == "---":
            return "\n".join(lines[index + 1:]).strip()
    raise ValueError("SKILL.md has unclosed YAML frontmatter")


def _local_target(source: PurePosixPath, target: str) -> PurePosixPath | None:
    """Return a normalized local file target; remote URLs and anchors need no file."""
    target = target.removeprefix("<").removesuffix(">")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path).replace("\\", "/")
    if path.startswith("/"):
        raise ValueError(f"Absolute local link is not portable: {target}")
    parts: list[str] = list(source.parent.parts)
    for part in PurePosixPath(path).parts:
        if part == "..":
            if not parts:
                raise ValueError(f"Link escapes repository: {target}")
            parts.pop()
        elif part != ".":
            parts.append(part)
    return PurePosixPath(*parts)


def _link_targets(text: str):
    for match in INLINE_LINK.finditer(text):
        yield match.group(2)
    for match in REFERENCE_LINK.finditer(text):
        yield match.group(2)


def _standalone_prompt(files: dict[str, bytes]) -> str:
    anchors = {str(SKILL / name): anchor for name, anchor in INLINE_FILES.items()}
    sections = ["# 马斯克式决策顾问：ChatGPT 完整指令\n\n"
                "以下是可在普通聊天中使用的完整指令和参考资料。它是受公开资料启发的非官方方法。\n"]
    for name, anchor in INLINE_FILES.items():
        source = SKILL / name
        content = files[str(source)].decode("utf-8")
        if name == "SKILL.md":
            content = _without_frontmatter(content)

        def replace_target(target: str) -> str:
            local = _local_target(source, target)
            if local is None:
                return target
            key = str(local)
            if key not in anchors:
                raise ValueError(f"Standalone instructions cannot inline {source}: {target}")
            return "#" + anchors[key]

        content = INLINE_LINK.sub(
            lambda match: match.group(1) + replace_target(match.group(2)) + match.group(3), content
        )
        content = REFERENCE_LINK.sub(
            lambda match: match.group(1) + replace_target(match.group(2)) + match.group(3), content
        )
        sections.append(f'<a id="{anchor}"></a>\n\n{content.strip()}\n')
    return "\n\n---\n\n".join(sections) + "\n"


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(entries.items()):
            # Stable metadata keeps identical sources reproducible.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)


def build_release(root: Path, output_dir: Path) -> list[Path]:
    """Validate inputs, then write the install ZIP, source ZIP and ChatGPT prompt."""
    root = Path(root).absolute()
    output_dir = Path(output_dir).absolute()
    if _path_traverses_link_or_reparse(root) or not root.is_dir():
        raise ValueError("Repository root must not traverse links or reparse points")
    if _path_traverses_link_or_reparse(output_dir):
        raise ValueError("Output directory must not traverse links or reparse points")

    required = {"VERSION", "LICENSE", "README.md"} | {str(SKILL / name) for name in INLINE_FILES}
    for name in sorted(required):
        path = root / name
        if not _is_public_file(root, path):
            raise FileNotFoundError(f"Missing or unsafe required release file: {name}")
    version = _read_text(root / "VERSION").strip()
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version):
        raise ValueError("VERSION must use three numeric components, such as 0.1.0")

    files: dict[str, bytes] = {}
    for path in _public_paths(root):
        # Never include a custom output directory under the public source tree.
        if path == output_dir or output_dir in path.parents:
            continue
        relative = path.relative_to(root).as_posix()
        try:
            files[relative] = _read_text(path).encode("utf-8")
        except (UnicodeDecodeError, ValueError):
            if relative in required:
                raise
            continue

    for name in required:
        if name not in files:
            raise FileNotFoundError(f"Required release file is excluded: {name}")
    # Resolve every local Markdown link in the Skill before creating output.
    for name, content in files.items():
        if not name.startswith(str(SKILL) + "/") or not name.endswith(".md"):
            continue
        for target in _link_targets(content.decode("utf-8")):
            local = _local_target(PurePosixPath(name), target)
            if local is not None and str(local) not in files:
                raise FileNotFoundError(f"Missing or excluded reference in {name}: {target}")
    prompt = _standalone_prompt(files)
    install_files = {
        "musk-decision/" + name[len(str(SKILL)) + 1:]: content
        for name, content in files.items() if name.startswith(str(SKILL) + "/")
    }
    install_files["musk-decision/LICENSE"] = files["LICENSE"]

    paths = [
        output_dir / f"musk-decision-v{version}.zip",
        output_dir / f"ai-musk-skill-v{version}.zip",
        output_dir / "chatgpt-instructions.md",
    ]
    if any(_is_link_or_reparse(path) for path in paths):
        raise ValueError("Release outputs must not be links or reparse points")
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_zip(paths[0], install_files)
    _write_zip(paths[1], files)
    paths[2].write_text(prompt, encoding="utf-8", newline="\n")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        for path in build_release(args.root, args.output_dir or args.root / "dist"):
            print(path)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Release build failed: {error}\n")


if __name__ == "__main__":
    main()
