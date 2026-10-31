"""Exercise real Git sharing boundaries using disposable repositories and synthetic records."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from check_public import audit
sys.path.insert(0, str(REPO / "skills/setup-workspace/scripts"))
from init_local import COPIES, DIRECTORIES, initialize
from workspace import CONFIG_NAME, ROOT as WORKSPACE_ROOT, workspace_path


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        shutil.copytree(REPO / "skills/setup-workspace/assets/templates", self.root / "skills/setup-workspace/assets/templates")
        shutil.copyfile(REPO / ".gitignore", self.root / ".gitignore")
        self.git("init", "-q")
        self.git("config", "user.name", "Workspace Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_skill_scripts_resolve_the_repository_root(self):
        self.assertEqual(WORKSPACE_ROOT, REPO)

    def test_default_workspace_is_blank_and_idempotent(self):
        created, kept = initialize(self.root)
        target = self.root / "workspace"
        self.assertEqual(set(created), set(COPIES))
        self.assertFalse(kept)
        self.assertEqual(workspace_path(self.root), target.resolve())
        self.assertTrue(all((target / name).is_dir() for name in DIRECTORIES))
        self.assertIn("待填写", (target / "profile.md").read_text())
        self.assertFalse(list((target / "applications").glob("*/log.md")))
        self.assertTrue((target / "applications/inbox").is_dir())
        self.assertFalse((target / "research/inbox").exists())
        self.write("workspace/profile.md", "Synthetic facts; preserve me.\n")
        self.write("workspace/applications/example/log.md", "Synthetic progress; preserve me.\n")
        before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
        created, kept = initialize(self.root)
        self.assertFalse(created)
        self.assertEqual(set(kept), set(COPIES))
        for name, content in before.items():
            self.assertEqual((target / name).read_bytes(), content)

    def test_binding_existing_external_workspace_does_not_copy_or_modify_it(self):
        target = Path(self.temp.name) / "private-workspace"
        target.mkdir()
        for name in ("profile.md", "preferences.md"):
            (target / name).write_text("Synthetic existing record\n")
        before = {p.name: p.read_bytes() for p in target.iterdir()}
        created, kept = initialize(self.root, workspace="../private-workspace", use_existing=True)
        self.assertEqual((created, kept), ([], []))
        self.assertEqual(workspace_path(self.root), target.resolve())
        self.assertEqual(before, {p.name: p.read_bytes() for p in target.iterdir()})
        self.assertFalse((self.root / "workspace").exists())
        self.git("add", ".")
        self.assertNotIn(CONFIG_NAME, self.git("ls-files").decode().splitlines())
        self.assertEqual(audit(self.root), [])

    def test_invalid_workspace_targets_are_rejected(self):
        for target in (".", "..", "data/personal"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                initialize(self.root, workspace=target)
        self.assertFalse((self.root / CONFIG_NAME).exists())

    def test_use_existing_requires_existing_facts_and_preferences(self):
        with self.assertRaises(ValueError):
            initialize(self.root, workspace="../missing", use_existing=True)
        self.assertFalse((self.root / CONFIG_NAME).exists())

    def test_initialization_refuses_linked_workspace(self):
        (self.root / "workspace").symlink_to(self.root / "skills/setup-workspace/assets/templates", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            initialize(self.root)
        self.assertFalse((self.root / CONFIG_NAME).exists())

    def test_legacy_workspace_does_not_silently_create_a_second_one(self):
        self.write("local/profile.md", "Synthetic existing facts\n")
        with self.assertRaisesRegex(ValueError, "Legacy"):
            initialize(self.root)
        self.assertFalse((self.root / "workspace").exists())

    def test_normal_add_excludes_workspace_configuration_and_legacy_personal_paths(self):
        initialize(self.root)
        fixtures = ("workspace/resume/resume.md", "workspace/applications/example/log.md",
                    "local/profile.md", "applications/example/log.md", "private/note.md",
                    "resume/resume.md", "resumes/resume.md", "profile.md", ".env", "draft.eml")
        for name in fixtures:
            self.write(name, "Synthetic private fixture\n")
        self.git("add", ".")
        paths = set(self.git("ls-files").decode().splitlines())
        self.assertIn("skills/setup-workspace/assets/templates/profile.md", paths)
        self.assertFalse(paths.intersection((*fixtures, CONFIG_NAME)))
        self.assertFalse(any(p.startswith("workspace/") for p in paths))
        self.assertEqual(audit(self.root), [])

    def test_force_added_workspace_and_path_configuration_are_blocked(self):
        for name in ("workspace/profile.md", CONFIG_NAME):
            with self.subTest(name=name):
                self.write(name, "Synthetic private fixture\n")
                self.git("add", "-f", name)
                self.assertTrue(any("Index: " + name in p for p in audit(self.root)))

    def test_missing_nested_repository_cannot_use_parent_workspace(self):
        nested = self.root / "shared-project"
        nested.mkdir()
        self.write("docs/personal-note.md", "Synthetic private parent content\n")
        self.git("add", "docs/personal-note.md")
        self.assertTrue(any("Repository root mismatch" in p for p in audit(nested)))

    def test_deleted_private_history_is_still_blocked(self):
        self.write("workspace/profile.md", "Synthetic private fixture\n")
        self.git("add", "-f", "workspace/profile.md")
        self.git("commit", "-qm", "Synthetic fixture")
        self.git("rm", "-q", "workspace/profile.md")
        self.git("commit", "-qm", "Remove synthetic fixture")
        self.assertTrue(any("History: workspace/profile.md" in p for p in audit(self.root)))

    def test_historical_public_views_are_allowed_after_catalog_migration(self):
        self.write("companies/example.md", "Synthetic public view\n")
        self.git("add", "companies/example.md")
        self.git("commit", "-qm", "Old public view")
        (self.root / "catalog/companies").mkdir(parents=True)
        self.git("mv", "companies/example.md", "catalog/companies/example.md")
        self.git("commit", "-qm", "Intermediate public view layout")
        (self.root / "data/views/companies").mkdir(parents=True)
        self.git("mv", "catalog/companies/example.md", "data/views/companies/example.md")
        self.assertEqual(audit(self.root), [])

    def test_retired_root_layout_and_duplicate_indexes_cannot_be_reintroduced(self):
        for name in ("docs/sample.md", "scripts/sample.py", "templates/sample.md", "catalog/sample.md",
                     "schemas/sample.json", "tests/sample.py", "data/targets.json", "data/investor-index.json",
                     "data/investors/sample.json", "data/views/investors/sample.md", "data/platforms.json"):
            with self.subTest(name=name):
                self.write(name, "Synthetic obsolete-layout fixture\n")
                self.git("add", name)
                self.assertTrue(any("Index: " + name in p for p in audit(self.root)))

    def test_unexpected_top_level_file_is_blocked(self):
        self.write("personal-notes.md", "Synthetic fixture\n")
        self.git("add", "personal-notes.md")
        self.assertTrue(any("outside the shared file allowlist" in p for p in audit(self.root)))

    def test_shared_symlink_is_blocked(self):
        (self.root / "data").mkdir()
        (self.root / "data/linked.md").symlink_to("../workspace/profile.md")
        self.git("add", "data/linked.md")
        self.assertTrue(any("symlink" in p for p in audit(self.root)))

    def test_home_paths_and_credentials_are_blocked_without_echoing_content(self):
        fixtures = ("/" + "home" + "/example/person/private.md", "ghp_" + "a" * 36,
                    "sk-proj-" + "b" * 40, "-----BEGIN " + "PRIVATE KEY-----")
        for content in fixtures:
            with self.subTest(kind=content[:3]):
                self.write("data/sample.md", content + "\n")
                self.git("add", "data/sample.md")
                problems = audit(self.root)
                self.assertTrue(any("content withheld" in p for p in problems))
                self.assertNotIn(content, "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
