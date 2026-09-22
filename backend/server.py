"""Local-only HTTP API for the educational Bluetooth security lab."""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from simulator import list_scenarios, simulate

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

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._send(200, {"status": "ok", "safe_mode": True, "hardware_access": False})
        if path == "/api/scenarios":
            return self._send(200, {"scenarios": list_scenarios()})
        if path == "/api/docs":
            return self._send(200, {
                "safe_mode": True,
                "endpoints": {
                    "GET /api/health": "local service status",
                    "GET /api/scenarios": "available synthetic scenarios",
                    "POST /api/simulate": "generate a synthetic trace",
                },
                "request_example": {"scenario": "discovery_burst", "intensity": 5, "seed": 7},
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
        if urlparse(self.path).path != "/api/simulate":
            return self._send(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 4096:
                raise ValueError("request body is too large")
            data = json.loads(self.rfile.read(length) or b"{}")
            result = simulate(data.get("scenario", ""), int(data.get("intensity", 5)), int(data.get("seed", 7)))
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._send(400, {"error": str(exc)})
        return self._send(200, result)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[api] {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Bluetooth Security Lab running at http://127.0.0.1:{port} (safe simulation only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping lab")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
