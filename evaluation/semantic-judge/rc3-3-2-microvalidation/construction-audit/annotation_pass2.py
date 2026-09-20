#!/usr/bin/env python3
"""PASS 2 independent annotation via GPT-5.6-Luna (spec 14).

The model sees only public case data (claim + evidence packet). Pass-1
labels are never exposed. Output is raw JSON per case; agreement and
adjudication are computed separately.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(HERE))
import write_guard  # noqa: E402

PROXY = "http://127.0.0.1:10100/v1/chat/completions"
# Bare proxy ids return 401 (Codex Direct requires a bearer token);
# provider-scoped ids route without auth.
MODEL = "command-code/gpt-5.6-luna"

PROMPT = """You are annotating a proof-validation benchmark case.
Given the CLAIM and the EVIDENCE packet, output ONLY a JSON object with:
- "semantic_relation": one of SUPPORTED, CONTRADICTED,
  PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE, REVIEW_REQUIRED
  (SUPPORTED = evidence establishes the claim; CONTRADICTED = evidence
  positively refutes it; PARTIALLY_SUPPORTED = part matches, part
  conflicts; INSUFFICIENT_EVIDENCE = packet does not decide it;
  REVIEW_REQUIRED = relevant evidence exists but resolving the claim
  requires bounded inference or interpretation, e.g. exceptions, local
  practice, transition rules, or effects of amendments)
- "semantic_quantity_identity": "TYPE:VALUE:UNIT" for the claim's
  central quantity (TYPE in MONEY/PERCENTAGE/PERIOD/AGE/DATE, e.g.
  "MONEY:1006:NOK", "PERIOD:6:MONTH", "AGE:16:YEAR"), or null
- "temporal_applicability": one of CURRENT_MATCH,
  HISTORICAL_VS_CURRENT, SUPERSEDED, PERIOD_MISMATCH, UNKNOWN,
  NOT_APPLICABLE
- "comparator_applicable": true only if the claim asserts a numeric
  comparison RELATIVE TO the evidence (claim says "na X", "minst X",
  "mer enn X", "innen X"), not merely because a number or age
  threshold appears; the compared value is the claim's number
- "comparator_relation": the claim's own comparison predicate as ASCII
  one of "=", ">=", ">", "<=", "<", else null
  ("na/er" -> "=", "minst" -> ">=", "mer enn" -> ">",
  "ikke over/innen ... ar" (upper bound) -> "<=")
- "aggregate_component_role": one of STANDALONE, AGGREGATE, COMPONENT,
  DERIVED
- "temporal_applicability": CURRENT_MATCH when the evidence states a
  current rule without conflicting dates; UNKNOWN only when the packet
  cannot establish which rule version applies; PERIOD_MISMATCH when
  the claim's date falls outside the evidence's validity window;
  SUPERSEDED only when the evidence states supersession
- "semantic_quantity_identity": null unless the claim itself contains
  a specific number
- aggregate claims: when the evidence states components of a sum and
  the claim asserts a specific total, compute the sum; a claimed total
  that does not equal the component sum is CONTRADICTED
No prose outside the JSON."""


def call(case):
    packet = {
        "claim": case["claim"],
        "evidence": [s["text"] for s in case["evidence"]],
    }
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": json.dumps(packet,
                                                   ensure_ascii=False)},
        ],
        "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(PROXY, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        text = text.strip("`").lstrip("json").strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


FIELDS = ["semantic_relation", "semantic_quantity_identity",
          "temporal_applicability", "comparator_applicable",
          "comparator_relation", "aggregate_component_role"]


def main():
    pub = json.loads((TASK / "microvalidation-cases.json").read_text(
        encoding="utf-8"))
    out = {}
    for i, case in enumerate(pub["cases"], 1):
        for attempt in range(3):
            try:
                lab = call(case)
                missing = [f for f in FIELDS if f not in lab]
                if missing:
                    raise ValueError(f"missing {missing}")
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    raise SystemExit(
                        f"PASS2_FAIL {case['case_id']}: {exc}")
                time.sleep(2)
        out[case["case_id"]] = lab
        print(f"pass2 {i:02d}/30 {case['case_id']} "
              f"{lab['semantic_relation']}")
    write_guard.write_text(
        HERE / "labels-pass2-raw.json",
        json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print("PASS2_COMPLETE", len(out))


if __name__ == "__main__":
    main()
