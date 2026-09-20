#!/usr/bin/env python3
"""Shared dual-pass annotator (spec 14/17/22/23).

Both passes run this same script with different --tag/--out arguments.
Each request sends: contract verbatim + schema + exactly one case.
No pass ever sees the other pass's output or any prior labels.
Outputs are schema-validated; failures are retried, then recorded as
SCHEMA_FAILURE (spec 25) rather than disagreement.
"""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "command-code/gpt-5.6-luna"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def call_case(contract, schema_str, case):
    user = json.dumps({"case": case}, ensure_ascii=False)
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             contract + "\n\nJSON SCHEMA (validate strictly):\n"
             + schema_str},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(
        PROXY, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"].strip()
    tick = chr(96)
    if text.startswith(tick):
        text = text.strip(tick)
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    import jsonschema
    contract = (HERE / "annotation-contract-v3.md").read_text(
        encoding="utf-8")
    schema_path = HERE / "annotation-contract-v3.schema.json"
    schema_str = schema_path.read_text(encoding="utf-8")
    schema = json.loads(schema_str)
    pub = json.loads(Path(args.cases).read_text(encoding="utf-8"))

    annotations = {}
    schema_failures = []
    cases = pub["cases"]
    for i, case in enumerate(cases, 1):
        cid = case["case_id"]
        ok = None
        for attempt in range(3):
            try:
                lab = call_case(contract, schema_str, case)
                jsonschema.validate(lab, schema)
                if lab.get("case_id") != cid:
                    raise ValueError(
                        "case_id mismatch: " + str(lab.get("case_id")))
                ok = lab
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    schema_failures.append(
                        {"case_id": cid, "error": str(exc)[:300]})
                time.sleep(2)
        if ok:
            annotations[cid] = ok
        print(f"{args.tag} {i:02d}/{len(cases)} {cid} "
              f"{ok['semantic_relation'] if ok else 'SCHEMA_FAILURE'}",
              flush=True)
    result = {
        "tag": args.tag,
        "model": MODEL,
        "temperature": 0,
        "contract_sha256": sha(HERE / "annotation-contract-v3.md"),
        "schema_sha256": sha(schema_path),
        "cases_file": Path(args.cases).name,
        "annotations": annotations,
        "schema_failure_count": len(schema_failures),
        "schema_failures": schema_failures,
    }
    Path(args.out).write_text(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(args.tag + "_COMPLETE " + str(len(annotations)) + "/"
          + str(len(cases)) + " schema_failures="
          + str(len(schema_failures)))


if __name__ == "__main__":
    main()
