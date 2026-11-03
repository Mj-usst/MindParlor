"""Safe text, Markdown links and reproducible ZIP IO for MindParlor."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import zipfile


INLINE_LINK = re.compile(r"(!?\[[^\]\n]*\]\()([^\s)]+)([^)\n]*\))")


REFERENCE_LINK = re.compile(r"^(\s{0,3}\[[^\]\n]+\]:\s*)(\S+)(.*)$", re.MULTILINE)


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


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    if "\0" in text:
        raise ValueError(f"Binary content is not publishable: {path}")
    return text


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


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(entries.items()):
            # Stable metadata keeps identical sources reproducible.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
