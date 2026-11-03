#!/usr/bin/env python3
"""Validate, list and distribute MindParlor without a model API or dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata

try:
    from . import build_release as legacy
except ImportError:  # Direct `python scripts/mindparlor.py` execution.
    import build_release as legacy


IDS = ("musk", "jobs", "buffett", "naval", "feynman", "mao", "trump", "warsh", "altman", "saylor")
SKILL = PurePosixPath("skills/mindparlor")
SHARED = ("SKILL.md", "catalog.json", "references/conversation.md", "agents/openai.yaml")
PERSON_FILES = ("manifest.json", "persona.zh.md", "persona.en.md", "sources.md", "dialogues.zh.md", "dialogues.en.md")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
SOURCE_ID_GRAMMAR = r"[A-Z]{1,4}\d{2,3}"
SOURCE_REFERENCE = re.compile(r"(?<![A-Za-z0-9_])(" + SOURCE_ID_GRAMMAR + r")(?![A-Za-z0-9_])")


def _read(root: Path, relative: str | PurePosixPath) -> str:
    relative = PurePosixPath(relative)
    if relative.is_absolute() or any(part in ("..", ".") or "\\" in part for part in relative.parts):
        raise ValueError(f"Unsafe input path: {relative}")
    path = root / str(relative)
    if legacy._path_traverses_link_or_reparse(path):
        raise ValueError(f"Input must not traverse links or reparse points: {relative}")
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {relative}")
    return legacy._read_text(path)


def _json(text: str):
    return json.loads(text, object_pairs_hook=legacy._json_object)


def _alias(value: str) -> str:
    return re.sub(r"[\s_-]+", "", unicodedata.normalize("NFKC", value).casefold())


def _config(root: Path) -> dict:
    config = _json(_read(root, SKILL / "catalog.json"))
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("Unsupported MindParlor catalog schema")
    if not isinstance(config.get("version"), str) or not VERSION.fullmatch(config["version"]):
        raise ValueError("Catalog version must be semantic x.y.z")
    if config.get("people") != list(IDS):
        raise ValueError("Catalog must contain the ten canonical people in release order")
    return config


def load_catalog(root: Path) -> list[dict]:
    root = Path(root).absolute()
    config = _config(root)
    people, aliases = [], {}
    for person_id in config["people"]:
        person = _json(_read(root, SKILL / "personas" / person_id / "manifest.json"))
        if not isinstance(person, dict) or person.get("id") != person_id:
            raise ValueError(f"Manifest ID does not match folder: {person_id}")
        for key in ("name_zh", "name_en", "version", "as_of", "status"):
            if not isinstance(person.get(key), str) or not person[key].strip():
                raise ValueError(f"Missing manifest {key}: {person_id}")
        if not VERSION.fullmatch(person["version"]):
            raise ValueError(f"Invalid persona version: {person_id}")
        if person.get("reconstruction") not in ("public-expression", "text-grounded"):
            raise ValueError(f"Missing reconstruction type: {person_id}")
        for key in ("aliases", "source_ids"):
            if not isinstance(person.get(key), list) or any(not isinstance(v, str) or not v.strip() for v in person[key]):
                raise ValueError(f"Invalid manifest {key}: {person_id}")
        if not person["source_ids"] or len(set(person["source_ids"])) != len(person["source_ids"]):
            raise ValueError(f"Source IDs must be nonempty and unique: {person_id}")
        for name in (person_id, person["name_zh"], person["name_en"], *person["aliases"]):
            normalized = _alias(name)
            if not normalized:
                raise ValueError(f"Empty alias: {person_id}")
            if normalized in aliases and aliases[normalized] != person_id:
                raise ValueError(f"Alias collision: {name} ({aliases[normalized]}, {person_id})")
            aliases[normalized] = person_id
        people.append(person)
    return people


def resolve_person(catalog: list[dict], query: str) -> dict:
    normalized = _alias(query)
    for person in catalog:
        if normalized in {_alias(name) for name in (person["id"], person["name_zh"], person["name_en"], *person["aliases"])}:
            return person
    raise ValueError(f"Unknown person: {query}. Run 'list' to see the ten supported people.")


def validate(root: Path) -> tuple[dict, list[dict], dict[str, bytes]]:
    root = Path(root).absolute()
    config, people = _config(root), load_catalog(root)
    paths = [PurePosixPath("LICENSE"), *(SKILL / name for name in SHARED)]
    paths += [SKILL / "personas" / person["id"] / name for person in people for name in PERSON_FILES]
    files = {str(path): _read(root, path).encode("utf-8") for path in paths}
    for name, raw in files.items():
        if not name.endswith(".md"):
            continue
        for target in legacy._link_targets(raw.decode("utf-8")):
            local = legacy._local_target(PurePosixPath(name), target)
            if local is not None and str(local) not in files:
                raise FileNotFoundError(f"Missing or unapproved reference in {name}: {target}")
    for person in people:
        prefix = str(SKILL / "personas" / person["id"])
        sources = files[prefix + "/sources.md"].decode("utf-8")
        headings = set(re.findall(r"^#{1,6}\s+(" + SOURCE_ID_GRAMMAR + r")(?=$|[^A-Za-z0-9_])", sources, re.MULTILINE))
        for source_id in person["source_ids"]:
            if source_id not in headings:
                raise ValueError(f"Missing declared source {source_id}: {person['id']}")
        for filename in PERSON_FILES:
            if not filename.startswith(("persona.", "dialogues.")):
                continue
            references = set(SOURCE_REFERENCE.findall(files[prefix + "/" + filename].decode("utf-8")))
            missing = references - set(person["source_ids"])
            if missing:
                raise ValueError(f"Unregistered source IDs in {person['id']}/{filename}: {sorted(missing)}")
    return config, people, files


def _compile(person: dict, lang: str, files: dict[str, bytes]) -> str:
    if lang not in ("zh", "en"):
        raise ValueError("Language must be zh or en")
    base = SKILL / "personas" / person["id"]
    selected = [(SKILL / "references/conversation.md", "conversation"),
                (base / f"persona.{lang}.md", "persona"),
                (base / "sources.md", "sources"),
                (base / f"dialogues.{lang}.md", "dialogues")]
    anchors = {str(path): anchor for path, anchor in selected}
    if lang == "zh":
        intro = f"# MindParlor — {person['name_zh']}\n\n当前人物：{person['name_zh']}；默认用中文聊天。以下是完整独立指令，用户无需提供本地文件。直接进入所选人物的自然对话；首次简短说明非官方 AI 模拟。原始来源和原创对话示范见下文。\n"
    else:
        intro = f"# MindParlor — {person['name_en']}\n\nActive character: {person['name_en']}; converse in English by default. These instructions are self-contained; no local files are needed. Begin a natural conversation as the selected character, with one brief initial notice that this is an unofficial AI simulation. Sources and original example conversations follow.\n"
    if lang == "zh":
        intro += f"\n这份文件只包含{person['name_zh']}的人物包。用户要求换人时，简短说明需要项目确实提供的另一份完整指令，或在完整版 skill 的支持名单中选择；不要承诺未收录人物可用。不要凭一般印象临时扮演另一人，也不声称已经读取未提供的资料。下文换人约定只在所需人物包确实可用时适用。用户只是提到别人，不自动改变当前人物。\n"
    else:
        intro += f"\nThis file bundles only {person['name_en']}. If the user asks to switch people, briefly explain that they need another complete prompt the project actually provides, or a person on the full skill's supported roster; do not promise an unlisted character is available. Do not improvise another persona from general knowledge or claim to have loaded missing material. The switching contract below applies only when the required persona package is actually available. Merely mentioning someone else does not switch the active character.\n"
    sections = [intro]
    for path, anchor in selected:
        content = files[str(path)].decode("utf-8")

        def rewrite(target):
            local = legacy._local_target(path, target)
            if local is None:
                return target
            if str(local) not in anchors:
                raise ValueError(f"Cannot inline reference in selected-person prompt: {path}: {target}")
            return "#" + anchors[str(local)]

        content = legacy.INLINE_LINK.sub(lambda m: m.group(1) + rewrite(m.group(2)) + m.group(3), content)
        content = legacy.REFERENCE_LINK.sub(lambda m: m.group(1) + rewrite(m.group(2)) + m.group(3), content)
        sections.append(f'<a id="{anchor}"></a>\n\n{content.strip()}\n')
    return "\n\n---\n\n".join(sections).rstrip() + "\n"


def compile_prompt(root: Path, person_id: str, lang: str) -> str:
    _, people, files = validate(root)
    return _compile(resolve_person(people, person_id), lang, files)


def _check_output(path: Path) -> None:
    if legacy._path_traverses_link_or_reparse(path):
        raise ValueError(f"Output must not traverse links or reparse points: {path}")
    for parent in path.parents:
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Output ancestor is not a directory: {parent}")
    if path.exists() and not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"Existing output must be a regular file: {path}")


def _check_input_overlap(root: Path, target: Path) -> None:
    # Normalize '..' after checking for links/reparse points. Protect both data
    # inputs and the running exporter, even when --root is a separate fixture.
    root, target = Path(root).resolve(), Path(target).resolve()
    protected = {root / "LICENSE", Path(__file__).resolve(), Path(legacy.__file__).resolve()}
    if target.is_relative_to(root / "skills") or target in protected:
        raise ValueError(f"Output must not overwrite project inputs: {target}")


def build_release(root: Path, output_dir: Path) -> list[Path]:
    root, output_dir = Path(root).absolute(), Path(output_dir).absolute()
    config, people, files = validate(root)
    version = config["version"]
    install = {"mindparlor/" + name[len(str(SKILL)) + 1:]: raw for name, raw in files.items() if name.startswith(str(SKILL) + "/")}
    install["mindparlor/LICENSE"] = files["LICENSE"]
    prompts = {f"{lang}/{person['id']}.md": _compile(person, lang, files).encode("utf-8") for person in people for lang in ("zh", "en")}
    archive_paths = [output_dir / f"mindparlor-v{version}.zip", output_dir / f"mindparlor-prompts-v{version}.zip"]
    prompt_files = {output_dir / "prompts" / name: raw for name, raw in prompts.items()}
    manifest_path = output_dir / "release-manifest.json"
    targets = [*archive_paths, *prompt_files, manifest_path]
    for target in targets:
        _check_output(target)
        _check_input_overlap(root, target)
    output_dir.mkdir(parents=True, exist_ok=True)
    legacy._write_zip(archive_paths[0], install)
    legacy._write_zip(archive_paths[1], prompts)
    for target, content in prompt_files.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    manifest = {"project": "mindparlor", "version": version, "as_of": config.get("as_of"),
                "status": "preview", "people": list(IDS),
                "sha256": {path.relative_to(output_dir).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in targets if path != manifest_path}}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return targets


def main():
    # Use a stable interchange encoding even when Windows pipes default to GBK.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List the ten people")
    listing.add_argument("--lang", choices=("zh", "en"), default="zh")
    prompt = commands.add_parser("prompt", help="Print a self-contained selected-person prompt")
    prompt.add_argument("person", help="Canonical ID, English/Chinese name, or an alias")
    prompt.add_argument("--lang", choices=("zh", "en"), default="zh")
    prompt.add_argument("--output", type=Path)
    release = commands.add_parser("build", help="Build installation and prompt archives")
    release.add_argument("--output-dir", type=Path)
    commands.add_parser("check", help="Validate the catalog, files, references and all twenty prompts")
    args = parser.parse_args()
    try:
        if args.command == "list":
            for index, person in enumerate(load_catalog(args.root), 1):
                print(f"{index:2}. {person['name_' + args.lang]} ({person['id']})")
        elif args.command == "prompt":
            result = compile_prompt(args.root, args.person, args.lang)
            if args.output:
                _check_output(args.output.absolute())
                _check_input_overlap(args.root, args.output)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(result, encoding="utf-8", newline="\n")
            else:
                print(result, end="")
        elif args.command == "build":
            for path in build_release(args.root, args.output_dir or args.root / "dist/mindparlor"):
                print(path)
        else:
            config, people, files = validate(args.root)
            for person in people:
                for lang in ("zh", "en"):
                    _compile(person, lang, files)
            print(f"MindParlor {config['version']}: {len(people)} people, 20 complete prompts; content status: preview.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"MindParlor: {error}\n")


if __name__ == "__main__":
    main()
