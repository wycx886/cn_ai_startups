#!/usr/bin/env python3
"""Audit key people (people[]) and their confirmed public social profiles across organizations."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from organizations import select


def extract_people(record):
    return list(record.get("people", []))


def confirmed_profiles(people):
    return [
        prof for p in people for prof in p.get("profiles", [])
        if prof.get("verification_status") == "confirmed"
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", choices=["organizations", "companies", "operating", "investors"],
                        default="organizations")
    parser.add_argument("--wave", choices=["all", "first", "watchlist", "later"], default="first")
    parser.add_argument("--category", help="Filter operating organizations by category_id")
    parser.add_argument("--missing-only", action="store_true",
                        help="Only list organizations without any confirmed person-level profile")
    parser.add_argument("--summary", action="store_true", help="Print summary coverage statistics")
    args = parser.parse_args()

    records = select(ROOT, args.entity, args.wave, args.category)
    if args.missing_only:
        records = [(f, r) for f, r in records if not confirmed_profiles(extract_people(r))]

    if args.summary:
        op = [r for _, r in records if r["organization_type"] == "operating_organization"]
        inv = [r for _, r in records if r["organization_type"] == "investment_firm"]
        output = {
            "organizations_in_scope": len(records),
            "operating_organizations": {
                "total": len(op),
                "with_named_people": sum(bool(extract_people(r)) for r in op),
                "named_people_count": sum(len(extract_people(r)) for r in op),
                "with_confirmed_profiles": sum(bool(confirmed_profiles(extract_people(r))) for r in op),
                "confirmed_profile_count": sum(len(confirmed_profiles(extract_people(r))) for r in op),
            },
            "investment_firms": {
                "total": len(inv),
                "with_named_people": sum(bool(extract_people(r)) for r in inv),
                "named_people_count": sum(len(extract_people(r)) for r in inv),
                "with_confirmed_profiles": sum(bool(confirmed_profiles(extract_people(r))) for r in inv),
                "confirmed_profile_count": sum(len(confirmed_profiles(extract_people(r))) for r in inv),
            },
        }
    else:
        output = [
            {
                "id": r["id"],
                "name": r["name"],
                "organization_type": r["organization_type"],
                "wave": r["targeting"]["wave"],
                "people": extract_people(r),
            }
            for _, r in records
        ]
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
