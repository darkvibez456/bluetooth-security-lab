"""Optional, read-only BLE telemetry using the local BlueZ bluetoothctl client.

This module never accepts a target address, pairs, connects, sends packets, or
changes radio settings. It only parses discovery output from a time-limited
local scan and returns privacy-preserving records.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

DEVICE_RE = re.compile(r"Device\s+(?P<address>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})\s*(?P<name>.*)$")
RSSI_RE = re.compile(r"Device\s+(?P<address>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}).*RSSI:\s*(?P<rssi>-?\d+)")
MAX_SCAN_SECONDS = 20


class TelemetryError(RuntimeError):
    """A safe, user-facing scanner error."""


@dataclass(frozen=True)
class DeviceObservation:
    device_id: str
    name: str
    rssi: int | None
    address_type: str
    first_seen: str
    last_seen: str
    observation_count: int


class ReadOnlyScanner:
    def __init__(self) -> None:
        self._salt = os.urandom(16)

    @property
    def available(self) -> bool:
        return shutil.which("bluetoothctl") is not None

    def _privacy_id(self, address: str) -> str:
        digest = hashlib.sha256(self._salt + address.upper().encode()).hexdigest()[:8]
        return f"ble-{digest}"

    def scan(self, duration_seconds: int = 10) -> dict[str, Any]:
        if not isinstance(duration_seconds, int) or not 3 <= duration_seconds <= MAX_SCAN_SECONDS:
            raise TelemetryError(f"duration_seconds must be an integer from 3 to {MAX_SCAN_SECONDS}")
        if not self.available:
            raise TelemetryError("bluetoothctl is unavailable; install BlueZ to enable hardware discovery")

        command = ["timeout", f"{duration_seconds + 2}s", "bluetoothctl", "scan", "on"]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=duration_seconds + 5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise TelemetryError("The local Bluetooth scan could not be completed safely") from exc

        observations: dict[str, dict[str, Any]] = {}
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rssi_by_address: dict[str, int] = {}
        lines = (completed.stdout + "\n" + completed.stderr).splitlines()
        for raw_line in lines:
            rssi_match = RSSI_RE.search(raw_line)
            if rssi_match:
                rssi_by_address[rssi_match.group("address").upper()] = int(rssi_match.group("rssi"))
        for raw_line in lines:
            match = DEVICE_RE.search(raw_line)
            if not match:
                continue
            address = match.group("address").upper()
            name = match.group("name").strip() or "Unnamed device"
            # Never return or persist the real address.
            device_id = self._privacy_id(address)
            record = observations.get(device_id)
            if record is None:
                observations[device_id] = {
                    "device_id": device_id,
                    "name": name[:80],
                    "rssi": rssi_by_address.get(address),
                    "address_type": "masked",
                    "first_seen": now,
                    "last_seen": now,
                    "observation_count": 1,
                }
            else:
                record["last_seen"] = now
                record["observation_count"] += 1
                if name != "Unnamed device":
                    record["name"] = name[:80]
                if address in rssi_by_address:
                    record["rssi"] = rssi_by_address[address]

        return {
            "safe_mode": True,
            "hardware_access": True,
            "read_only": True,
            "duration_seconds": duration_seconds,
            "scanned_at": now,
            "device_count": len(observations),
            "privacy": {
                "identifiers": "ephemeral salted hashes",
                "real_addresses_returned": False,
                "raw_output_stored": False,
            },
            "devices": [asdict(DeviceObservation(**item)) for item in observations.values()],
            "notes": [
                "Discovery data is from the local adapter and may include nearby devices.",
                "Only scan devices you are authorized to monitor.",
                "No pairing, connection, packet transmission, or radio changes are performed.",
            ],
            "exit_code": completed.returncode,
        }


SCANNER = ReadOnlyScanner()


def hardware_status() -> dict[str, Any]:
    return {
        "available": SCANNER.available,
        "backend": "BlueZ bluetoothctl read-only discovery" if SCANNER.available else None,
        "default_mode": "simulation",
        "capabilities": ["time-limited discovery", "RSSI-ready telemetry", "privacy masking"] if SCANNER.available else [],
        "disabled_capabilities": ["pairing", "connections", "packet transmission", "jamming", "target selection"],
    }
