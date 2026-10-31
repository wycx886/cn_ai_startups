"""Resolve one private workspace without importing its contents into the repository."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG_NAME = "workspace.local.json"


def resolve_workspace(root, value):
    root = Path(root).resolve()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink():
        raise ValueError("Select the real private workspace directory, not a symlink.")
    target = candidate.resolve()
    if target == root or target in root.parents:
        raise ValueError("A private workspace cannot be the repository or its parent.")
    if root in target.parents and target != root / "workspace":
        raise ValueError("Inside the repository, use only the ignored workspace/ directory.")
    return target


def workspace_path(root=ROOT):
    root = Path(root).resolve()
    config = root / CONFIG_NAME
    if not config.exists():
        return resolve_workspace(root, "workspace")
    data = json.loads(config.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("workspace_path"), str):
        raise ValueError("Invalid local workspace configuration.")
    return resolve_workspace(root, data["workspace_path"])


def bind_workspace(root, target):
    root = Path(root).resolve()
    target = resolve_workspace(root, str(target))
    config = root / CONFIG_NAME
    if config.is_symlink():
        raise ValueError("Local configuration must not be a symlink.")
    data = {"schema_version": 1, "workspace_path": os.path.relpath(target, root)}
    config.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    target = workspace_path()
    print(json.dumps({"workspace_path": str(target), "exists": target.is_dir()}, ensure_ascii=False)
          if args.json else str(target))
