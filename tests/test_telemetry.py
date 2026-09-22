import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from telemetry import ReadOnlyScanner, TelemetryError


class TelemetryTests(unittest.TestCase):
    def test_identifiers_are_privacy_masked(self):
        scanner = ReadOnlyScanner()
        self.assertTrue(scanner._privacy_id("AA:BB:CC:DD:EE:FF").startswith("ble-"))
        self.assertNotIn("AA:BB", scanner._privacy_id("AA:BB:CC:DD:EE:FF"))

    def test_duration_is_bounded(self):
        scanner = ReadOnlyScanner()
        with patch("telemetry.shutil.which", return_value="/usr/bin/bluetoothctl"):
            with self.assertRaises(TelemetryError):
                scanner.scan(30)

    def test_scan_parses_without_returning_addresses(self):
        scanner = ReadOnlyScanner()
        fake = type("Completed", (), {
            "stdout": "[NEW] Device AA:BB:CC:DD:EE:FF Classroom Sensor\n",
            "stderr": "",
            "returncode": 0,
        })()
        with patch("telemetry.shutil.which", return_value="/usr/bin/bluetoothctl"), patch("telemetry.subprocess.run", return_value=fake):
            result = scanner.scan(3)
        self.assertEqual(result["device_count"], 1)
        self.assertFalse(result["privacy"]["real_addresses_returned"])
        self.assertNotIn("AA:BB:CC:DD:EE:FF", str(result))
        self.assertEqual(result["devices"][0]["name"], "Classroom Sensor")


if __name__ == "__main__":
    unittest.main()
