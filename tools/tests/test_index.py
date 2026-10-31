"""Protect complete, source-dated discovery metadata through index consolidation."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build
from targets import build_index


class UnifiedIndexTests(unittest.TestCase):
    def setUp(self):
        self.records = [(folder, json.loads(path.read_text()))
                        for folder in ("companies",)
                        for path in sorted((ROOT / "data" / folder).glob("*.json"))]
        self.index = build_index(ROOT, self.records)

    def test_every_record_has_one_typed_entry_with_original_dates_and_paths(self):
        entries = {(entry["organization_type"], entry["id"]): entry
                   for entry in self.index["organizations"]}
        self.assertEqual(len(entries), len(self.records))
        self.assertEqual(self.index["counts"]["organizations"], len(self.records))
        for folder, record in self.records:
            entry = entries[(record["organization_type"], record["id"])]
            for field in ("name", "aliases", "focus", "targeting", "checked_at"):
                self.assertEqual(entry[field], record[field])
            self.assertEqual(entry["json_path"], f"data/{folder}/{record['id']}.json")
            self.assertEqual(entry["markdown_path"], f"data/views/{folder}/{record['id']}.md")

    def test_type_specific_metadata_remains_available_without_extra_indexes(self):
        for entry in self.index["organizations"]:
            record = json.loads((ROOT / entry["json_path"]).read_text())
            if entry["organization_type"] == "operating_organization":
                self.assertEqual(entry["category_id"], record["category_id"])
                self.assertEqual(entry["investment_status"], record["investment"]["verification_status"])
                self.assertIn("category_name", entry)
                if "organizational_context" in record:
                    self.assertEqual(entry["organizational_context"], record["organizational_context"])
            else:
                self.assertEqual(entry["group"], record["group"])
                self.assertEqual(entry["stage"], record["stage"])
                self.assertEqual(entry["coverage_role"], record["coverage"]["role"])
                self.assertEqual(entry["founded_year"], record["founded"]["year"])
                self.assertEqual(entry["team_names"], [p["name"] for p in record["team"]])
                self.assertEqual(entry["previous_platforms"], sorted({f for p in record["team"] for f in p["previous_firms"]}))
                self.assertEqual(entry["prior_firm_case_count"] + entry["current_firm_case_count"], len(record["representative_cases"]))
                self.assertIn("cohort", entry)
        for label, kind in [("operating_organizations", "operating_organization"), ("investment_firms", "investment_firm")]:
            self.assertEqual(self.index["statistics"][label]["source_records"],
                             sum(len(record["sources"]) for _, record in self.records if record["organization_type"] == kind))

    def test_build_exposes_one_index_and_all_profile_views_under_data(self):
        output = build.outputs()
        self.assertEqual({name for name in output if name.endswith(".json")}, {"data/index.json"})
        self.assertTrue(all(name == "data/index.json" or name.startswith("data/views/") for name in output))
        for entry in self.index["organizations"]:
            self.assertIn(entry["markdown_path"], output)
        generated_index = json.loads(output["data/index.json"])
        self.assertEqual(generated_index, self.index)


if __name__ == "__main__":
    unittest.main()
