"""Query discovery seeds by explicit sector tags and sourced topics, without inferring leadership."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_seeds(root=ROOT, list_name="incumbents"):
    root = Path(root)
    if list_name == "incumbents":
        return json.loads((root / "data/lists/incumbents.json").read_text(encoding="utf-8"))["platforms"]
    if list_name != "vcs":
        raise ValueError("Unknown discovery list")
    from record_checks import load, record_path
    entries = load(root / "data/lists/vcs.json")["entries"]
    seeds = []
    for entry in entries:
        record = load(record_path(root, "investment_firm", entry["company_id"]))
        if record["organization_type"] != "investment_firm" or record["id"] != entry["company_id"]:
            raise ValueError("VC list must reference an investment-firm company record")
        seeds.append({**entry, **{key: record[key] for key in ("id", "name", "aliases", "group", "checked_at")},
                      "official_url": record["contacts"]["website"],
                      "json_path": "data/companies/" + record["id"] + ".json"})
    return seeds


def select_seeds(root=ROOT, sector=None, topic=None, group=None, entity_id=None, list_name="incumbents"):
    selected = []
    for seed in read_seeds(root, list_name):
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
    parser.add_argument("--list", dest="list_name", choices=["incumbents", "vcs"], default="incumbents")
    parser.add_argument("--sector", help="Explicit business tag, e.g. hardware or software; may overlap")
    parser.add_argument("--topic", help="Only seeds with explicitly sourced evidence for this topic")
    parser.add_argument("--group")
    parser.add_argument("--id")
    args = parser.parse_args()
    print(json.dumps(select_seeds(ROOT, args.sector, args.topic, args.group, args.id, args.list_name), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
