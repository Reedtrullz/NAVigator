#!/usr/bin/env python3
"""Minimal native TypeSafe System One client for the Jev qualification experiment.

Reads TYPESAFE_API_KEY from environment or .env.local. The key is never printed,
hashed, logged, or persisted by this module.
"""
import json, os, pathlib, time, urllib.request, urllib.error

API_URL = "https://api.typesafe.ai/v1/systemone"

def load_api_key():
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    env_local = pathlib.Path(__file__).resolve().parent.parent.parent / ".env.local"
    if env_local.exists():
        for line in env_local.read_text().splitlines():
            if line.startswith("TYPESAFE_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    raise RuntimeError("TYPESAFE_API_KEY not found in environment or .env.local")

def system_one(state, questions, model="jev-latest", timeout=120):
    payload = {"state": state, "model": model, "questions": questions}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body, method="POST",
        headers={
            "Authorization": "Bearer " + load_api_key(),
            "Content-Type": "application/json",
        })
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, time.monotonic() - t0
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:2000]
        return {"http_error": e.code, "error_body": detail, "model": model}, time.monotonic() - t0
    except Exception as e:
        return {"transport_error": type(e).__name__ + ": " + str(e)[:500], "model": model}, time.monotonic() - t0
