from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from screenshare_mediator import EXPECTED_SCENARIO_CLASSES, load_fixture_index, validate_fixture_set


class SyntheticFixtureTests(unittest.TestCase):
    def test_fixture_set_covers_all_expected_scenario_classes(self):
        repo_root = Path(__file__).resolve().parents[1]
        fixtures = load_fixture_index(repo_root)
        validate_fixture_set(fixtures)
        self.assertEqual(
            {fixture["scenario_class"] for fixture in fixtures},
            set(EXPECTED_SCENARIO_CLASSES),
        )

    def test_fixture_index_has_no_external_paths(self):
        repo_root = Path(__file__).resolve().parents[1]
        index_path = repo_root / "data" / "synthetic" / "index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        synthetic_root = index_path.parent.resolve()
        for entry in index["fixtures"]:
            candidate = (index_path.parent / entry["file"]).resolve()
            self.assertTrue(candidate.is_relative_to(synthetic_root))
            self.assertTrue(candidate.exists())

    def test_validate_fixture_set_rejects_missing_required_field(self):
        with self.assertRaises(ValueError) as ctx:
            validate_fixture_set([{
                "id": "x", "scenario_class": "terminal_secret", "modality": ["screen_text"],
                "synthetic": True, "input": {}, "expected_policy_action": "redact_before_model",
                # 'risk_label' missing
            }])
        self.assertIn("missing fields", str(ctx.exception))

    def test_validate_fixture_set_rejects_non_synthetic_flag(self):
        full = {
            "id": "x", "scenario_class": "terminal_secret", "modality": ["screen_text"],
            "synthetic": False, "risk_label": "test",
            "input": {}, "expected_policy_action": "redact_before_model",
        }
        with self.assertRaises(ValueError) as ctx:
            validate_fixture_set([full])
        self.assertIn("synthetic=true", str(ctx.exception))

    def test_validate_fixture_set_rejects_unknown_scenario_class(self):
        full = {
            "id": "x", "scenario_class": "not_a_real_class", "modality": ["screen_text"],
            "synthetic": True, "risk_label": "test",
            "input": {}, "expected_policy_action": "redact_before_model",
        }
        with self.assertRaises(ValueError) as ctx:
            validate_fixture_set([full])
        self.assertIn("unknown scenario_class", str(ctx.exception))

    def test_validate_fixture_set_rejects_coverage_shortfall(self):
        # One fixture, valid in itself, but coverage incomplete.
        full = {
            "id": "x", "scenario_class": "terminal_secret", "modality": ["screen_text"],
            "synthetic": True, "risk_label": "test",
            "input": {}, "expected_policy_action": "redact_before_model",
        }
        with self.assertRaises(ValueError) as ctx:
            validate_fixture_set([full])
        self.assertIn("scenario coverage mismatch", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
