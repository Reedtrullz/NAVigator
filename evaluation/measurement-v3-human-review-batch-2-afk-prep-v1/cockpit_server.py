#!/usr/bin/env python3
"""Local OWNER-01 review cockpit for Batch 2 (mechanical support only).

Bindings: 127.0.0.1 only, stdlib only, no model calls. Reads frozen
Batch 2 packets read-only; persists OWNER-01 draft reviews atomically to
owner-reviews-draft.jsonl in THIS prep lineage (never in the authoritative
batch directory). Evidence spans are only re-encodied with the frozen
batch-1 span_tool convention and checked verbatim; no semantic assistance.
"""
import json, os, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
BATCH = os.path.join(EVAL, "measurement-v3-human-review-batch-2-repaired")
BATCH1 = os.path.join(EVAL, "measurement-v3-human-review-batch-1")
sys.path.insert(0, HERE)
sys.path.insert(0, BATCH1)
import prep_lib as P
import span_tool

DRAFT = os.path.join(HERE, "owner-reviews-draft.jsonl")
HTML = os.path.join(HERE, "review-cockpit.html")
LOCK = threading.Lock()


def make_chunks(order, dims):
    crit = [pid for pid in order if dims[pid] == "critical_condition"]
    forb = [pid for pid in order if dims[pid] == "forbidden_claim"]
    out = []
    def add(name, ids):
        if ids:
            out.append({"chunk": name, "packet_ids": ids})
    if len(crit) >= 3:
        add("critical 1-3 (pilot)", crit[:3])
        add("critical 4-10", crit[3:])
    else:
        add("critical", crit)
    for i in range(0, len(forb), 10):
        add("forbidden " + str(i + 1) + "-" + str(min(i + 10, len(forb))), forb[i:i + 10])
    return out


def read_draft():
    rows = []
    if os.path.exists(DRAFT):
        with open(DRAFT, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def write_draft_atomic(rows):
    tmp = DRAFT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + chr(10))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DRAFT)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(HTML, "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
            return
        if self.path == "/api/state":
            packets = P.load_packets()
            order = P.load_order()
            by_id = {p["packet_id"]: p for p in packets}
            dims = {p["packet_id"]: p["dimension"] for p in packets}
            view = []
            for i, pid in enumerate(order, 1):
                p = by_id[pid]
                view.append({"pos": i, "packet_id": pid, "case_id": p["case_id"],
                             "dimension": p["dimension"], "criterion": p["criterion"],
                             "case_context": p["case_context"],
                             "reviewer_instructions": p["reviewer_instructions"],
                             "packet_sha256": p["packet_sha256"],
                             "contract_version": p["contract_version"],
                             "sut_output": p["sut_output"]})
            draft = {r["packet_id"]: r for r in read_draft()}
            self._send(200, {"packets": view, "chunks": make_chunks(order, dims),
                             "enums": P.ENUMS, "draft": draft, "reviewer_id": P.REVIEWER_ID})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 2000000:
            self._send(413, {"errors": ["payload too large"]})
            return
        try:
            req = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception as e:
            self._send(400, {"errors": ["invalid JSON: " + str(e)[:120]]})
            return
        if self.path == "/api/spancheck":
            packets = {p["packet_id"]: p for p in P.load_packets()}
            p = packets.get(req.get("packet_id"))
            if p is None:
                self._send(400, {"errors": ["unknown packet_id"]})
                return
            spans = req.get("spans")
            if not isinstance(spans, list) or not all(isinstance(s, str) for s in spans):
                self._send(400, {"errors": ["spans must be a list of strings"]})
                return
            self._send(200, {"results": span_tool.map_packet(p, spans)})
            return
        if self.path in ("/api/save", "/api/delete"):
            packets = P.load_packets()
            by_id = {p["packet_id"]: p for p in packets}
            with LOCK:
                rows = read_draft()
                if self.path == "/api/delete":
                    pid = req.get("packet_id")
                    if pid in by_id:
                        rows = [r for r in rows if r.get("packet_id") != pid]
                        write_draft_atomic(rows)
                        self._send(200, {"ok": True, "removed": pid})
                    else:
                        self._send(400, {"errors": ["unknown packet_id"]})
                    return
                row = req.get("row")
                p0 = by_id.get(row.get("packet_id")) if isinstance(row, dict) else None
                if p0 is None:
                    self._send(400, {"errors": ["unknown packet_id in row"]})
                    return
                # mechanical re-encoding only: reviewer-copied display text ->
                # raw JSON encoding, same frozen convention as batch-1 prepare
                spans = (row.get("judgment") or {}).get("evidence_spans") or []
                mapped = span_tool.map_packet(p0, spans)
                bad = [m for m in mapped if m.get("status") != "ok"]
                if bad:
                    self._send(400, {"errors": [
                        "evidence span not mappable (copy exactly from the SUT answer): "
                        + str((b.get("reason") or "")[:120]) for b in bad]})
                    return
                row["judgment"]["evidence_spans"] = [m["raw"] for m in mapped]
                errs = P.validate_review_row(row, by_id, set())
                if errs:
                    self._send(400, {"errors": errs})
                    return
                pid = row["packet_id"]
                rows = [r for r in rows if r.get("packet_id") != pid] + [row]
                rows.sort(key=lambda r: r["packet_id"])
                write_draft_atomic(rows)
                self._send(200, {"ok": True, "packet_id": pid, "saved_rows": len(rows)})
            return
        self._send(404, {"error": "not found"})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Cockpit: http://127.0.0.1:" + str(port) + "  (Ctrl-C to stop)")
    print("Draft reviews: " + DRAFT)
    srv.serve_forever()


if __name__ == "__main__":
    main()
