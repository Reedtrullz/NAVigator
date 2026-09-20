#!/usr/bin/env python3
"""Mechanical evidence-span mapping for review batch 1 (v2 presentation layer).

The v2 workbook shows the parsed SUT answer and structured claims. The frozen
lane validates evidence spans verbatim against the RAW sut_output JSON string.
This tool converts spans copied from the v2 workbook (block C or D) into the
exact raw encoding, deterministically, with fail-closed behavior.

It performs NO semantic work: it only re-encodes text the reviewer copied.
If a span cannot be located byte-exactly, it is reported as not_found and
nothing is fabricated.

Usage:
  span_tool.py map            < packets.json   (one JSON object per line:
                              {"packet_id": ..., "spans": [...]})
  span_tool.py prepare IN.jsonl OUT.jsonl      (filled v2 form -> ingest file)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(HERE), "measurement-v3-burned-baseline-v1")


def load_packets():
    out = {}
    with open(os.path.join(BASE, "human-review-packets.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                out[p["packet_id"]] = p
    return out


def string_regions(raw, key):
    """Return raw-substring regions (start, end) for a top-level JSON string
    value, or for each element of a top-level JSON array of strings."""
    idx = raw.find('"' + key + '"')
    if idx < 0:
        return []
    colon = raw.find(':', idx + len(key) + 2)
    if colon < 0:
        return []
    j = colon + 1
    while raw[j] in ' \t\r\n':
        j += 1
    if raw[j] == '[':
        # array of strings
        k = raw.index('[', j)
        regions = []
        depth_scan = k + 1
        while True:
            while raw[depth_scan] in ' \t\r\n,':
                depth_scan += 1
            if raw[depth_scan] == ']':
                break
            assert raw[depth_scan] == '"', "non-string array element"
            start = depth_scan
            depth_scan += 1
            while True:
                if raw[depth_scan] == '\\':
                    depth_scan += 2
                    continue
                if raw[depth_scan] == '"':
                    break
                depth_scan += 1
            regions.append((start, depth_scan + 1))
            depth_scan += 1
        return regions
    if raw[j] != '"':
        return []
    k = j + 1
    while True:
        if raw[k] == '\\':
            k += 2
            continue
        if raw[k] == '"':
            break
        k += 1
    return [(j, k + 1)]


def decode_region_map(raw, start, end):
    """Decode a raw JSON string region into text plus a per-char map
    [ (raw_start, raw_end) ] aligned to decoded characters."""
    region = raw[start:end]
    text = json.loads(region)
    i = start + 1
    charmap = []
    out = []
    while raw[i] != '"':
        rs = i
        if raw[i] == '\\':
            esc = raw[i + 1]
            if esc == 'u':
                i += 6
            else:
                i += 2
        else:
            i += 1
        charmap.append((rs, i))
        out.append(True)
    assert len(charmap) == len(text)
    return text, charmap


def map_span(raw, regions, span):
    """Try to locate span inside any region; return raw-encoded span or None."""
    for start, end in regions:
        text, charmap = decode_region_map(raw, start, end)
        pos = text.find(span)
        if pos < 0:
            continue
        rs = charmap[pos][0]
        re_ = charmap[pos + len(span) - 1][1]
        return raw[rs:re_]
    return None


def map_packet(packet, spans):
    raw = packet["sut_output"]
    d = json.loads(raw)
    has_answer = isinstance(d.get("answer"), str)
    has_claims = isinstance(d.get("claims"), list) and all(isinstance(x, str) for x in d.get("claims", []))
    answer_regions = string_regions(raw, "answer") if has_answer else []
    claims_regions = string_regions(raw, "claims") if has_claims else []
    out = []
    for s in spans:
        if not isinstance(s, str) or not s.strip():
            out.append({"input": s, "raw": None, "status": "not_found",
                        "reason": "empty or non-string span"})
            continue
        candidates = []
        raw_span = map_span(raw, answer_regions, s)
        if raw_span is not None:
            candidates.append(raw_span)
        raw_span = map_span(raw, claims_regions, s)
        if raw_span is not None:
            candidates.append(raw_span)
        if s in raw:
            candidates.append(s)  # already raw-safe (copied from appendix)
        if candidates:
            out.append({"input": s, "raw": candidates[0], "status": "ok",
                        "identical_in_raw": candidates[0] == s})
        else:
            out.append({"input": s, "raw": None, "status": "not_found",
                        "reason": "span not byte-locatable in answer/claims; copy exactly from block C/D or appendix"})
    return out


def cmd_map(stream):
    packets = load_packets()
    for line in stream:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        p = packets.get(req["packet_id"])
        if p is None:
            print(json.dumps({"packet_id": req["packet_id"], "error": "unknown packet_id"}))
            continue
        results = map_packet(p, req.get("spans", []))
        print(json.dumps({"packet_id": req["packet_id"], "spans": results}, ensure_ascii=False))


def cmd_prepare(inp, outp):
    packets = load_packets()
    written, skipped_empty, errors = 0, 0, []
    with open(inp, encoding="utf-8") as f, open(outp, "w", encoding="utf-8") as out:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            j = r.get("judgment", {})
            pid = r.get("packet_id")
            p = packets.get(pid)
            if p is None:
                errors.append({"packet_id": pid, "reason": "unknown packet_id"})
                continue
            spans = j.get("evidence_spans", [])
            filled = any(j.get(k) for k in ("criterion_semantic_match", "speaker_commitment",
                                            "critical_evidence_state")) or bool(spans) or j.get("note")
            if not filled:
                skipped_empty += 1
                continue
            mapped = map_packet(p, spans)
            bad = [m for m in mapped if m["status"] != "ok"]
            if bad:
                errors.append({"packet_id": pid,
                               "reason": "evidence span not mappable",
                               "detail": bad})
                continue
            clean = {"evidence_spans": [m["raw"] for m in mapped]}
            if p["dimension"] == "critical_condition":
                clean["critical_evidence_state"] = j.get("critical_evidence_state")
            else:
                clean["criterion_semantic_match"] = j.get("criterion_semantic_match")
                clean["speaker_commitment"] = j.get("speaker_commitment")
            clean["note"] = j.get("note", "")
            import datetime
            rec = {"packet_id": pid, "packet_sha256": p["packet_sha256"],
                   "reviewer_id": r.get("reviewer_id"), "contract_version": p["contract_version"],
                   "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "judgment": clean}
            out.write(json.dumps(rec, ensure_ascii=False) + chr(10))
            written += 1
    print(json.dumps({"written": written, "skipped_empty": skipped_empty,
                      "errors": errors}, ensure_ascii=False))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "map":
        cmd_map(sys.stdin)
    elif len(sys.argv) >= 4 and sys.argv[1] == "prepare":
        cmd_prepare(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(__doc__)
