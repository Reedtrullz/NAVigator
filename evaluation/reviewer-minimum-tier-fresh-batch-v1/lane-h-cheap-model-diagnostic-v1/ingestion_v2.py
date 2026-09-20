#!/usr/bin/env python3
"""Ingestion V2 for the Lane H diagnostic tool: strict fence-only outer-json
handling and per-row model-facing input hashing (MODEL_FACING_TEXT_V2).

No span normalization, no JSON reconstruction, no repair of model content.
The validate() from the original run is imported unchanged.
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HASH_FORMAT = "MODEL_FACING_TEXT_V2"

# Exactly one outer markdown fence. The wrapper must start at the first
# non-whitespace byte and end at the last non-whitespace byte. Content that
# itself contains fences stays untouched; anything else fails closed as before.
FENCE_RE = re.compile(
    r"\A\s*```[A-Za-z0-9_-]*[ \t]*\r?\n(.*?)\r?\n?[ \t]*```\s*\Z",
    re.DOTALL,
)


def strip_outer_fence(raw):
    if not isinstance(raw, str):
        return raw, False
    m = FENCE_RE.match(raw)
    if not m:
        return raw, False
    return m.group(1), True


def parse_like_original(raw, fence_enabled):
    """Original ingestion was json.loads(raw); here optionally preceded by one
    strict outer-fence strip. Validation is NOT part of this function."""
    stripped, was_stripped = strip_outer_fence(raw) if fence_enabled else (raw, False)
    try:
        return json.loads(stripped), was_stripped, None
    except Exception as exc:
        return None, was_stripped, str(exc)


def model_input_hash_v2(system_prompt, user_prompt):
    payload = {"format": HASH_FORMAT, "system": system_prompt, "user": user_prompt}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def replay_results(results_path, rows_by_id, fence_enabled=True):
    """Replay stored raw responses through parse (+ unchanged validate).
    Returns summary and per-row dispositions. Read-only."""
    import run_diagnostic as base

    counts = {"OK": 0, "INVALID_JSON": 0, "INVALID_MODEL_REVIEW": 0,
              "OTHER": 0, "changed_vs_original_OK_rows": 0}
    dispositions = []
    with open(results_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec["row_id"]
            original = rec.get("status")
            if original not in ("OK", "INVALID_JSON", "INVALID_MODEL_REVIEW"):
                counts["OTHER"] += 1
                continue
            parsed, was_stripped, err = parse_like_original(rec.get("raw"), fence_enabled)
            if parsed is None:
                status, why = "INVALID_JSON", None
            else:
                ok, vwhy = base.validate(rows_by_id[rid], parsed)
                status, why = ("OK", None) if ok else ("INVALID_MODEL_REVIEW", vwhy)
            counts[status] += 1
            if original == "OK" and status != "OK":
                counts["changed_vs_original_OK_rows"] += 1
            if status != "OK":
                dispositions.append({"row_id": rid, "original_status": original,
                                     "replay_status": status,
                                     "fence_stripped": was_stripped,
                                     "reason": why or err})
    return counts, dispositions
