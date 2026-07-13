import subprocess
import sys
import time

# Start the Flask server as a subprocess
proc = subprocess.Popen(
    [sys.executable, "api.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for the server to start
time.sleep(2)

import json
import urllib.request

endpoints = [
    ("GET", "http://localhost:3000/health"),
    ("GET", "http://localhost:3000/hello"),
    ("GET", "http://localhost:3000/supersquad"),
    ("GET", "http://localhost:3000/supername"),
]

for method, url in endpoints:
    print(f"\n--- {method} {url} ---")
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            print(f"Status: {resp.status}")
            print(f"Body:   {body}")
    except Exception as e:
        print(f"Error: {e}")

proc.terminate()
proc.wait()
print("\nAll tests done. Server stopped.")
