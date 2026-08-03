"""End-to-end tests for the Task API.

Starts a uvicorn server in a subprocess, checks every endpoint against its
expected status code, and exits non-zero if any check fails.
"""

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

PORT = 8100
BASE = f"http://localhost:{PORT}"

# Start the server as a subprocess (api.py has no __main__ block, so
# launch it through uvicorn explicitly)
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api:app", "--port", str(PORT)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)


def wait_for_server(url, timeout=15):
    """Poll the health endpoint until the server is ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise SystemExit("Server did not start in time")


def request(method, path, body=None):
    """Perform a request and return (status_code, body)."""
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# (method, path, expected status, request body or None)
tests = [
    # info & health
    ("GET", "/", 200, None),
    ("GET", "/health", 200, None),
    # read
    ("GET", "/tasks", 200, None),
    ("GET", "/tasks?done=true", 200, None),
    ("GET", "/tasks?search=groceries", 200, None),
    ("GET", "/tasks/stats", 200, None),
    ("GET", "/tasks/1", 200, None),
    ("GET", "/tasks/99", 404, None),
    # create
    ("POST", "/tasks", 201, {"title": "Write a test"}),
    ("POST", "/tasks", 422, {"title": ""}),
    ("POST", "/tasks", 422, {"title": "   "}),
    # update
    ("PUT", "/tasks/1", 200, {"done": True}),
    ("PUT", "/tasks/99", 404, {"done": True}),
    # delete (seed task 3 is removed by the first call, then gone)
    ("DELETE", "/tasks/3", 204, None),
    ("DELETE", "/tasks/3", 404, None),
    ("DELETE", "/tasks/99", 404, None),
]

wait_for_server(BASE + "/health")

failed = 0
for method, path, expected, body in tests:
    status, resp_body = request(method, path, body)
    ok = status == expected
    if not ok:
        failed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {method:6} {path:35} -> {status} (expected {expected})")
    if resp_body and not ok:
        print(f"        body: {resp_body.decode()[:200]}")

proc.terminate()
proc.wait()
print(f"\n{len(tests) - failed}/{len(tests)} tests passed.")
sys.exit(1 if failed else 0)
