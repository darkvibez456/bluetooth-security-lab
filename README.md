# Bluetooth Security Lab

<p align="center">
  <strong>A safe, local-only simulator for learning Bluetooth defensive telemetry</strong>
</p>

> **Educational and defensive use only.** This repository does **not** scan for Bluetooth devices, connect to them, send packets, jam radio signals, perform denial-of-service actions, or accept real target addresses. All device identifiers are synthetic and begin with `SIM-`.

[![Safety: synthetic only](https://img.shields.io/badge/safety-synthetic--only-16a34a)](#safety-boundary)
[![Python: standard library](https://img.shields.io/badge/python-standard%20library-3776ab)](#requirements)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 1. What this project does

Bluetooth Security Lab is a small browser application for discussing **defensive signals** without touching live radio hardware. It creates reproducible mock telemetry for three classroom scenarios:

1. **Discovery burst** — synthetic advertisements arrive faster than a normal baseline.
2. **Pairing failure wave** — repeated synthetic pairing attempts fail in a short window.
3. **Connection churn** — synthetic sessions connect and disconnect rapidly.

The application turns those events into a simple risk score and suggests controls such as rate limiting, user approval, audit logging, and exponential backoff.

## 2. Why the architecture is different

The reference-style attack scripts in this area usually accept a device address and invoke operating-system Bluetooth utilities. This project intentionally takes a different path:

| Layer | Implementation | Safety property |
|---|---|---|
| Simulation engine | `backend/simulator.py` | Generates only in-memory synthetic events |
| HTTP backend | `backend/server.py` | Python standard library; loopback-only by default |
| Browser UI | `frontend/` | Displays telemetry and defensive lessons |
| Tests | `tests/` | Validates determinism, bounds, and hardware-free behavior |

There is no Bluetooth adapter dependency, no shell command execution, no packet routine, no thread-flooding routine, and no real address input.

## 3. Requirements

- Python **3.10 or newer**
- A modern browser
- No Bluetooth adapter required
- No third-party Python packages required

Check your Python version:

```bash
python3 --version
```

## 4. Install and run — step by step

### Step 1: Clone the repository

```bash
git clone https://github.com/darkvibez456/bluetooth-security-lab.git
cd bluetooth-security-lab
```

### Step 2: Start the local backend

```bash
python3 backend/server.py
```

You should see:

```text
Bluetooth Security Lab running at http://127.0.0.1:8080 (safe simulation only)
```

The server listens on `127.0.0.1` so it is available only on your own computer. Keep this terminal open.

### Step 3: Open the dashboard

Open **http://127.0.0.1:8080** in your browser.

### Step 4: Generate a training trace

1. Choose a scenario from the dropdown.
2. Move the intensity slider from 1 to 10.
3. Click **Generate synthetic trace**.
4. Read the risk score, recommended controls, and event stream.
5. Explain which control would reduce the observed signal and why.

### Step 5: Stop the server

Return to the terminal running the server and press:

```text
Ctrl+C
```

## 5. How to read the dashboard

- **Safe simulation badge:** Confirms the result came from synthetic data.
- **Risk score:** A teaching aid from 0–100, not a real-world security verdict.
- **Recommended controls:** Defensive ideas to discuss or implement in a real product.
- **Synthetic event stream:** Each row uses a generated `SIM-####` identifier and contains no real device data.
- **Scenario lesson:** A short explanation of the defensive concept represented by the trace.

## 6. API usage for learners

The backend exposes a small JSON API. These examples are safe because they operate on generated data only.

### Health check

```bash
curl http://127.0.0.1:8080/api/health
```

Expected fields include `"safe_mode": true` and `"hardware_access": false`.

### List scenarios

```bash
curl http://127.0.0.1:8080/api/scenarios
```

### Generate a deterministic trace

```bash
curl -X POST http://127.0.0.1:8080/api/simulate \
  -H 'Content-Type: application/json' \
  -d '{"scenario":"pairing_failures","intensity":6,"seed":42}'
```

Valid scenarios are `discovery_burst`, `pairing_failures`, and `connection_churn`. Intensity must be an integer from `1` to `10`. The optional seed makes a trace reproducible for classroom exercises.

### Change the local port

The default port is `8080`. To use another local port:

```bash
PORT=9090 python3 backend/server.py
```

The server still binds to loopback (`127.0.0.1`).

## 7. Tool ka use — kya, kab, aur kyun?

Yeh project **attack tool nahi** hai. Iska purpose defensive learning hai: synthetic events generate karke dekhna ki noisy behavior ko kaise observe, score, aur control kiya ja sakta hai.

| Tool / component | Kis kaam ke liye hai | Example |
|---|---|---|
| `backend/server.py` | Local web server aur JSON API start karne ke liye | `python3 backend/server.py` |
| Browser dashboard | Scenario choose karke visual trace dekhne ke liye | `http://127.0.0.1:8080` |
| `backend/simulator.py` | Reproducible synthetic events aur risk score banane ke liye | `python3 backend/simulator.py` |
| `/api/health` | Check karne ke liye ki server safe mode mein running hai | `curl http://127.0.0.1:8080/api/health` |
| `/api/scenarios` | Available classroom scenarios list karne ke liye | `curl http://127.0.0.1:8080/api/scenarios` |
| `/api/simulate` | Programmatically synthetic trace generate karne ke liye | `curl -X POST ...` |
| `/api/docs` | API endpoints aur request format samajhne ke liye | `curl http://127.0.0.1:8080/api/docs` |
| `tests/` | Code safe aur predictable hai ya nahi verify karne ke liye | `python3 -m unittest discover -s tests -v` |

### Recommended learning workflow

1. Server start karein: `python3 backend/server.py`.
2. Browser dashboard open karein.
3. Pehle `discovery_burst` ko intensity `2` par run karein.
4. Phir wahi scenario intensity `8` par run karke event count aur risk score compare karein.
5. `pairing_failures` scenario run karke **backoff**, **approval gate**, aur **alerting** jaise controls discuss karein.
6. `connection_churn` scenario run karke resource cleanup aur connection budgets par notes banayein.
7. Same `seed` ke saath API request repeat karke reproducibility verify karein.

### Kis kaam ke liye use nahi karna hai

Is project ko real device scan karne, kisi Bluetooth address ko target karne, packets bhejne, radio interfere karne, pairing force karne, ya kisi device/service ko disrupt karne ke liye use nahi kiya ja sakta aur nahi kiya jana chahiye. Real-world testing ke liye written authorization, isolated lab, aur vendor disclosure process zaroori hai.

## 8. Run the tests

The test suite uses only Python's standard library:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q backend tests
```

The tests verify that scenarios are present, traces are deterministic, intensity bounds are enforced, and generated identifiers remain synthetic.

## 9. Suggested classroom exercises

1. Generate the same scenario twice with the same seed. What stays constant?
2. Increase intensity from 2 to 9. Which metrics change?
3. Map each recommended control to a prevention, detection, or response category.
4. Design a dashboard alert rule using only the synthetic event fields.
5. Discuss what additional privacy controls would be needed before logging real device telemetry.

## 10. Safety boundary

Do not extend this project with Bluetooth scanning, pairing automation, packet injection, radio interference, target selection, disruption logic, or instructions for impacting devices. If you are studying a real Bluetooth security issue, use an isolated lab, obtain authorization, minimize collection, and follow the affected vendor's coordinated vulnerability disclosure process.

This project is a **simulation and teaching aid**, not a penetration-testing tool and not evidence that a real device is vulnerable.

## 11. Project structure

```text
bluetooth-security-lab/
├── backend/
│   ├── server.py          # local HTTP API and static-file server
│   └── simulator.py       # deterministic synthetic event engine
├── frontend/
│   ├── index.html         # dashboard markup
│   ├── app.js             # API calls and rendering
│   └── styles.css         # responsive visual design
├── tests/
│   └── test_simulator.py  # standard-library unit tests
├── docs/
│   └── threat-model.md    # scope and out-of-scope behavior
├── LICENSE
└── README.md
```

## 12. License

MIT. See [LICENSE](LICENSE).
