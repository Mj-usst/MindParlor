import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.output = self.base / "dist"
        for name, content in {
            "VERSION": "0.1.0\n",
            "LICENSE": "Original project license\n",
            "README.md": "# Public skill\n",
            "skills/musk-decision/SKILL.md": (
                "---\nname: musk-decision\ndescription: Use when choosing a direction.\n---\n"
                "# Decision\nRead [framework](references/decision-framework.md), "
                "[sources](references/sources.md), [worksheet](assets/current-state.md).\n"
            ),
            "skills/musk-decision/agents/openai.yaml": 'interface:\n  display_name: "顾问"\n',
            "skills/musk-decision/references/decision-framework.md": "# Framework\nDecision method.\n",
            "skills/musk-decision/references/sources.md": "# Sources\n[M01](https://www.tesla.com/secret-master-plan)\n",
            "skills/musk-decision/assets/current-state.md": "# Input\nUser goals.\n",
            ".git/config": "SECRET_GIT_CONFIG",
            "private/profile.md": "SECRET_PERSONAL_PROFILE",
            "decisions/report.md": "SECRET_DECISION",
            "docs/private/notes.md": "NESTED_PRIVATE_NOTE",
            "docs/__pycache__/cache.pyc": "PRIVATE_CACHE",
            ".env": "SECRET_TOKEN",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def load_builder(self):
        path = ROOT / "scripts/build_release.py"
        self.assertTrue(path.is_file(), "Release builder has not been implemented")
        spec = importlib.util.spec_from_file_location("release_builder", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def make_junction(self, link, target):
        """Use real Windows junctions; remove only the junction at cleanup."""
        if os.name != "nt":
            self.skipTest("Windows junction creation requires Windows")
        link.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            detail = result.stderr.decode("mbcs" if os.name == "nt" else "utf-8", errors="replace").strip()
            self.skipTest(f"Windows junction creation unavailable: {detail}")
        self.addCleanup(os.rmdir, link)
        self.assertFalse(link.is_symlink(), "Fixture must exercise junctions, not symlinks")
        self.assertTrue(link.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

    def configure_editions(self):
        config = {
            "project_slug": "ai-musk-skill",
            "default_edition": "zh-CN",
            "editions": {
                "zh-CN": {
                    "skill_name": "musk-decision",
                    "prompt_file": "chatgpt-instructions.md",
                    "prompt_title": "马斯克式决策顾问：ChatGPT完整指令",
                },
                "en": {
                    "skill_name": "musk-decision-en",
                    "prompt_file": "chatgpt-instructions.en.md",
                    "prompt_title": "Musk-inspired decision advisor: Complete ChatGPT instructions",
                },
            },
        }
        self.write_config(config)
        (self.root / "README.en.md").write_text("# English installation\n", encoding="utf-8")
        for path in (self.root / "skills/musk-decision").rglob("*"):
            if path.is_file():
                destination = self.root / "skills/musk-decision-en" / path.relative_to(self.root / "skills/musk-decision")
                destination.parent.mkdir(parents=True, exist_ok=True)
                text = path.read_text(encoding="utf-8").replace("name: musk-decision", "name: musk-decision-en")
                if path.suffix == ".yaml":
                    text = 'interface:\n  display_name: "Advisor"\n'
                destination.write_text(text, encoding="utf-8")
        (self.root / "skills/musk-decision/references/decision-framework.md").write_text(
            "# 中文方法\n中文决策方法。\n", encoding="utf-8"
        )
        return config

    def write_config(self, config):
        (self.root / "release.json").write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

    def test_english_edition_installs_in_its_own_folder_and_has_english_only_prompt(self):
        self.configure_editions()
        paths = self.load_builder().build_release(self.root, self.output, edition="en")
        self.assertEqual({p.name for p in paths}, {
            "musk-decision-en-v0.1.0.zip", "ai-musk-skill-v0.1.0.zip", "chatgpt-instructions.en.md",
        })
        with zipfile.ZipFile(self.output / "musk-decision-en-v0.1.0.zip") as archive:
            self.assertTrue(all(name.startswith("musk-decision-en/") for name in archive.namelist()))
            self.assertIn("musk-decision-en/references/sources.md", archive.namelist())
            self.assertIn("musk-decision-en/assets/current-state.md", archive.namelist())
            self.assertIn("musk-decision-en/LICENSE", archive.namelist())
            self.assertIn(b"name: musk-decision-en", archive.read("musk-decision-en/SKILL.md"))
        prompt = (self.output / "chatgpt-instructions.en.md").read_text(encoding="utf-8")
        self.assertTrue(prompt.startswith("# Musk-inspired decision advisor: Complete ChatGPT instructions\n"))
        self.assertNotRegex(prompt, r"[\u3400-\u9fff]")
        for text in ["Decision method.", "User goals.", "https://www.tesla.com/secret-master-plan"]:
            self.assertIn(text, prompt)
        self.assertIn("](#decision-framework)", prompt)
        self.assertNotIn("](references/", prompt)
        self.assertNotIn("](assets/", prompt)
        self.assertNotIn("name: musk-decision-en", prompt)

    def test_configured_default_remains_chinese_and_source_includes_both_editions(self):
        self.configure_editions()
        paths = self.load_builder().build_release(self.root, self.output)
        self.assertEqual({p.name for p in paths}, {
            "musk-decision-v0.1.0.zip", "ai-musk-skill-v0.1.0.zip", "chatgpt-instructions.md",
        })
        prompt = (self.output / "chatgpt-instructions.md").read_text(encoding="utf-8")
        self.assertTrue(prompt.startswith("# 马斯克式决策顾问：ChatGPT完整指令\n"))
        self.assertIn("中文决策方法。", prompt)
        with zipfile.ZipFile(self.output / "ai-musk-skill-v0.1.0.zip") as archive:
            self.assertEqual(archive.read("README.en.md"), b"# English installation\n")
            self.assertIn("release.json", archive.namelist())
            self.assertIn("skills/musk-decision-en/SKILL.md", archive.namelist())

    def test_build_all_returns_five_distinct_artifacts_without_overwriting_editions(self):
        self.configure_editions()
        paths = self.load_builder().build_release(self.root, self.output, all_editions=True)
        self.assertEqual({p.name for p in paths}, {
            "musk-decision-v0.1.0.zip", "musk-decision-en-v0.1.0.zip", "ai-musk-skill-v0.1.0.zip",
            "chatgpt-instructions.md", "chatgpt-instructions.en.md",
        })
        self.assertEqual(len(paths), 5)
        self.assertIn("中文决策方法。", (self.output / "chatgpt-instructions.md").read_text(encoding="utf-8"))
        self.assertIn("Decision method.", (self.output / "chatgpt-instructions.en.md").read_text(encoding="utf-8"))

    def test_cli_selects_english_and_all_editions(self):
        self.configure_editions()
        for flag in [("--edition", "en"), ("--all",)]:
            output = self.base / ("cli-en" if "en" in flag else "cli-all")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_release.py"), "--root", str(self.root),
                 "--output-dir", str(output), *flag], capture_output=True, text=True,
            )
            with self.subTest(flag=flag):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((output / "musk-decision-en-v0.1.0.zip").is_file())
                self.assertEqual(len(list(output.iterdir())), 3 if "en" in flag else 5)

    def test_custom_project_framework_and_worksheet_are_inlined(self):
        config = self.configure_editions()
        config["project_slug"] = "mao-decision-skill"
        config["default_edition"] = "zh-CN"
        config["editions"] = {"zh-CN": {
            "skill_name": "mao-decision", "prompt_file": "mao-chatgpt-instructions.md",
            "prompt_title": "毛选决策顾问", "framework_file": "references/methods.md",
            "worksheet_file": "assets/situation.md",
        }}
        self.write_config(config)
        for name, content in {
            "SKILL.md": "# Mao advisor\n[Methods](references/methods.md), [sources](references/sources.md), [input](assets/situation.md).\n",
            "references/methods.md": "# Methods\nInvestigate the situation.\n",
            "references/sources.md": "# Sources\nPublic references.\n",
            "assets/situation.md": "# Situation\nRecord constraints.\n",
        }.items():
            path = self.root / "skills/mao-decision" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        paths = self.load_builder().build_release(self.root, self.output)
        self.assertEqual({p.name for p in paths}, {
            "mao-decision-v0.1.0.zip", "mao-decision-skill-v0.1.0.zip", "mao-chatgpt-instructions.md",
        })
        prompt = (self.output / "mao-chatgpt-instructions.md").read_text(encoding="utf-8")
        self.assertIn("Investigate the situation.", prompt)
        self.assertIn("Record constraints.", prompt)
        self.assertNotIn("](references/", prompt)

    def test_invalid_configuration_is_rejected_without_creating_output(self):
        config = self.configure_editions()
        cases = [
            ("project_slug", "../private"), ("project_slug", "CON"), ("project_slug", "unsafe."),
            ("default_edition", "missing"), ("editions", {}),
        ]
        for key, value in cases:
            candidate = json.loads(json.dumps(config))
            candidate[key] = value
            self.write_config(candidate)
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.load_builder().build_release(self.root, self.output)
            self.assertFalse(self.output.exists())
        for key, value in [
            ("skill_name", "/tmp/skill"), ("skill_name", ".hidden"), ("skill_name", "C:\\private"),
            ("prompt_file", "../prompt.md"), ("prompt_file", "folder/prompt.md"),
            ("prompt_file", "CHATGPT-INSTRUCTIONS.MD"), ("skill_name", "musk-decision"),
            ("prompt_title", ""), ("framework_file", "../references/sources.md"),
            ("framework_file", "SKILL.md"),
            ("framework_file", "/references/sources.md"), ("framework_file", "references/.tokens.md"),
            ("worksheet_file", "assets\\current-state.md"), ("worksheet_file", "C:/secret.md"),
        ]:
            candidate = json.loads(json.dumps(config))
            candidate["editions"]["en"][key] = value
            self.write_config(candidate)
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.load_builder().build_release(self.root, self.output)
            self.assertFalse(self.output.exists())

    def test_unknown_edition_and_malformed_json_fail_without_output(self):
        self.configure_editions()
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output, edition="fr")
        self.assertFalse(self.output.exists())
        (self.root / "release.json").write_text("{invalid json", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_duplicate_configuration_keys_fail_without_output(self):
        self.configure_editions()
        path = self.root / "release.json"
        config = path.read_text(encoding="utf-8")
        path.write_text(config.replace('"project_slug":', '"project_slug": "other", "project_slug":', 1), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_build_all_validates_every_edition_before_writing_first_output(self):
        self.configure_editions()
        (self.root / "skills/musk-decision-en/references/sources.md").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load_builder().build_release(self.root, self.output, all_editions=True)
        self.assertFalse(self.output.exists())

    def test_unselected_edition_required_files_are_validated_before_output(self):
        self.configure_editions()
        (self.root / "skills/musk-decision-en/references/sources.md").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_unselected_edition_local_links_are_validated_before_output(self):
        self.configure_editions()
        (self.root / "skills/musk-decision-en/references/decision-framework.md").write_text(
            "# Framework\n[Missing reference](missing.md)\n", encoding="utf-8",
        )
        with self.assertRaises(FileNotFoundError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_unselected_edition_standalone_prompt_is_compiled_before_output(self):
        self.configure_editions()
        (self.root / "skills/musk-decision-en/SKILL.md").write_text(
            "---\nname: musk-decision-en\n# Unclosed frontmatter\n", encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_configured_framework_junction_is_rejected_before_output(self):
        config = self.configure_editions()
        external = self.base / "external-framework"
        external.mkdir()
        (external / "methods.md").write_text("FAKE_EXTERNAL_SECRET", encoding="utf-8")
        self.make_junction(self.root / "skills/musk-decision-en/linked", external)
        config["editions"]["en"]["framework_file"] = "linked/methods.md"
        self.write_config(config)
        with self.assertRaises(FileNotFoundError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_unapproved_hidden_paths_are_excluded_but_root_gitignore_is_kept(self):
        (self.root / ".gitignore").write_text("# PUBLIC_ROOT_IGNORE\n", encoding="utf-8")
        for prefix in ["docs", "skills/musk-decision"]:
            for hidden in [".codex", ".ssh", ".aws", ".azure", ".config", ".kube", ".gnupg", ".other"]:
                path = self.root / prefix / hidden / "auth.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"token":"FAKE_CREDENTIAL_DO_NOT_PACKAGE"}', encoding="utf-8")
            for filename in [".tokens.md", ".gitignore"]:
                (self.root / prefix / filename).write_text("FAKE_CREDENTIAL_DO_NOT_PACKAGE", encoding="utf-8")
        self.load_builder().build_release(self.root, self.output)
        for path in self.output.glob("*.zip"):
            with self.subTest(archive=path.name), zipfile.ZipFile(path) as archive:
                self.assertNotIn(b"FAKE_CREDENTIAL_DO_NOT_PACKAGE", b"\n".join(archive.read(n) for n in archive.namelist()))
                for name in archive.namelist():
                    self.assertFalse(any(part.startswith(".") for part in Path(name).parts if name != ".gitignore"))
        with zipfile.ZipFile(self.output / "ai-musk-skill-v0.1.0.zip") as archive:
            self.assertEqual(archive.read(".gitignore"), b"# PUBLIC_ROOT_IGNORE\n")

    def test_nested_input_junction_does_not_publish_external_files(self):
        external = self.base / "external-notes"
        external.mkdir()
        (external / "profile.md").write_text("FAKE_EXTERNAL_PROFILE", encoding="utf-8")
        self.make_junction(self.root / "docs/linked-notes", external)
        self.load_builder().build_release(self.root, self.output)
        with zipfile.ZipFile(self.output / "ai-musk-skill-v0.1.0.zip") as archive:
            self.assertFalse(any("linked-notes" in name for name in archive.namelist()))
            self.assertNotIn(b"FAKE_EXTERNAL_PROFILE", b"\n".join(archive.read(n) for n in archive.namelist()))

    def test_public_directory_junction_does_not_publish_external_files(self):
        external = self.base / "external-examples"
        external.mkdir()
        (external / "profile.md").write_text("FAKE_EXTERNAL_PROFILE", encoding="utf-8")
        self.make_junction(self.root / "examples", external)
        self.load_builder().build_release(self.root, self.output)
        with zipfile.ZipFile(self.output / "ai-musk-skill-v0.1.0.zip") as archive:
            self.assertFalse(any(name.startswith("examples/") for name in archive.namelist()))

    def test_repository_root_junction_is_rejected(self):
        linked_root = self.base / "linked-repo"
        self.make_junction(linked_root, self.root)
        with self.assertRaises(ValueError):
            self.load_builder().build_release(linked_root, self.output)
        self.assertFalse(self.output.exists())

    def test_output_directory_junction_is_rejected_without_external_writes(self):
        external = self.base / "external-output"
        external.mkdir()
        self.make_junction(self.output, external)
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output)
        self.assertEqual(list(external.iterdir()), [])

    def test_output_ancestor_junction_is_rejected_without_external_writes(self):
        external = self.base / "external-output"
        external.mkdir()
        linked_parent = self.base / "linked-output"
        self.make_junction(linked_parent, external)
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, linked_parent / "new-dist")
        self.assertEqual(list(external.iterdir()), [])

    def test_output_target_reparse_point_is_rejected_before_any_release_write(self):
        external = self.base / "external-output"
        external.mkdir()
        self.output.mkdir()
        linked_target = self.output / "ai-musk-skill-v0.1.0.zip"
        self.make_junction(linked_target, external)
        failure = None
        try:
            self.load_builder().build_release(self.root, self.output)
        except (OSError, ValueError) as error:
            failure = error
        self.assertIsInstance(failure, ValueError, "Reject a reparse target explicitly before writing the first ZIP")
        self.assertFalse((self.output / "musk-decision-v0.1.0.zip").exists())
        self.assertEqual(list(external.iterdir()), [])

    def test_output_target_directory_is_rejected_before_any_release_write(self):
        occupied = self.output / "ai-musk-skill-v0.1.0.zip"
        occupied.mkdir(parents=True)
        failure = None
        try:
            self.load_builder().build_release(self.root, self.output)
        except (OSError, ValueError) as error:
            failure = error
        self.assertIsInstance(failure, ValueError, "Reject non-file outputs before writing the first ZIP")
        self.assertEqual(list(self.output.iterdir()), [occupied])

    def test_skill_zip_contains_complete_installable_folder(self):
        paths = self.load_builder().build_release(self.root, self.output)
        self.assertEqual(len(paths), 3)
        with zipfile.ZipFile(self.output / "musk-decision-v0.1.0.zip") as archive:
            names = set(archive.namelist())
            self.assertIn("musk-decision/SKILL.md", names)
            self.assertIn("musk-decision/references/sources.md", names)
            self.assertIn("musk-decision/assets/current-state.md", names)
            self.assertIn("musk-decision/LICENSE", names)

    def test_distribution_excludes_private_state_and_credentials(self):
        self.load_builder().build_release(self.root, self.output)
        for path in self.output.glob("*.zip"):
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                self.assertFalse(any(".." in Path(n).parts for n in names))
                contents = b"\n".join(archive.read(n) for n in names)
                for marker in [b"SECRET", b"NESTED_PRIVATE_NOTE", b"PRIVATE_CACHE"]:
                    self.assertNotIn(marker, contents)

    def test_chatgpt_prompt_is_self_contained_with_resolved_reference_links(self):
        self.load_builder().build_release(self.root, self.output)
        prompt = (self.output / "chatgpt-instructions.md").read_text(encoding="utf-8")
        self.assertIn("Decision method.", prompt)
        self.assertIn("User goals.", prompt)
        self.assertIn("https://www.tesla.com/secret-master-plan", prompt)
        self.assertNotIn("](references/", prompt)
        self.assertNotIn("](assets/", prompt)
        self.assertFalse(prompt.startswith("---"))

    def test_missing_reference_fails_before_writing_release(self):
        (self.root / "skills/musk-decision/references/sources.md").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_version_is_rejected_before_writing_release(self):
        (self.root / "VERSION").write_text("../private", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.load_builder().build_release(self.root, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
