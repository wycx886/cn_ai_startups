"""Verify public people updates against isolated records, without network or private workspaces."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from record_checks import load, validate_record


def module_at(name, relative):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPDATE = module_at("people_updater_tests", "skills/find-person/scripts/update_people.py")
AUDIT = module_at("people_audit_tests", "skills/find-person/scripts/audit_people.py")


class PeopleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / "repo").resolve()
        shutil.copytree(REPO / "data/schemas", self.root / "data/schemas")
        (self.root / "data/companies").mkdir()
        self.record = load(REPO / "data/companies/hypershell.json")
        self.record["channels"] = []
        self.record["people"] = []
        self.record["sources"] = [s for s in self.record["sources"] if s.get("scope", "organization") == "organization"]
        self.path = self.root / "data/companies/hypershell.json"
        self.write_record(self.path, self.record)

    def write_record(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def entry(self, **changes):
        value = {
            "entity_type": "operating_organization", "entity_id": "hypershell",
            "person_name": "Synthetic Founder", "person_role": "Founder & CEO",
            "background": "Synthetic test background, not a real person's biography.",
            "previous_firms": [], "platform": "linkedin",
            "url": "https://www.linkedin.com/in/synthetic-founder/?utm_source=test#bio",
            "checked_at": "2026-10-31", "evidence_title": "Synthetic public professional profile",
            "verification_status": "confirmed", "notes": "Synthetic unit-test observation only.",
            "identity_evidence": [{
                "title": "Synthetic company team page", "url": "https://synthetic-company.org/team/founder",
                "supports": "Synthetic named founder and current role for this test only.",
                "published_date": None, "checked_at": "2026-10-31",
            }],
        }
        value.update(changes)
        return value

    def batch(self, *entries):
        return {"schema_version": 1, "public_only": True, "entries": list(entries or [self.entry()])}

    def invoke(self, batch, *args):
        output = io.StringIO()
        with patch.object(UPDATE, "ROOT", self.root), patch.object(sys, "argv", ["update_people", *args]), \
             patch.object(sys, "stdin", io.StringIO(json.dumps(batch))), contextlib.redirect_stdout(output):
            UPDATE.main()
        return json.loads(output.getvalue())

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in (self.root / "data").rglob("*.json")}

    def apply(self, *entries):
        UPDATE.apply_changes(UPDATE.plan_person_changes(self.batch(*entries), self.root))
        return load(self.path)

    def two_company_changes(self):
        second = copy.deepcopy(self.record)
        second.update(id="synthetic-second", name="Synthetic Second Company")
        second_path = self.path.parent / "synthetic-second.json"
        self.write_record(second_path, second)
        changes = UPDATE.plan_person_changes(self.batch(
            self.entry(), self.entry(entity_id="synthetic-second", person_name="Synthetic Second Founder")), self.root)
        return second_path, changes

    def test_stdin_preview_then_apply_writes_people_only_without_private_workspace(self):
        before = self.snapshot()
        preview = self.invoke(self.batch())
        self.assertTrue(preview["dry_run"])
        self.assertEqual(before, self.snapshot())
        result = self.invoke(self.batch(), "--apply")
        self.assertFalse(result["dry_run"])
        record = load(self.path)
        person = record["people"][0]
        self.assertEqual(person["name"], "Synthetic Founder")
        self.assertEqual(person["role"], "Founder & CEO")
        self.assertEqual(record["channels"], [])
        self.assertEqual(record["checked_at"], self.record["checked_at"])
        self.assertEqual(record["contacts"], self.record["contacts"])
        self.assertEqual(record["sources"][:len(self.record["sources"])], self.record["sources"])
        self.assertTrue(all(s["scope"] == "person" for s in record["sources"][len(self.record["sources"]):]))
        self.assertEqual(person["checked_at"], "2026-10-31")
        self.assertGreaterEqual(len(person["source_ids"]), 2)
        self.assertNotIn("?", person["profiles"][0]["url"])
        self.assertNotIn("#", person["profiles"][0]["url"])
        self.assertEqual(validate_record(record, self.root), record)
        self.assertFalse((self.root / "workspace").exists())
        self.assertFalse((self.root / "workspace.local.json").exists())
        self.assertFalse((self.root / "applications").exists())

    def test_repeated_observation_is_idempotent(self):
        self.apply()
        before = self.snapshot()
        self.assertEqual(UPDATE.plan_person_changes(self.batch(), self.root), {})
        self.assertEqual(before, self.snapshot())

    def test_unknown_private_and_unverified_input_fields_are_rejected(self):
        for change in [{"private_notes": "Synthetic private communication"},
                       {"verification_status": "partial"}, {"entity_type": "unknown"},
                       {"entity_id": "../hypershell"}, {"entity_id": "missing-company"},
                       {"checked_at": "2999-01-01"}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                UPDATE.plan_person_changes(self.batch(self.entry(**change)), self.root)
        for key, value in [("public_only", False), ("schema_version", 999), ("private_context", "Synthetic private note")]:
            batch = self.batch()
            batch[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                UPDATE.plan_person_changes(batch, self.root)

    def test_profile_urls_must_match_platform_and_specific_person(self):
        cases = [
            {"url": "https://github.com/openai"},
            {"url": "https://www.linkedin.com/company/synthetic-company/"},
            {"url": "https://www.linkedin.com/in/"},
            {"url": "https://www.linkedin.com.attacker.org/in/person"},
            {"url": "https://account:secret@www.linkedin.com/in/person"},
            {"url": "http://www.linkedin.com/in/person"},
            {"url": "https://www.linkedin.com/in/%2e%2e/person"},
            {"platform": "x", "url": "https://x.com/search"},
            {"platform": "x", "url": "https://x.com/synthetic-founder/status/123"},
            {"platform": "github", "url": "https://github.com/synthetic-founder/repository"},
        ]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(ValueError):
                UPDATE.plan_person_changes(self.batch(self.entry(**change)), self.root)

    def test_github_requires_observed_user_type_and_api_identity_evidence(self):
        evidence = {
            "title": "Synthetic GitHub account metadata", "url": "https://api.github.com/users/synthetic-founder",
            "supports": "Synthetic API observation: login synthetic-founder; type User.",
            "published_date": None, "checked_at": "2026-10-31",
        }
        entry = self.entry(platform="github", url="https://github.com/synthetic-founder", account_type="User",
                           identity_evidence=[evidence])
        record = self.apply(entry)
        self.assertEqual(record["people"][0]["profiles"][0]["account_type"], "User")
        for change in [{"account_type": "Organization"}, {"account_type": None},
                       {"identity_evidence": self.entry()["identity_evidence"]}]:
            bad = copy.deepcopy(entry)
            bad.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                UPDATE.plan_person_changes(self.batch(bad), self.root)

    def test_person_identity_requires_distinct_supporting_evidence(self):
        for evidences in [[], [{**self.entry()["identity_evidence"][0], "url": self.entry()["url"]}]]:
            with self.subTest(evidence=evidences), self.assertRaises(ValueError):
                UPDATE.plan_person_changes(self.batch(self.entry(identity_evidence=evidences)), self.root)
        incomplete = self.entry()
        del incomplete["identity_evidence"][0]["supports"]
        with self.assertRaises(ValueError):
            UPDATE.plan_person_changes(self.batch(incomplete), self.root)

    def test_old_observation_cannot_downgrade_person_profile_or_sources(self):
        self.apply()
        before = self.snapshot()
        old = self.entry(checked_at="2026-10-30")
        old["identity_evidence"][0]["checked_at"] = "2026-10-30"
        with self.assertRaises(ValueError):
            UPDATE.plan_person_changes(self.batch(old), self.root)
        self.assertEqual(before, self.snapshot())

    def test_person_facts_require_source_references_and_real_check_date(self):
        record = self.apply()
        for change in [{"source_ids": []}, {"source_ids": ["s999"]}, {"checked_at": "2999-01-01"}]:
            broken = copy.deepcopy(record)
            broken["people"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_record(broken, self.root)

    def test_channels_cannot_store_a_person_owner(self):
        record = copy.deepcopy(self.record)
        record["channels"] = [{
            "id": "ch-synthetic-person", "layer": "professional_social", "platform": "linkedin",
            "url": "https://www.linkedin.com/in/synthetic-founder", "purpose": "public_profile",
            "owner": {"scope": "person", "name": "Synthetic Founder", "role": "Founder"},
            "verification_status": "confirmed", "checked_at": record["checked_at"],
            "source_ids": [record["sources"][0]["id"]], "notes": None,
        }]
        with self.assertRaises(ValueError):
            validate_record(record, self.root)

    def test_invalid_second_entry_prevents_all_writes(self):
        before = self.snapshot()
        invalid = self.entry(entity_id="missing-company")
        with self.assertRaises(ValueError):
            self.invoke(self.batch(self.entry(), invalid), "--apply")
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_edit_is_preserved_and_no_other_record_is_written(self):
        second_path, changes = self.two_company_changes()
        original_first = self.path.read_bytes()
        external = second_path.read_bytes() + b"\n"
        second_path.write_bytes(external)
        with self.assertRaises(ValueError):
            UPDATE.apply_changes(changes)
        self.assertEqual(self.path.read_bytes(), original_first)
        self.assertEqual(second_path.read_bytes(), external)
        self.assertFalse(list(self.path.parent.glob(".*.tmp")))

    def test_second_write_failure_rolls_back_first_and_removes_temporary_files(self):
        second_path, changes = self.two_company_changes()
        before = self.snapshot()
        replace = Path.replace

        def fail_second(path, target):
            if target == second_path:
                raise OSError("Synthetic second-record write failure")
            return replace(path, target)

        with patch.object(Path, "replace", new=fail_second), self.assertRaises(OSError):
            UPDATE.apply_changes(changes)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(self.path.parent.glob(".*.tmp")))

    def test_rollback_does_not_overwrite_another_writers_newer_changes(self):
        _, changes = self.two_company_changes()
        replace = Path.replace
        external = {}

        def external_edits(path, target):
            result = replace(path, target)
            if target == self.path:
                for changed_path in changes:
                    external[changed_path] = changed_path.read_bytes() + b"\n"
                    changed_path.write_bytes(external[changed_path])
            return result

        with patch.object(Path, "replace", new=external_edits), self.assertRaises(ValueError):
            UPDATE.apply_changes(changes)
        self.assertTrue(external)
        for path, content in external.items():
            self.assertEqual(path.read_bytes(), content)

    def test_common_team_page_preserves_each_persons_distinct_assertion(self):
        first = self.entry()
        first["identity_evidence"][0].update(
            url="https://synthetic-company.org/team",
            supports="Synthetic Founder is CEO in this synthetic team-page observation.")
        second = self.entry(person_name="Synthetic Second Founder", person_role="CTO",
                            url="https://www.linkedin.com/in/synthetic-second-founder/")
        second["identity_evidence"][0].update(
            url="https://synthetic-company.org/team",
            supports="Synthetic Second Founder is CTO in this synthetic team-page observation.")
        record = self.apply(first, second)
        sources = {source["id"]: source for source in record["sources"]}
        people = {person["name"]: person for person in record["people"]}
        for entry in (first, second):
            person = people[entry["person_name"]]
            claims = [sources[source_id]["supports"] for source_id in person["source_ids"]
                      if sources[source_id]["url"] == "https://synthetic-company.org/team"]
            self.assertIn(entry["identity_evidence"][0]["supports"], claims)
        self.assertEqual(validate_record(record, self.root), record)

    def test_changed_identity_evidence_keeps_retired_source_as_history(self):
        original = self.apply()
        old_evidence = next(source for source in original["sources"]
                            if source["url"] == self.entry()["identity_evidence"][0]["url"])
        next_day = self.entry(checked_at="2026-11-01")
        next_day["identity_evidence"][0].update(
            url="https://synthetic-company.org/leadership/founder",
            checked_at="2026-11-01")
        record = self.apply(next_day)
        person = record["people"][0]
        sources = {source["id"]: source for source in record["sources"]}
        self.assertEqual(person["checked_at"], "2026-11-01")
        self.assertIn(old_evidence["id"], person["historical_source_ids"])
        self.assertNotIn(old_evidence["id"], person["source_ids"])
        self.assertEqual(sources[old_evidence["id"]], old_evidence)
        self.assertEqual(validate_record(record, self.root), record)
        self.assertEqual(UPDATE.plan_person_changes(self.batch(next_day), self.root), {})

    def test_changed_claim_at_same_url_preserves_old_claim_and_profile_history(self):
        original = self.apply()
        old_person_sources = {source["id"]: source for source in original["sources"]
                              if source.get("scope") == "person"}
        updated = self.entry(person_role="Chief Scientist", checked_at="2026-11-01")
        updated["identity_evidence"][0].update(
            supports="Synthetic Founder is now Chief Scientist in this synthetic observation.",
            checked_at="2026-11-01")
        record = self.apply(updated)
        person = record["people"][0]
        sources = {source["id"]: source for source in record["sources"]}
        self.assertEqual(person["role"], "Chief Scientist")
        self.assertEqual(person["checked_at"], "2026-11-01")
        for source_id, old_source in old_person_sources.items():
            self.assertEqual(sources[source_id], old_source)
            self.assertIn(source_id, person["historical_source_ids"])
            self.assertNotIn(source_id, person["source_ids"])
        self.assertTrue(any(sources[source_id]["supports"] == updated["identity_evidence"][0]["supports"]
                            for source_id in person["source_ids"]))
        self.assertEqual(validate_record(record, self.root), record)

    def test_people_audit_does_not_mix_legacy_team_into_people(self):
        canonical = {"name": "Canonical Person", "profiles": []}
        legacy = {"name": "Legacy Team Person", "profiles": []}
        self.assertEqual(AUDIT.extract_people({"people": [canonical], "team": [legacy]}), [canonical])


if __name__ == "__main__":
    unittest.main()
