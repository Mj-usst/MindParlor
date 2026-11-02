import importlib.util
import os
from pathlib import Path
import stat
import subprocess
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
            capture_output=True, text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            self.skipTest(f"Windows junction creation unavailable: {result.stderr.strip()}")
        self.addCleanup(os.rmdir, link)
        self.assertFalse(link.is_symlink(), "Fixture must exercise junctions, not symlinks")
        self.assertTrue(link.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

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
