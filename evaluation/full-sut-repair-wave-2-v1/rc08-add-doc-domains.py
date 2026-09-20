"""RC-08 one-shot: add per-doc domains to data/knowledge-index-v1.json.

Doc content and sha256 pins are untouched; only index metadata changes.
The pre-change index SHA is recorded in rc08-root-cause.md.
"""
import hashlib
import json

PATH = "data/knowledge-index-v1.json"

DOM = {
    "mental_health": {"25", "26", "28b", "28c", "31", "45", "69", "75",
                      "22", "24", "33", "71", "72", "73", "74"},
    "housing": {"55", "56", "57", "58", "59", "60", "61", "62", "66"},
    "financial_support": {"48", "49", "50", "51", "52", "53", "54", "56",
                          "63", "64", "65", "66", "67", "68"},
    "child_safety": {"38", "39", "40", "42", "44", "46", "41"},
    "education": {"17", "28", "29", "30", "31", "32", "65", "66"},
    "employment": {"20", "21"},
    "legal_rights": {"18", "19", "24", "33", "34", "35", "36", "37", "41",
                     "46", "48", "49", "50", "63", "68"},
}
ORDER = ["mental_health", "housing", "financial_support", "child_safety",
         "education", "employment", "legal_rights", "general"]


def domains_for(doc_id):
    num = doc_id.split("-")[0]
    doms = [d for d, ids in DOM.items() if num in ids]
    return sorted(doms or ["general"], key=ORDER.index)


def main():
    with open(PATH, encoding="utf-8") as fh:
        idx = json.load(fh)
    for d in idx["docs"]:
        d["domains"] = domains_for(d["id"])
    note = (" RC-08: per-doc domains added from frozen decompose "
            "vocabulary; content and sha256 pins unchanged.")
    idx["note"] = (idx.get("note", "") + note).strip()
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=2)
        fh.write(chr(10))
    with open(PATH, "rb") as fh:
        print("new index sha:", hashlib.sha256(fh.read()).hexdigest())


if __name__ == "__main__":
    main()
