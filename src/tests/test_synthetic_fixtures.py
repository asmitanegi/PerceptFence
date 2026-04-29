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


if __name__ == "__main__":
    unittest.main()
