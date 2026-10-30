"""Create a blank, ignored personal workspace without overwriting existing records."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    "local/README.md": "local-guide.md",
    "local/profile.md": "profile.md",
    "local/preferences.md": "preferences.md",
    "applications/README.md": "applications-index.md",
    "applications/AGENTS.md": "applications-agent-rules.md",
}
DIRECTORIES = (
    "local/resumes", "local/drafts", "applications/inbox",
    "applications/archive", "applications/headhunters",
)


def initialize(root=ROOT):
    root = Path(root).resolve()
    targets = [root / p for p in (*COPIES, *DIRECTORIES)]
    # Refuse links or file/directory collisions before creating anything.
    for target in targets:
        for part in (target, *target.parents):
            if part == root:
                break
            if part.is_symlink():
                raise ValueError("Local workspace path must not be a symlink: " + str(part))
            if part != target and part.exists() and not part.is_dir():
                raise ValueError("Expected directory: " + str(part))
        if target.exists() and target.is_dir() != (target.relative_to(root).as_posix() in DIRECTORIES):
            raise ValueError("Unexpected workspace path type: " + str(target))
    contents = {name: (root / "templates" / template).read_text(encoding="utf-8")
                for name, template in COPIES.items()}
    created, kept = [], []
    for name, content in contents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
            created.append(name)
        except FileExistsError:
            kept.append(name)
    for name in DIRECTORIES:
        (root / name).mkdir(parents=True, exist_ok=True)
    return created, kept


if __name__ == "__main__":
    added, existing = initialize()
    print("Local workspace ready: %d blank files created, %d existing files preserved." %
          (len(added), len(existing)))
    print("applications/ and local/ stay local; no personal information was imported.")
