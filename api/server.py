from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

API_KEY = os.environ.get("AVIATOR_API_KEY", "")

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(200, {
                "connected": bool(API_KEY),
                "status": "configured" if API_KEY else "waiting",
                "message": "Authorized data feed not connected yet."
            })
        elif self.path == "/api/test-round":
            self.send_json(200, {
                "test": True,
                "multiplier": 1.75,
                "message": "TEST DATA ONLY - not a real game round"
            })
        else:
            self.send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        return

port = int(os.environ.get("PORT", "3000"))
print(f"Aviator backend running on port {port}")
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
