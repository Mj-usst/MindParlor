#!/usr/bin/env python3
"""Build public releases using Python 3.10+ and the standard library only."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import zipfile


ROOT_FILES = {"README.md", "README.en.md", "LICENSE", "VERSION", ".gitignore", "release.json"}
PUBLIC_DIRECTORIES = {"skills", "docs", "examples", "scripts", "tests"}
TEXT_SUFFIXES = {".md", ".txt", ".rst", ".yaml", ".yml", ".py", ".toml", ".json", ".csv", ".tsv"}
EXCLUDED_PARTS = {
    "private", "decisions", ".git", ".agents", ".env", "__pycache__", "dist",
    ".cache", "cache", "caches", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".venv", "venv", "node_modules", "build",
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


def _safe_basename(value: object, label: str) -> str:
    """Accept portable, visible basenames, including on Windows."""
    reserved = {"CON", "PRN", "AUX", "NUL"} | {
        prefix + str(number) for prefix in ("COM", "LPT") for number in range(1, 10)
    }
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value)
        or value.endswith(".")
        or value.split(".", 1)[0].upper() in reserved
    ):
        raise ValueError(f"{label} must be a safe, portable basename")
    return value


def _relative_markdown(value: object, label: str) -> str:
    if not isinstance(value, str) or "\\" in value:
        raise ValueError(f"{label} must be a relative Markdown path within the Skill")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or not path.parts or path.suffix.lower() != ".md":
        raise ValueError(f"{label} must be a relative Markdown path within the Skill")
    for part in path.parts:
        _safe_basename(part, label)
    if _is_excluded(Path(*path.parts)):
        raise ValueError(f"{label} must refer to a public Skill file")
    return value


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate release configuration key: {key}")
        result[key] = value
    return result


def _release_config(root: Path) -> tuple[str, str, dict[str, dict[str, str]]]:
    path = root / "release.json"
    if _is_link_or_reparse(path):
        raise ValueError("release.json must not be a link or reparse point")
    if path.exists():
        if not _is_public_file(root, path):
            raise ValueError("release.json must be a public file")
        config = json.loads(_read_text(path), object_pairs_hook=_json_object)
    else:
        # Repositories created before edition support retain the original three outputs.
        config = {
            "project_slug": "ai-musk-skill",
            "default_edition": "zh-CN",
            "editions": {"zh-CN": {
                "skill_name": "musk-decision",
                "prompt_file": "chatgpt-instructions.md",
                "prompt_title": "马斯克式决策顾问：ChatGPT 完整指令",
            }},
        }
    if not isinstance(config, dict) or set(config) != {"project_slug", "default_edition", "editions"}:
        raise ValueError("release.json must contain project_slug, default_edition and editions")
    project_slug = _safe_basename(config["project_slug"], "project_slug")
    default = _safe_basename(config["default_edition"], "default_edition")
    entries = config["editions"]
    if not isinstance(entries, dict) or not entries or default not in entries:
        raise ValueError("editions must be nonempty and contain default_edition")
    editions: dict[str, dict[str, str]] = {}
    names = {project_slug.casefold()}
    prompts: set[str] = set()
    required_keys = {"skill_name", "prompt_file", "prompt_title"}
    for key, entry in entries.items():
        _safe_basename(key, "edition")
        if (
            not isinstance(entry, dict)
            or not required_keys <= set(entry)
            or set(entry) - required_keys - {"framework_file", "worksheet_file"}
        ):
            raise ValueError(f"Invalid release metadata for edition: {key}")
        skill_name = _safe_basename(entry["skill_name"], "skill_name")
        prompt_file = _safe_basename(entry["prompt_file"], "prompt_file")
        if not prompt_file.lower().endswith(".md"):
            raise ValueError("prompt_file must use the .md extension")
        title = entry["prompt_title"]
        if not isinstance(title, str) or not title.strip() or any(c in title for c in "\0\r\n"):
            raise ValueError("prompt_title must be a nonempty single line")
        if skill_name.casefold() in names or prompt_file.casefold() in prompts:
            raise ValueError("Edition output filenames must be distinct, ignoring case")
        names.add(skill_name.casefold())
        prompts.add(prompt_file.casefold())
        framework = _relative_markdown(
            entry.get("framework_file", "references/decision-framework.md"), "framework_file",
        )
        worksheet = _relative_markdown(
            entry.get("worksheet_file", "assets/current-state.md"), "worksheet_file",
        )
        if len({"skill.md", framework.casefold(), "references/sources.md", worksheet.casefold()}) != 4:
            raise ValueError("Edition inline files must be distinct")
        editions[key] = {
            "skill_name": skill_name, "prompt_file": prompt_file, "prompt_title": title,
            "framework_file": framework, "worksheet_file": worksheet,
        }
    return project_slug, default, editions


def _inline_files(edition: dict[str, str]) -> dict[str, str]:
    return {
        "SKILL.md": "skill-instructions",
        edition["framework_file"]: "decision-framework",
        "references/sources.md": "sources",
        edition["worksheet_file"]: "current-state",
    }


def _standalone_prompt(files: dict[str, bytes], edition: dict[str, str]) -> str:
    skill = PurePosixPath("skills") / edition["skill_name"]
    inline_files = _inline_files(edition)
    anchors = {str(skill / name): anchor for name, anchor in inline_files.items()}
    sections = ["# " + edition["prompt_title"] + "\n"]
    for name, anchor in inline_files.items():
        source = skill / name
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


def build_release(
    root: Path, output_dir: Path, edition: str | None = None, *, all_editions: bool = False,
) -> list[Path]:
    """Validate inputs, then write selected editions and one shared source ZIP.

    Without release.json, the original Chinese edition and filenames are used.
    All configured file references are validated before writing. all_editions builds
    every edition and deduplicates the source ZIP.
    """
    root = Path(root).absolute()
    output_dir = Path(output_dir).absolute()
    if _path_traverses_link_or_reparse(root) or not root.is_dir():
        raise ValueError("Repository root must not traverse links or reparse points")
    if _path_traverses_link_or_reparse(output_dir):
        raise ValueError("Output directory must not traverse links or reparse points")

    project_slug, default, editions = _release_config(root)
    if all_editions and edition is not None:
        raise ValueError("Choose edition or all_editions, not both")
    if edition is not None and edition not in editions:
        raise ValueError(f"Unknown edition: {edition}")
    selected = list(editions.values()) if all_editions else [editions[edition or default]]
    required = {"VERSION", "LICENSE", "README.md"}
    if (root / "release.json").exists():
        required.add("release.json")
    for entry in editions.values():
        skill = PurePosixPath("skills") / entry["skill_name"]
        required.update(str(skill / name) for name in _inline_files(entry))
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
    # Validate all configured Skills, including those included only in the source ZIP.
    skill_prefixes = tuple("skills/" + entry["skill_name"] + "/" for entry in editions.values())
    for name, content in files.items():
        if not name.startswith(skill_prefixes) or not name.endswith(".md"):
            continue
        for target in _link_targets(content.decode("utf-8")):
            local = _local_target(PurePosixPath(name), target)
            if local is not None and str(local) not in files:
                raise FileNotFoundError(f"Missing or excluded reference in {name}: {target}")
    compiled_prompts = {
        entry["skill_name"]: _standalone_prompt(files, entry) for entry in editions.values()
    }
    # Prepare every prompt and archive before creating or changing any output.
    source_path = output_dir / f"{project_slug}-v{version}.zip"
    archives: dict[Path, dict[str, bytes]] = {}
    prompts: dict[Path, str] = {}
    paths: list[Path] = []
    for entry in selected:
        skill_name = entry["skill_name"]
        prefix = "skills/" + skill_name + "/"
        prompt = compiled_prompts[skill_name]
        install_files = {
            skill_name + "/" + name[len(prefix):]: content
            for name, content in files.items() if name.startswith(prefix)
        }
        install_files[skill_name + "/LICENSE"] = files["LICENSE"]
        install_path = output_dir / f"{skill_name}-v{version}.zip"
        prompt_path = output_dir / entry["prompt_file"]
        archives[install_path] = install_files
        archives[source_path] = files
        prompts[prompt_path] = prompt
        for path in (install_path, source_path, prompt_path):
            if path not in paths:
                paths.append(path)
    if any(_is_link_or_reparse(path) for path in paths):
        raise ValueError("Release outputs must not be links or reparse points")
    for path in paths:
        try:
            entry = path.lstat()
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(entry.st_mode):
            raise ValueError(f"Existing release output must be a regular file: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, entries in archives.items():
        _write_zip(path, entries)
    for path, prompt in prompts.items():
        path.write_text(prompt, encoding="utf-8", newline="\n")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--edition", help="Edition key from release.json (defaults to default_edition)")
    selection.add_argument("--all", dest="all_editions", action="store_true", help="Build every configured edition")
    args = parser.parse_args()
    try:
        for path in build_release(
            args.root, args.output_dir or args.root / "dist", args.edition, all_editions=args.all_editions,
        ):
            print(path)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Release build failed: {error}\n")


if __name__ == "__main__":
    main()
