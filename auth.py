from dotenv import load_dotenv
import os
import requests
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import webbrowser

load_dotenv()

CLIENT_ID = os.getenv("C_ID")
CLIENT_SECRET = os.getenv("C_SECRET")
TENANT_ID = os.getenv("T_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8080"
SCOPES = ["Mail.Read", "User.Read", "profile openid email"]


auth_code = None

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        auth_code = query.get('code', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Authorization code received. You can close this tab.</h1>')

        print(f"\nAuthorization Code received:\n{auth_code}")

def start_local_server():
    server = HTTPServer(('localhost', 8080), AuthHandler)
    print("Waiting for authorization code at: http://localhost:8000")
    server.handle_request()

def acquire_token():
    global auth_code

    auth_url = (
    f"{AUTHORITY}/oauth2/v2.0/authorize?"
    f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&response_mode=query&scope={' '.join(SCOPES)}&state=12345"
    )

    threading.Thread(target=start_local_server, daemon=True).start()
    webbrowser.open(auth_url)

    while auth_code is None:
        pass

    token_url = f"{AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": " ".join(SCOPES),
    }

    response = requests.post(token_url, data=data)
    result = response.json()

    if "access_token" in result:
        print("Access token acquired.")
        return result["access_token"]
    else:
        raise Exception("Failed to acquire token:\n" + str(result))
