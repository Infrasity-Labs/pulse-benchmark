"""Minimal REST helper so gates that need real JSON arrays can be satisfied.

The pi MCP bridge stringifies nested array params, which makes
record_requirement_lint unusable there (findings must be a native array or null,
and null always trips requirement_lint_score_findings_mismatch). This talks to
the SAME local server, so every gate still runs server-side.
"""
import json
import os
import sys
import urllib.error
import urllib.request

# Configuration is read from the environment:
#   PULSE_BASE_URL  REST root of the Okto Pulse server (default below)
#   PULSE_API_KEY   API key for the benchmark agent (required)
#   PULSE_BOARD_ID  id of the board the staged chain runs on (required)
BASE = os.environ.get("PULSE_BASE_URL", "http://127.0.0.1:8100/api/v1")


def api_key():
    key = os.environ.get("PULSE_API_KEY")
    if not key:
        sys.exit("PULSE_API_KEY is not set")
    return key


def call(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    # key is passed the same way the MCP client passes it
    sep = "&" if "?" in url else "?"
    req.full_url = f"{url}{sep}api_key={api_key()}"
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw or "{}")
        except Exception:
            return e.code, {"_nonjson": raw[:200]}


BOARD = os.environ.get("PULSE_BOARD_ID", "")

if __name__ == "__main__":
    if not BOARD:
        sys.exit("PULSE_BOARD_ID is not set")
    status, body = call("GET", f"/boards/{BOARD}/specs")
    print(status, json.dumps(body, indent=1)[:600])
