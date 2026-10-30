"""Exercise privacy boundaries in disposable Git repositories, using synthetic records."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from check_public import audit
from init_local import COPIES, DIRECTORIES, initialize


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(REPO / "templates", self.root / "templates")
        shutil.copyfile(REPO / ".gitignore", self.root / ".gitignore")
        self.git("init", "-q")
        self.git("config", "user.name", "cn_ai_startups Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_initialization_is_blank_and_preserves_existing_records(self):
        created, kept = initialize(self.root)
        self.assertEqual(set(created), set(COPIES))
        self.assertFalse(kept)
        self.assertTrue(all((self.root / name).is_dir() for name in DIRECTORIES))
        self.assertIn("待填写", (self.root / "local/profile.md").read_text())
        self.assertFalse(list((self.root / "applications").glob("*/log.md")))
        self.write("local/profile.md", "Synthetic local facts; preserve me.\n")
        self.write("applications/example/log.md", "Synthetic progress; preserve me.\n")
        before = {p.relative_to(self.root): p.read_bytes()
                  for top in ("local", "applications") for p in (self.root / top).rglob("*") if p.is_file()}
        created, kept = initialize(self.root)
        self.assertFalse(created)
        self.assertEqual(set(kept), set(COPIES))
        for name, contents in before.items():
            self.assertEqual((self.root / name).read_bytes(), contents)

    def test_initialization_refuses_linked_workspace(self):
        (self.root / "local").symlink_to(self.root / "templates", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            initialize(self.root)
        self.assertFalse((self.root / "applications").exists())

    def test_normal_add_excludes_personal_files(self):
        initialize(self.root)
        for name in ("applications/example/log.md", "local/drafts/note.md", "private/note.md",
                     "resumes/resume.md", "profile.md", "preferences.json", ".env", "draft.eml"):
            self.write(name, "Synthetic private fixture\n")
        self.git("add", ".")
        paths = self.git("ls-files", "-z").decode().split("\0")
        self.assertIn("templates/profile.md", paths)
        self.assertTrue(all(not p.startswith(("applications/", "local/", "private/", "resumes/")) for p in paths))
        self.assertEqual(audit(self.root), [])

    def test_force_added_private_file_is_blocked(self):
        self.write("applications/example/log.md", "Synthetic private fixture\n")
        self.git("add", "-f", "applications/example/log.md")
        self.assertTrue(any("Index: applications/example/log.md" in p for p in audit(self.root)))

    def test_deleted_private_history_is_still_blocked(self):
        self.write("local/profile.md", "Synthetic private fixture\n")
        self.git("add", "-f", "local/profile.md")
        self.git("commit", "-qm", "Synthetic fixture")
        self.git("rm", "-q", "local/profile.md")
        self.git("commit", "-qm", "Remove synthetic fixture")
        self.assertTrue(any("History: local/profile.md" in p for p in audit(self.root)))

    def test_unexpected_top_level_file_is_blocked(self):
        self.write("personal-notes.md", "Synthetic fixture\n")
        self.git("add", "personal-notes.md")
        self.assertTrue(any("outside the shared file allowlist" in p for p in audit(self.root)))

    def test_shared_symlink_is_blocked(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/linked.md").symlink_to("../local/profile.md")
        self.git("add", "docs/linked.md")
        self.assertTrue(any("symlink" in p for p in audit(self.root)))

    def test_home_paths_and_credentials_are_blocked_without_echoing_content(self):
        fixtures = (
            "/" + "home" + "/example/person/private.md",
            "ghp_" + "a" * 36,
            "sk-proj-" + "b" * 40,
            "-----BEGIN " + "PRIVATE KEY-----",
        )
        for content in fixtures:
            with self.subTest(kind=content[:3]):
                self.write("docs/sample.md", content + "\n")
                self.git("add", "docs/sample.md")
                problems = audit(self.root)
                self.assertTrue(any("content withheld" in p for p in problems))
                self.assertNotIn(content, "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
