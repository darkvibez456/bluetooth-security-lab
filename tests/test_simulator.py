import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from simulator import list_scenarios, simulate


class SimulatorTests(unittest.TestCase):
    def test_scenarios_are_available(self):
        self.assertEqual(
            {item["id"] for item in list_scenarios()},
            {"discovery_burst", "pairing_failures", "connection_churn"},
        )

    def test_trace_is_deterministic_and_hardware_free(self):
        first = simulate("discovery_burst", intensity=4, seed=11)
        second = simulate("discovery_burst", intensity=4, seed=11)
        self.assertEqual(first, second)
        self.assertTrue(first["safe_mode"])
        self.assertFalse(first["hardware_access"])
        self.assertTrue(all(event["synthetic_device"].startswith("SIM-") for event in first["events"]))

    def test_intensity_changes_event_count(self):
        self.assertLess(
            len(simulate("pairing_failures", 2)["events"]),
            len(simulate("pairing_failures", 8)["events"]),
        )

    def test_unknown_scenario_rejected(self):
        for scenario in ("", "real_device", "bluetooth_scan"):
            with self.assertRaises(ValueError):
                simulate(scenario)

    def test_intensity_bounds_rejected(self):
        with self.assertRaises(ValueError):
            simulate("connection_churn", intensity=0)
        with self.assertRaises(ValueError):
            simulate("connection_churn", intensity=11)


if __name__ == "__main__":
    unittest.main()
