"""Service descriptions must parse before they reach a HACS release."""
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "weltlage"


class ServiceDescriptionTests(unittest.TestCase):
    def test_all_component_yaml_is_parseable(self):
        for path in ROOT.rglob("*.yaml"):
            with self.subTest(path=path.relative_to(ROOT)):
                data = yaml.safe_load(path.read_text())
                self.assertIsInstance(data, dict)

    def test_legacy_service_fields_match_supported_choices(self):
        data = yaml.safe_load((ROOT / "services.yaml").read_text())
        self.assertEqual(set(data), {"fetch_intel"})
        fields = data["fetch_intel"]["fields"]
        self.assertIs(fields["kind"]["required"], True)
        self.assertEqual(fields["kind"]["selector"]["select"]["options"], ["flights", "satellites", "cameras"])
        self.assertEqual(fields["provider"]["selector"]["select"]["options"], ["london", "finland", "bc"])
        for field, low, high in [("latitude", -90, 90), ("longitude", -180, 180)]:
            self.assertEqual(fields[field]["selector"]["number"]["min"], low)
            self.assertEqual(fields[field]["selector"]["number"]["max"], high)


if __name__ == "__main__":
    unittest.main()
