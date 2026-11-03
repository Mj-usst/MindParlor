import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
IDS = ["musk", "jobs", "buffett", "naval", "feynman", "mao", "trump", "warsh", "altman", "saylor"]


class MindParlorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.output = Path(self.temp.name) / "release"
        self.skill = self.root / "skills/mindparlor"
        self.write("LICENSE", "Project MIT license\n")
        self.write("skills/mindparlor/SKILL.md", "---\nname: mindparlor\ndescription: Use when choosing a conversation partner.\n---\n# Router\nRead [conversation](references/conversation.md).\n")
        self.write("skills/mindparlor/catalog.json", json.dumps({"schema_version": 1, "version": "0.1.0", "as_of": "2026-11-03", "people": IDS}))
        self.write("skills/mindparlor/references/conversation.md", "# Shared\nShared conversation contract.\n")
        self.write("skills/mindparlor/agents/openai.yaml", 'interface:\n  display_name: "MindParlor"\n')
        for index, person in enumerate(IDS):
            prefix = f"skills/mindparlor/personas/{person}"
            self.write(prefix + "/manifest.json", json.dumps({
                "id": person, "name_zh": f"人物{index}", "name_en": f"Person {index}",
                "aliases": [f"Alias {index}"], "version": "0.1.0", "as_of": "2026-11-03",
                "reconstruction": "text-grounded" if person == "mao" else "public-expression",
                "status": "preview", "source_ids": ["S01"],
            }))
            self.write(prefix + "/sources.md", "# Sources\n## S01 — Original\nhttps://example.org/original\n")
            for lang in ("zh", "en"):
                self.write(prefix + f"/persona.{lang}.md", f"# Persona\nUNIQUE_{person}_{lang}\nRead [evidence](sources.md). [Section](#voice)\n")
                self.write(prefix + f"/dialogues.{lang}.md", f"# Examples\nEXAMPLE_{person}_{lang}\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def load(self):
        self.assertTrue((ROOT / "scripts/mindparlor.py").is_file(), "MindParlor runtime is not implemented")
        return importlib.import_module("scripts.mindparlor")

    def change_manifest(self, person, **changes):
        path = self.skill / "personas" / person / "manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_alias_resolution_normalizes_case_spaces_and_fullwidth(self):
        module = self.load()
        people = module.load_catalog(self.root)
        self.assertEqual(module.resolve_person(people, "  ＡＬＩＡＳ　０ ")["id"], "musk")
        self.assertEqual(module.resolve_person(people, "MUSK")["id"], "musk")
        with self.assertRaises(ValueError):
            module.resolve_person(people, "somebody else")

    def test_duplicate_alias_is_rejected_before_any_output(self):
        self.change_manifest("jobs", aliases=["alias 0"])
        with self.assertRaisesRegex(ValueError, "[Aa]lias"):
            self.load().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_export_is_self_contained_and_only_one_person_language(self):
        prompt = self.load().compile_prompt(self.root, "musk", "en")
        self.assertIn("UNIQUE_musk_en", prompt)
        self.assertIn("EXAMPLE_musk_en", prompt)
        self.assertIn("Shared conversation contract.", prompt)
        self.assertIn("](#sources)", prompt)
        self.assertNotIn("](sources.md)", prompt)
        self.assertNotIn("UNIQUE_musk_zh", prompt)
        self.assertNotIn("UNIQUE_jobs", prompt)
        self.assertIn("https://example.org/original", prompt)

    def test_complete_archive_has_ten_people_and_twenty_prompts(self):
        paths = self.load().build_release(self.root, self.output)
        self.assertTrue(all(path.is_file() for path in paths))
        with zipfile.ZipFile(self.output / "mindparlor-v0.1.0.zip") as archive:
            names = archive.namelist()
            self.assertTrue(all(name.startswith("mindparlor/") for name in names))
            self.assertIn("mindparlor/LICENSE", names)
            for person in IDS:
                self.assertIn(f"mindparlor/personas/{person}/manifest.json", names)
        with zipfile.ZipFile(self.output / "mindparlor-prompts-v0.1.0.zip") as archive:
            prompts = [name for name in archive.namelist() if name.endswith(".md")]
            self.assertEqual(len(prompts), 20)
            self.assertIn("UNIQUE_mao_zh", archive.read("zh/mao.md").decode("utf-8"))
        manifest = json.loads((self.output / "release-manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), digest)

    def test_archives_reproduce_and_unapproved_files_are_excluded(self):
        self.write("skills/mindparlor/private/secret.md", "SECRET_SHOULD_NOT_SHIP")
        self.write("skills/mindparlor/personas/musk/.env", "SECRET_CREDENTIAL")
        module = self.load()
        module.build_release(self.root, self.output)
        first = (self.output / "mindparlor-v0.1.0.zip").read_bytes()
        module.build_release(self.root, self.output)
        self.assertEqual(first, (self.output / "mindparlor-v0.1.0.zip").read_bytes())
        with zipfile.ZipFile(self.output / "mindparlor-v0.1.0.zip") as archive:
            self.assertFalse(any("private" in name or ".env" in name for name in archive.namelist()))

    def test_missing_other_language_blocks_all_outputs(self):
        (self.skill / "personas/saylor/persona.en.md").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_unresolved_local_link_blocks_output(self):
        self.write("skills/mindparlor/personas/musk/persona.en.md", "Read [missing](missing.md).\n")
        with self.assertRaises((FileNotFoundError, ValueError)):
            self.load().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_declared_source_blocks_output(self):
        self.change_manifest("mao", source_ids=["S01", "S99"])
        with self.assertRaisesRegex(ValueError, "S99"):
            self.load().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_undeclared_source_ids_are_detected_next_to_chinese_and_at_full_length(self):
        for text, source_id in [("依据MU99支持此特征。", "MU99"),
                                ("See [ABCD123] for this trait.", "ABCD123")]:
            with self.subTest(source_id=source_id):
                self.write("skills/mindparlor/personas/musk/persona.zh.md", text)
                with self.assertRaisesRegex(ValueError, source_id):
                    self.load().validate(self.root)

    def test_person_id_path_traversal_and_invalid_language_are_rejected(self):
        module = self.load()
        with self.assertRaises(ValueError):
            module.compile_prompt(self.root, "../private", "en")
        with self.assertRaises(ValueError):
            module.compile_prompt(self.root, "musk", "../../en")

    def test_output_target_is_validated_before_any_file_is_written(self):
        target = self.output / "prompts/en/saylor.md"
        target.mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.load().build_release(self.root, self.output)
        self.assertEqual([p for p in self.output.rglob("*") if p.is_file()], [])

    def test_catalog_requires_exact_roster_and_unique_json_keys(self):
        self.write("skills/mindparlor/catalog.json", '{"schema_version":1,"version":"0.1.0","version":"9.9.9","people":[]}')
        with self.assertRaises(ValueError):
            self.load().load_catalog(self.root)

    def test_cli_resolves_an_alias_and_unknown_person_exits_without_traceback(self):
        self.load()
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        script = str(ROOT / "scripts/mindparlor.py")
        result = subprocess.run([sys.executable, script, "--root", str(self.root), "prompt", "Alias 5", "--lang", "en"], capture_output=True, encoding="utf-8", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("UNIQUE_mao_en", result.stdout)
        result = subprocess.run([sys.executable, script, "--root", str(self.root), "prompt", "unknown"], capture_output=True, encoding="utf-8", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_chinese_output_is_utf8_without_python_encoding_flags(self):
        self.load()
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
        result = subprocess.run([sys.executable, str(ROOT / "scripts/mindparlor.py"),
                                 "--root", str(self.root), "list"], capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("人物0".encode("utf-8"), result.stdout)

    def test_prompt_output_cannot_overwrite_inputs_even_with_dotdot(self):
        self.load()
        scratch = self.root / "scratch"
        scratch.mkdir()
        targets = [self.root / "LICENSE", self.skill / "personas/musk/manifest.json",
                   scratch / ".." / "LICENSE"]
        for target in targets:
            with self.subTest(target=target):
                original = target.read_bytes()
                result = subprocess.run([sys.executable, str(ROOT / "scripts/mindparlor.py"),
                                         "--root", str(self.root), "prompt", "musk", "--lang", "en",
                                         "--output", str(target)], capture_output=True)
                try:
                    self.assertNotEqual(result.returncode, 0, "Export must refuse to overwrite its own input")
                    self.assertEqual(target.read_bytes(), original)
                finally:
                    target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
