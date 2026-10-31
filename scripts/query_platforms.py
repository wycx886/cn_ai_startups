"""Query discovery seeds by explicit sector tags and sourced topics, without inferring leadership."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def select_seeds(root=ROOT, sector=None, topic=None, group=None, entity_id=None):
    registry = json.loads((Path(root) / "data/platforms.json").read_text(encoding="utf-8"))
    selected = []
    for seed in registry["platforms"]:
        if entity_id and seed["id"] != entity_id:
            continue
        if group and seed["group"] != group:
            continue
        if sector and sector.casefold() not in {s.casefold() for s in seed.get("sectors", [])}:
            continue
        if topic and topic.casefold() not in {e["topic"].casefold() for e in seed.get("topic_evidence", [])}:
            continue
        selected.append(seed)
    return sorted(selected, key=lambda seed: seed["id"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sector", help="Explicit business tag, e.g. hardware or software; may overlap")
    parser.add_argument("--topic", help="Only seeds with explicitly sourced evidence for this topic")
    parser.add_argument("--group")
    parser.add_argument("--id")
    args = parser.parse_args()
    print(json.dumps(select_seeds(ROOT, args.sector, args.topic, args.group, args.id), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
