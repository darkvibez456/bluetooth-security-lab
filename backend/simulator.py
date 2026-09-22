"""Synthetic Bluetooth security lab; never touches a Bluetooth adapter or radio."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from random import Random
from typing import Any

SCENARIOS = {
    "discovery_burst": {
        "title": "Discovery burst",
        "description": "Synthetic advertisements arrive faster than a baseline consumer app expects.",
        "lesson": "Rate limiting and authenticated discovery policies reduce noisy observations.",
    },
    "pairing_failures": {
        "title": "Pairing failure wave",
        "description": "Synthetic pairing attempts fail repeatedly in a short observation window.",
        "lesson": "Backoff, user-visible alerts, and lockouts help contain repeated failures.",
    },
    "connection_churn": {
        "title": "Connection churn",
        "description": "Synthetic sessions connect and disconnect rapidly without contacting real devices.",
        "lesson": "Connection budgets, telemetry, and cleanup protect application resources.",
    },
}

@dataclass(frozen=True)
class Event:
    timestamp: int
    event_type: str
    synthetic_device: str
    severity: str
    message: str


def simulate(scenario: str, intensity: int = 5, seed: int = 7) -> dict[str, Any]:
    """Return a reproducible training trace. No hardware, sockets, or addresses are used."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    if not isinstance(intensity, int) or not 1 <= intensity <= 10:
        raise ValueError("intensity must be an integer from 1 to 10")

    rng = Random(seed)
    count = 4 + intensity * 2
    event_type = {
        "discovery_burst": "synthetic_advertisement",
        "pairing_failures": "pairing_failure",
        "connection_churn": "session_change",
    }[scenario]
    events: list[Event] = []
    for index in range(count):
        severity = "medium" if index < count * 0.65 else "high"
        device = f"SIM-{rng.randrange(1000, 9999):04d}"
        events.append(Event(
            timestamp=index + 1,
            event_type=event_type,
            synthetic_device=device,
            severity=severity,
            message=f"Training event {index + 1}: {SCENARIOS[scenario]['description']}",
        ))

    risk_score = min(100, 18 + intensity * 7 + (count // 3))
    return {
        "safe_mode": True,
        "hardware_access": False,
        "scenario": scenario,
        "scenario_title": SCENARIOS[scenario]["title"],
        "risk_score": risk_score,
        "recommended_controls": [
            "Apply per-device and per-application rate limits",
            "Record auditable events without storing real device identifiers",
            "Require explicit user approval for pairing",
            "Use exponential backoff after repeated failures",
        ],
        "lesson": SCENARIOS[scenario]["lesson"],
        "events": [asdict(event) for event in events],
    }


def list_scenarios() -> list[dict[str, str]]:
    return [{"id": key, **value} for key, value in SCENARIOS.items()]


if __name__ == "__main__":
    import json
    print(json.dumps(simulate("discovery_burst"), indent=2))
