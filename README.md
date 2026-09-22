# Bluetooth Security Lab

> **Educational and defensive use only.** This project is a synthetic simulator. It does not scan for Bluetooth devices, connect to them, send packets, jam radio signals, perform denial-of-service actions, or accept real target addresses.

Bluetooth Security Lab is a small local web application for learning how defensive telemetry and controls can be discussed without interacting with live radio hardware. It generates reproducible mock events for three classroom scenarios: discovery bursts, repeated pairing failures, and connection churn. Every identifier begins with `SIM-`, and the backend intentionally uses only Python's standard library.

## Why this is different

The reference project is a command-line script that invokes a Bluetooth utility against a supplied address and launches threads. This project uses a separate architecture: a dependency-free local HTTP API, a pure simulation engine, and a browser interface. There is no Bluetooth adapter dependency, no shell execution, no device-address input, and no operational attack routine.

## Run locally

```bash
python3 backend/server.py
# open http://127.0.0.1:8080
```

The server binds to loopback only. To run the tests:

```bash
python3 -m pytest -q
```

## Learning goals

- Recognize noisy or repeated event patterns in synthetic telemetry.
- Compare controls such as rate limiting, backoff, approval gates, and audit logging.
- Practice explaining risk without targeting real devices or networks.
- Build classroom exercises around generated data rather than live attack tooling.

## Safety and responsible disclosure

Use this repository only in a classroom, lab, or authorized defensive setting. Do not add Bluetooth scanning, packet injection, radio interference, target selection, or disruption logic. If you discover a real Bluetooth vulnerability, stop testing and follow the affected vendor's coordinated vulnerability disclosure process.

## License

MIT. See [LICENSE](LICENSE).
