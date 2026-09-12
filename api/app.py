import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json, hashlib


def get_user_count():
    try:
        with open("api/users.json","r",encoding="utf-8") as f:
            users=json.load(f)
        return len(users)
    except Exception:
        return 0

class Handler(SimpleHTTPRequestHandler):

        if self.path == "/api/admin-login":
            length=int(self.headers.get("Content-Length","0"))
            body=json.loads(self.rfile.read(length) or b"{}")
            pin=body.get("pin","")

            if pin != os.environ.get("AVIATOR_ADMIN_PIN",""):
                self.send_response(401)
                self.send_header("Content-Type","application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message":"Invalid admin PIN"
                }).encode())
                return

            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "authenticated":True
            }).encode())
            return


    def do_POST(self):
        if self.path == "/api/register":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")

            name = str(body.get("name", "")).strip()
            phone = str(body.get("phone", "")).strip()
            email = str(body.get("email", "")).strip().lower()
            password = str(body.get("password", ""))

            if not name or not phone or not email or len(password) < 6:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "Complete all fields. Password must be at least 6 characters."
                }).encode())
                return

            users_file = Path("api/users.json")
            users = json.loads(users_file.read_text() or "[]")

            if any(u["email"] == email for u in users):
                self.send_response(409)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "An account with this email already exists."
                }).encode())
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            users.append({
                "name": name,
                "phone": phone,
                "email": email,
                "password_hash": password_hash
            })

            users_file.write_text(json.dumps(users, indent=2))

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Account created successfully."
            }).encode())
            return

    def do_POST(self):
        if self.path == "/api/login":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")

            email = str(body.get("email", "")).strip().lower()
            password = str(body.get("password", ""))

            users_file = Path("api/users.json")
            users = json.loads(users_file.read_text() or "[]")

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            user = next(
                (u for u in users
                 if u["email"] == email
                 and u["password_hash"] == password_hash),
                None
            )

            if not user:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "Invalid email or password."
                }).encode())
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "name": user["name"],
                    "phone": user["phone"],
                    "email": user["email"]
                }
            }).encode())
            return

    def do_GET(self):


        if self.path == "/api/admin-users":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                with open("api/users.json","r",encoding="utf-8") as f:
                    users=json.load(f)

                safe_users=[
                    {
                        "name":u.get("name",""),
                        "phone":u.get("phone",""),
                        "email":u.get("email","")
                    }
                    for u in users
                ]

                self.wfile.write(json.dumps({
                    "users":safe_users
                }).encode())

            except Exception:
                self.wfile.write(json.dumps({
                    "users":[]
                }).encode())

            return

        if self.path == "/api/admin-stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "users": get_user_count(),
                "status": "online"
            }).encode())
            return

        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "connected": bool(os.environ.get("AVIATOR_API_KEY")),
                "status": "connected" if os.environ.get("AVIATOR_API_KEY") else "waiting",
                "message": "Authorized live data source required"
            }).encode())
            return
        super().do_GET()

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
port = int(os.environ.get("PORT", 8000))
print(f"Aviator Analyzer running on port {port}")
ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
