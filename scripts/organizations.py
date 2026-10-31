"""Read typed organization records with neutral, explicit prospecting filters."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def select(root=ROOT, entity="organizations", wave="all", category=None, group=None, player_group=None):
    folders = ("companies", "investors") if entity == "organizations" else (entity,)
    selected = []
    for folder in folders:
        for path in sorted((Path(root) / "data" / folder).glob("*.json")):
            r = json.loads(path.read_text(encoding="utf-8"))
            if wave != "all" and r["targeting"]["wave"] != wave:
                continue
            if player_group and r["targeting"]["player_group"] != player_group:
                continue
            if category and r.get("category_id") != category:
                continue
            if group and r.get("group") != group:
                continue
            selected.append((folder, r))
    return sorted(selected, key=lambda pair: (pair[1]["organization_type"], pair[1]["id"]))
