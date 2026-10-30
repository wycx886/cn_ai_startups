"""Create one ignored workspace or bind an existing private workspace without copying it."""
import argparse
from pathlib import Path

from workspace import ROOT, bind_workspace, resolve_workspace, workspace_path

COPIES = {
    "README.md": "workspace-guide.md",
    "AGENTS.md": "workspace-agent-rules.md",
    "profile.md": "profile.md",
    "preferences.md": "preferences.md",
    "applications/README.md": "applications-index.md",
    "applications/AGENTS.md": "applications-agent-rules.md",
}
DIRECTORIES = (
    "resume", "drafts", "applications/inbox/done",
    "applications/archive", "applications/headhunters",
)


def initialize(root=ROOT, workspace=None, use_existing=False):
    root = Path(root).resolve()
    target = resolve_workspace(root, workspace) if workspace is not None else workspace_path(root)
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError("Expected a real private workspace directory.")
    if use_existing:
        if not target.is_dir() or not all((target / name).is_file() for name in ("profile.md", "preferences.md")):
            raise ValueError("An existing workspace must contain profile.md and preferences.md.")
        bind_workspace(root, target)
        return [], []
    if workspace is None and not target.exists() and any((root / name).exists() for name in ("local", "applications")):
        raise ValueError("Legacy personal folders found. Consolidate them, then bind with --workspace PATH --use-existing.")
    paths = [target / name for name in (*COPIES, *DIRECTORIES)]
    for path in paths:
        for part in (path, *path.parents):
            if part.is_symlink():
                raise ValueError("Workspace paths must not be symlinks.")
            if part == target:
                break
            if part != path and part.exists() and not part.is_dir():
                raise ValueError("Expected a workspace directory.")
        directory = path.relative_to(target).as_posix() in DIRECTORIES
        if path.exists() and path.is_dir() != directory:
            raise ValueError("Unexpected workspace path type.")
    contents = {name: (root / "templates" / template).read_text(encoding="utf-8")
                for name, template in COPIES.items()}
    created, kept = [], []
    for name, content in contents.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
            created.append(name)
        except FileExistsError:
            kept.append(name)
    for name in DIRECTORIES:
        (target / name).mkdir(parents=True, exist_ok=True)
    bind_workspace(root, target)
    return created, kept


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="Private workspace path; default is the configured path or workspace/")
    parser.add_argument("--use-existing", action="store_true", help="Only bind; do not create or copy personal files")
    args = parser.parse_args()
    added, existing = initialize(workspace=args.workspace, use_existing=args.use_existing)
    print("Existing workspace bound; no personal files copied." if args.use_existing else
          "Workspace ready: %d blank files created, %d existing files preserved." % (len(added), len(existing)))
    print("Personal contents and workspace.local.json stay outside shared commits.")
