"""Check the Git index and historical paths before sharing the public framework."""
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = frozenset({
    ".gitignore", "AGENTS.md", "README.md", "taxonomy.md", "requirements-dev.txt",
    "LICENSE", "LICENSE.md",
})
PUBLIC_DIRS = frozenset({
    ".github", "companies", "data", "docs", "exports", "investors",
    "schemas", "scripts", "templates", "tests",
})
PRIVATE_PARTS = frozenset({
    "applications", "application", "local", "private", "resumes", "drafts",
    ".venv", "__pycache__", ".git",
})
CONTENT_PATTERNS = (
    ("absolute home-directory path", re.compile(rb"/(?:Users|home)/[^/\s\x00]+/")),
    ("private key", re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("GitHub credential", re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("API credential", re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b")),
)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def path_problem(name):
    parts = PurePosixPath(name).parts
    folded = [part.casefold() for part in parts]
    if any(part in PRIVATE_PARTS or part == ".env" or part.startswith(".env.") for part in folded):
        return "private workspace or environment file"
    if PurePosixPath(name).suffix.casefold() in {".eml", ".msg", ".pem", ".key", ".p12"}:
        return "personal message or credential file"
    if name in PUBLIC_FILES or (len(parts) > 1 and parts[0] in PUBLIC_DIRS):
        return None
    return "outside the shared file allowlist"


def audit(root=ROOT):
    """Return problems without printing private contents or changing the index."""
    root = Path(root).resolve()
    actual_root = Path(git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if actual_root != root:
        return ["Repository root mismatch: refusing to share a parent workspace. Use this project's own Git repository."]
    problems = []
    seen_blobs = set()
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode("ascii").split()
        name = raw_name.decode("utf-8", errors="replace")
        reason = path_problem(name)
        if reason:
            problems.append("Index: %s (%s)" % (name, reason))
            continue
        if stage != "0" or mode not in {"100644", "100755"}:
            problems.append("Index: %s (unmerged entry, symlink or submodule)" % name)
            continue
        if oid not in seen_blobs:
            content = git(root, "cat-file", "blob", oid)
            for label, pattern in CONTENT_PATTERNS:
                if pattern.search(content):
                    problems.append("Index: %s (%s; content withheld)" % (name, label))
            seen_blobs.add(oid)
    # Ignore rules do not remove private files from earlier commits.
    history = git(root, "log", "--all", "--format=", "--name-only", "-z")
    historical_names = {name.decode("utf-8", errors="replace").strip("\n")
                        for name in history.split(b"\0") if name.strip(b"\n")}
    for name in sorted(historical_names):
        reason = path_problem(name)
        if reason:
            problems.append("History: %s (%s)" % (name, reason))
    return problems


def require_public(root=ROOT):
    problems = audit(root)
    if problems:
        raise SystemExit("Sharing blocked:\n" + "\n".join(problems) +
                         "\nReview locally before committing or pushing. No contents were printed.")


if __name__ == "__main__":
    require_public()
    print("Sharing check passed: Git index and historical file paths follow the public boundary.")
