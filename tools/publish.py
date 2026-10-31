"""Validate, commit and push shared framework/data changes; exclude personal workspaces."""
import argparse
import subprocess
import sys
from pathlib import Path

from check_public import PUBLIC_DIRS, PUBLIC_FILES, git, require_public

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", help="Commit message for shared changes; keep personal details out")
    parser.add_argument("--check-only", action="store_true", help="Check without staging, committing or pushing")
    args = parser.parse_args()
    if not args.check_only and not (args.message and args.message.strip()):
        parser.error("--message is required unless --check-only is used")
    require_public(ROOT)
    if not args.check_only:
        run(sys.executable, "tools/build.py")
    run(sys.executable, "tools/validate.py", "--check-generated")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tools/tests", "-v")
    if args.check_only:
        print("Checks passed; no files staged, committed or pushed.")
        return
    tracked = git(ROOT, "ls-files", "-z").decode("utf-8").split("\0")
    paths = [name for name in sorted(PUBLIC_FILES | PUBLIC_DIRS)
             if (ROOT / name).exists() or any(p == name or p.startswith(name + "/") for p in tracked)]
    run("git", "add", "-A", "--", *paths)
    require_public(ROOT)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode
    if changed == 1:
        run("git", "commit", "-m", args.message)
    elif changed:
        raise SystemExit("Could not inspect staged changes; nothing was pushed.")
    else:
        print("No new shared changes to commit.")
    require_public(ROOT)
    run("git", "push")


if __name__ == "__main__":
    main()
