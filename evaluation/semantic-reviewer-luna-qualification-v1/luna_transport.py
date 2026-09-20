#!/usr/bin/env python3
"""Shared frozen Luna transport path for all stages of this lineage.

Single serving route per candidate config (no provider hopping):
model gpt-5.6-luna via local proxy 127.0.0.1:10100, reasoning effort from
the frozen candidate config, json_object response format, max 1 technical
retry, fence-strip as the only parse fix class.
"""
import hashlib
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V1 = os.path.join(ROOT, "semantic-reviewer-cost-qualification-v1")
sys_v1 = os.path.normpath(V1)
import sys  # noqa: E402
if sys_v1 not in sys.path:
    sys.path.insert(0, sys_v1)

AUTH = os.path.join(os.path.expanduser("~"), ".codex", "auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-5.6-luna"
TIMEOUT = 600


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


def call_luna(effort, system_prompt, user_prompt, use_json_mode):
    """One call; returns (raw, elapsed, usage). Raises on transport error."""
    tok = json.load(open(AUTH))["tokens"]["access_token"]
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": user_prompt}],
        "reasoning_effort": effort,
    }
    if use_json_mode:
        payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        PROXY, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"})
    t0 = time.time()
    resp = json.load(urllib.request.urlopen(req, timeout=TIMEOUT))
    elapsed = round(time.time() - t0, 1)
    raw = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    return raw, elapsed, usage


def call_with_policy(effort, system_prompt, user_prompt):
    """Frozen retry/fix policy: 1 technical retry; json_object disabled on
    HTTP 400/422 (V1/V2 precedent); fence-strip parse fix (V2 precedent).
    Returns record fields without semantic interpretation."""
    attempts = []
    raw = elapsed = usage = err = None
    json_mode = True
    for attempt in (1, 2):
        try:
            raw, elapsed, usage = call_luna(effort, system_prompt,
                                            user_prompt, json_mode)
            err = None
            break
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode(errors="replace")[:300]
            except Exception:
                pass
            err = "HTTP_%d: %s" % (exc.code, body)
            attempts.append({"attempt": attempt, "error": err[:300]})
            if exc.code in (400, 422) and json_mode:
                json_mode = False
        except Exception as exc:
            err = type(exc).__name__ + ": " + str(exc)[:300]
            attempts.append({"attempt": attempt, "error": err[:300]})
        if attempt == 1 and err is not None:
            time.sleep(2)  # Astra runner precedent: brief pause before the single technical retry
    return {"attempts": attempts, "raw": raw, "elapsed_s": elapsed,
            "usage": usage, "error": err, "json_mode_final": json_mode}


def strip_fences(raw):
    s = raw.strip()
    fence = chr(96) * 3
    if s.startswith(fence):
        first_nl = s.find(chr(10))
        s = s[first_nl + 1:] if first_nl != -1 else s
        if s.rstrip().endswith(fence):
            s = s.rstrip()[:-3]
    return s.strip()


def request_config_hash(effort):
    return sha({"model": MODEL, "reasoning_effort": effort,
                "response_format": {"type": "json_object"},
                "retry_policy": "max1_technical",
                "parse_fix": "FENCE_STRIP_ONLY"})
