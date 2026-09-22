"""Local-only HTTP API for the educational Bluetooth security lab."""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from simulator import list_scenarios, simulate
from telemetry import SCANNER, TelemetryError, hardware_status

ROOT = Path(__file__).resolve().parent.parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: object, content_type: str = "application/json") -> None:
        body = json.dumps(payload).encode() if content_type == "application/json" else payload
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 4096:
            raise ValueError("request body is too large")
        data = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            status = hardware_status()
            return self._send(200, {
                "status": "ok",
                "safe_mode": True,
                "hardware_access": False,
                "hardware_discovery_available": status["available"],
                "message": "Hardware discovery is opt-in and read-only; simulation remains the default.",
            })
        if path == "/api/hardware/status":
            return self._send(200, hardware_status())
        if path == "/api/scenarios":
            return self._send(200, {"scenarios": list_scenarios()})
        if path == "/api/docs":
            return self._send(200, {
                "safe_mode": True,
                "endpoints": {
                    "GET /api/health": "local service and capability status",
                    "GET /api/hardware/status": "BlueZ availability and safety boundary",
                    "GET /api/scenarios": "available synthetic scenarios",
                    "POST /api/simulate": "generate a synthetic trace",
                    "POST /api/hardware/scan": "explicitly confirmed, time-limited read-only discovery",
                },
                "hardware_scan_request": {"confirm_authorized_scope": True, "duration_seconds": 10},
                "request_example": {"scenario": "pairing_failures", "intensity": 5, "seed": 7},
            })
        if path == "/":
            html = (ROOT / "frontend" / "index.html").read_bytes()
            return self._send(200, html, "text/html")
        if path == "/app.js":
            js = (ROOT / "frontend" / "app.js").read_bytes()
            return self._send(200, js, "text/javascript")
        if path == "/styles.css":
            css = (ROOT / "frontend" / "styles.css").read_bytes()
            return self._send(200, css, "text/css")
        return self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            data = self._json_body()
            if path == "/api/simulate":
                result = simulate(data.get("scenario", ""), int(data.get("intensity", 5)), int(data.get("seed", 7)))
                return self._send(200, result)
            if path == "/api/hardware/scan":
                if data.get("confirm_authorized_scope") is not True:
                    raise ValueError("confirm_authorized_scope must be true")
                result = SCANNER.scan(int(data.get("duration_seconds", 10)))
                return self._send(200, result)
        except TelemetryError as exc:
            return self._send(503, {"error": str(exc), "hardware": hardware_status()})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._send(400, {"error": str(exc)})
        return self._send(404, {"error": "not found"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[api] {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Bluetooth Security Lab running at http://127.0.0.1:{port} (simulation default; read-only BLE scan opt-in)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping lab")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
