"""Exercise real research workflows against disposable public-record fixtures."""
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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from organizations import select
from record_checks import load, platform_url, record_path, validate_record
from targets import render


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCAFFOLD = module_at("research_scaffold", "skills/find-company/scripts/scaffold_entity.py")
MERGE = module_at("research_merge", "skills/find-channels/scripts/merge_layer2_inbox.py")
CHANNEL_AUDIT = module_at("channel_audit", "skills/find-channels/scripts/audit_channels.py")
ENTITY_AUDIT = module_at("entity_audit", "skills/find-company/scripts/audit_entities.py")


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(REPO / "schemas", self.root / "schemas")
        (self.root / "data/companies").mkdir(parents=True)
        (self.root / "data/investors").mkdir()
        shutil.copyfile(REPO / "data/taxonomy.json", self.root / "data/taxonomy.json")
        shutil.copyfile(REPO / "data/platforms.json", self.root / "data/platforms.json")
        for folder, name in [("companies", "hypershell"), ("companies", "gaoding"),
                             ("investors", "monolith"), ("investors", "hongshan")]:
            shutil.copyfile(REPO / "data" / folder / (name + ".json"),
                            self.root / "data" / folder / (name + ".json"))
        self.company = self.root / "data/companies/hypershell.json"
        self.investor = self.root / "data/investors/monolith.json"

    def invoke(self, module, *args):
        output = io.StringIO()
        with patch.object(module, "ROOT", self.root), patch.object(sys, "argv", ["tool", *args]), contextlib.redirect_stdout(output):
            module.main()
        return output.getvalue()

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in (self.root / "data").rglob("*.json")}

    def entry(self, investor=False):
        record = load(self.investor if investor else self.company)
        return {"entity_type": record["organization_type"], "entity_id": record["id"],
                "platform": "boss_zhipin", "url": "https://www.zhipin.com/gongsi/synthetic-id.html?tracking=discard#top",
                "observed_name": record["name"], "checked_at": record["checked_at"],
                "evidence_title": record["name"] + " · 公开企业主页", "verification_status": "confirmed"}

    def batch(self, *entries):
        return {"schema_version": 1, "public_only": True, "entries": list(entries or [self.entry()])}

    def write_batch(self, batch):
        path = self.root / "candidate.json"
        path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def test_first_wave_unifies_organization_types_without_year_gate(self):
        investor = load(self.investor)
        investor["founded"]["year"] = 2005  # A label, not a founding-year threshold, drives selection.
        self.investor.write_text(json.dumps(investor), encoding="utf-8")
        first = [r for _, r in select(self.root, wave="first")]
        self.assertEqual({r["id"] for r in first}, {"hypershell", "monolith"})
        self.assertEqual({r["organization_type"] for r in first}, {"operating_organization", "investment_firm"})
        self.assertEqual([r["id"] for _, r in select(self.root, wave="later")], ["hongshan"])
        self.assertEqual([r["id"] for _, r in select(self.root, wave="watchlist")], ["gaoding"])

    def test_generated_target_index_and_views_agree(self):
        output = render(self.root)
        index = json.loads(output["data/targets.json"])
        self.assertEqual(index["counts"], {"organizations": 4, "first": 2, "watchlist": 1, "later": 1})
        for entry in index["organizations"]:
            source = load(self.root / entry["json_path"])
            self.assertEqual(entry["checked_at"], source["checked_at"])
            self.assertEqual(entry["targeting"], source["targeting"])
        self.assertIn("investors/monolith.md", output["catalog/first-wave.md"])
        self.assertNotIn("investors/hongshan.md", output["catalog/first-wave.md"])
        self.assertIn("investors/hongshan.md", output["catalog/later.md"])
        self.assertNotIn("investors/hongshan.md", output["catalog/new-vc-spinouts.md"])

    def test_entity_audit_date_filter_applies_to_investors(self):
        output = self.invoke(ENTITY_AUDIT, "--entity", "investors", "--before", "2000-01-01")
        self.assertEqual(json.loads(output), [])
        all_records = json.loads(self.invoke(ENTITY_AUDIT, "--entity", "investors", "--before", "2099-01-01"))
        self.assertEqual({r["id"] for r in all_records}, {"monolith", "hongshan"})

    def internal_unit(self):
        record = load(self.company)
        record.update(id="synthetic-unit", name="合成内部项目", aliases=["Synthetic internal unit"])
        record["sources"] = [{"id": "s01", "title": "合成单元测试依据", "url": "https://www.bytedance.com/about",
                              "supports": "合成测试，不代表实际项目或真实股权关系", "published_date": None,
                              "checked_at": record["checked_at"]}]
        record["targeting"]["source_ids"] = ["s01"]
        record["investment"] = {"summary": "合成的已确认内部单元，不适用独立主体股权融资。", "verification_status": "not_applicable"}
        record["organizational_context"] = {"form": "internal_team", "parent_platform_ids": ["bytedance"],
            "relationship_status": "confirmed", "summary": "合成内部团队测试，不代表真实项目。", "source_ids": ["s01"],
            "checked_at": record["checked_at"]}
        return record

    def test_internal_initiative_can_be_first_wave_without_independent_equity_funding(self):
        record = self.internal_unit()
        validate_record(record, self.root)
        path = self.company.parent / "synthetic-unit.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        selected = select(self.root, wave="first", form="internal_team", parent="bytedance")
        self.assertEqual([r["id"] for _, r in selected], ["synthetic-unit"])
        output = json.loads(render(self.root)["data/targets.json"])
        entry = next(r for r in output["organizations"] if r["id"] == "synthetic-unit")
        self.assertEqual(entry["organizational_context"], record["organizational_context"])
        self.assertEqual(entry["investment_status"], "not_applicable")

    def test_missing_organization_form_does_not_mean_independent(self):
        self.assertEqual(select(self.root, form="independent_organization"), [])
        self.assertEqual(select(self.root, parent="bytedance"), [])
        self.assertEqual(len(select(self.root)), 4)  # Parent seeds are not targets.

    def test_relationships_require_real_parent_ids_and_business_evidence(self):
        for change in [{"parent_platform_ids": ["missing-platform"]}, {"source_ids": ["s99"]}, {"parent_platform_ids": []}]:
            record = self.internal_unit()
            record["organizational_context"].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_record(record, self.root)

    def test_non_applicable_finance_is_not_a_fallback_for_unknown_funding(self):
        record = load(self.company)
        record["investment"]["verification_status"] = "not_applicable"
        with self.assertRaises(ValueError):
            validate_record(record, self.root)
        for change in [{"form": "corporate_spinout"}, {"relationship_status": "reported"}]:
            record = self.internal_unit()
            record["organizational_context"].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_record(record, self.root)

    def test_scaffolds_are_unverified_and_stdout_only_for_both_types(self):
        before = self.snapshot()
        category = load(self.company)["category_id"]
        for kind, extra in [("company", ["--category", category]), ("investor", [])]:
            draft = json.loads(self.invoke(SCAFFOLD, "--entity", kind, "--id", "synthetic-org", "--name", "合成研究候选", *extra))
            self.assertTrue(draft["draft"])
            self.assertIsNone(draft["record"]["checked_at"])
            self.assertEqual(draft["record"]["sources"], [])
            with self.assertRaises(ValueError):
                validate_record(draft["record"], self.root)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "workspace").exists())

    def test_scaffold_rejects_unknown_category_and_duplicate_identity(self):
        with self.assertRaises(ValueError):
            SCAFFOLD.make_draft(self.root, "company", "synthetic-org", "合成研究候选", "unknown-track")
        record = load(self.investor)
        with self.assertRaises(ValueError):
            SCAFFOLD.make_draft(self.root, "investor", "new-id", record["name"])

    def test_saved_draft_stays_private_and_never_overwrites(self):
        (self.root / "workspace").mkdir()
        args = ["--entity", "investor", "--id", "synthetic-org", "--name", "合成研究候选", "--save-draft"]
        before = self.snapshot()
        self.invoke(SCAFFOLD, *args)
        path = self.root / "workspace/drafts/research/investor-synthetic-org.json"
        self.assertTrue(load(path)["draft"])
        with self.assertRaises(FileExistsError):
            self.invoke(SCAFFOLD, *args)
        self.assertEqual(before, self.snapshot())

    def test_canonical_data_rejects_placeholder_facts_and_sources(self):
        for field, value in [("focus", "TODO: verify"), ("notes", "待填写来源")]:
            record = load(self.company)
            record[field] = value
            with self.assertRaises(ValueError):
                validate_record(record, self.root)
        record = load(self.company)
        record["sources"][0]["url"] = "https://example.com/research"
        with self.assertRaises(ValueError):
            validate_record(record, self.root)

    def test_merge_preview_does_not_write_and_apply_preserves_facts(self):
        original = load(self.company)
        before = self.snapshot()
        batch_path = self.write_batch(self.batch())
        preview = json.loads(self.invoke(MERGE, "--inbox-file", batch_path))
        self.assertTrue(preview["dry_run"])
        self.assertEqual(before, self.snapshot())
        applied = json.loads(self.invoke(MERGE, "--inbox-file", batch_path, "--apply"))
        self.assertFalse(applied["dry_run"])
        updated = load(self.company)
        self.assertEqual(updated["checked_at"], original["checked_at"])
        self.assertEqual(updated["contacts"], original["contacts"])
        self.assertEqual(updated["sources"][:-1], original["sources"])
        self.assertEqual(updated["channels"][0]["url"], "https://www.zhipin.com/gongsi/synthetic-id.html")
        self.assertEqual(updated["sources"][-1]["scope"], "channel")
        self.assertEqual(updated["channels"][0]["source_ids"], [updated["sources"][-1]["id"]])
        self.assertEqual(MERGE.plan_changes(self.batch(), self.root), {})

    def test_merge_uses_observation_date_without_refreshing_business_date(self):
        original = load(self.company)
        observed = self.entry()
        observed["checked_at"] = MERGE.today().isoformat()
        MERGE.apply_changes(MERGE.plan_changes(self.batch(observed), self.root))
        record = load(self.company)
        self.assertEqual(record["checked_at"], original["checked_at"])
        self.assertEqual(record["channels"][0]["checked_at"], observed["checked_at"])
        self.assertEqual(record["sources"][-1]["checked_at"], observed["checked_at"])
        self.assertEqual(validate_record(record, self.root), record)

    def test_merge_supports_investment_organizations(self):
        MERGE.apply_changes(MERGE.plan_changes(self.batch(self.entry(investor=True)), self.root))
        self.assertEqual(load(self.investor)["channels"][0]["owner"]["scope"], "organization")
        self.assertTrue(CHANNEL_AUDIT.has_platform(load(self.investor)))

    def test_merge_rejects_stale_observation(self):
        entry = self.entry()
        MERGE.apply_changes(MERGE.plan_changes(self.batch(entry), self.root))
        entry["checked_at"] = "2000-01-01"
        with self.assertRaisesRegex(ValueError, "Stale"):
            MERGE.plan_changes(self.batch(entry), self.root)

    def test_invalid_second_row_prevents_all_writes(self):
        bad = self.entry(investor=True)
        bad["observed_name"] = "Unrelated organization"
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.invoke(MERGE, "--inbox-file", self.write_batch(self.batch(self.entry(), bad)), "--apply")
        self.assertEqual(before, self.snapshot())

    def test_batch_rejects_private_fields_unverified_dates_and_unknown_ids(self):
        changes = [{"private_notes": "Synthetic private note"}, {"verification_status": "unverified"},
                   {"checked_at": "2999-01-01"}, {"entity_id": "missing-id"},
                   {"entity_id": "../hypershell"}, {"entity_type": "unknown"}]
        for change in changes:
            with self.subTest(change=change):
                entry = self.entry()
                entry.update(change)
                with self.assertRaises(ValueError):
                    MERGE.plan_changes(self.batch(entry), self.root)
        batch = self.batch()
        batch["public_only"] = False
        with self.assertRaises(ValueError):
            MERGE.plan_changes(batch, self.root)

    def test_platform_urls_require_real_platform_and_company_profile(self):
        invalid = ["https://zhipin.com.attacker.invalid/gongsi/id.html", "https://evilzhipin.com/gongsi/id.html",
                   "https://www.zhipin.com/job_detail/id.html", "https://www.zhipin.com/gongsi/",
                   "http://www.zhipin.com/gongsi/id.html", "https://www.zhipin.com/gongsi/%2e%2e/id",
                   "https://account@www.zhipin.com/gongsi/id.html"]
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(ValueError):
                platform_url(url, "boss_zhipin")
        self.assertEqual(platform_url("https://www.liepin.com/company/synthetic-id/?tracking=x", "liepin"),
                         "https://www.liepin.com/company/synthetic-id/")
        with self.assertRaises(ValueError):
            platform_url("https://www.liepin.com/company/synthetic-id/", "boss_zhipin")

    def test_linked_canonical_record_cannot_be_written(self):
        external = self.root.parent / "outside.json"
        external.write_bytes(self.company.read_bytes())
        self.company.unlink()
        self.company.symlink_to(external)
        with self.assertRaises(ValueError):
            MERGE.plan_changes(self.batch(self.entry()), self.root)
        with self.assertRaises(ValueError):
            record_path(self.root, "operating_organization", "../outside")

    def test_concurrent_edit_blocks_apply_without_overwriting_it(self):
        changes = MERGE.plan_changes(self.batch(), self.root)
        changed = self.company.read_bytes() + b"\n"
        self.company.write_bytes(changed)
        with self.assertRaises(ValueError):
            MERGE.apply_changes(changes)
        self.assertEqual(self.company.read_bytes(), changed)
        self.assertFalse(list(self.company.parent.glob("*.tmp")))

    def test_failed_batch_restores_earlier_applied_record(self):
        changes = MERGE.plan_changes(self.batch(self.entry(), self.entry(investor=True)), self.root)
        before = self.snapshot()
        replace = Path.replace

        def fail_second(path, target):
            if target.name == self.investor.name:
                raise OSError("Synthetic second-file failure")
            return replace(path, target)

        with patch.object(Path, "replace", new=fail_second), self.assertRaises(OSError):
            MERGE.apply_changes(changes)
        self.assertEqual(self.snapshot(), before)

    def test_rollback_preserves_external_edits_to_an_already_applied_record(self):
        changes = MERGE.plan_changes(self.batch(self.entry(), self.entry(investor=True)), self.root)
        replace = Path.replace
        external = {}

        def concurrent_replace(path, target):
            result = replace(path, target)
            # Simulate another writer modifying A and B after A is applied.
            if target.name == self.company.name:
                for record_path in changes:
                    external[record_path] = record_path.read_bytes() + b"\n"
                    record_path.write_bytes(external[record_path])
            return result

        with patch.object(Path, "replace", new=concurrent_replace), self.assertRaisesRegex(ValueError, "external edits were preserved"):
            MERGE.apply_changes(changes)
        for path, content in external.items():
            self.assertEqual(path.read_bytes(), content)

    def test_typed_coverage_does_not_infer_ownership_from_source_domains(self):
        record = load(self.company)
        record["sources"].append({"url": "https://github.com/third-party/research"})
        record["contacts"]["careers_url"] = self.entry()["url"]
        self.assertTrue(CHANNEL_AUDIT.legacy_platform_reference(record))
        for layer in ("official", "recruitment_platform", "professional_social"):
            self.assertFalse(CHANNEL_AUDIT.has_layer(record, layer))
        MERGE.apply_changes(MERGE.plan_changes(self.batch(), self.root))
        record = load(self.company)
        self.assertTrue(CHANNEL_AUDIT.has_platform(record))
        record["channels"][0]["verification_status"] = "historical"
        self.assertFalse(CHANNEL_AUDIT.has_platform(record))

    def test_collector_batches_are_neutral_nonoverlapping_and_unverified(self):
        first = json.loads(self.invoke(CHANNEL_AUDIT, "--wave", "all", "--offset", "0", "--limit", "2", "--template"))
        second = json.loads(self.invoke(CHANNEL_AUDIT, "--wave", "all", "--offset", "2", "--limit", "2", "--template"))
        self.assertFalse({e["entity_id"] for e in first["entries"]} & {e["entity_id"] for e in second["entries"]})
        self.assertEqual(len(first["entries"]) + len(second["entries"]), 4)
        with self.assertRaises(ValueError):
            MERGE.plan_changes(first, self.root)

    def test_channel_only_evidence_cannot_establish_targets_or_investment_cases(self):
        MERGE.apply_changes(MERGE.plan_changes(self.batch(self.entry(investor=True)), self.root))
        record = load(self.investor)
        channel_source = record["sources"][-1]["id"]
        changed = copy.deepcopy(record)
        changed["targeting"]["source_ids"] = [channel_source]
        with self.assertRaises(ValueError):
            validate_record(changed, self.root)
        record["representative_cases"][0]["evidence_source_ids"] = [channel_source]
        with self.assertRaises(ValueError):
            validate_record(record, self.root)


if __name__ == "__main__":
    unittest.main()
