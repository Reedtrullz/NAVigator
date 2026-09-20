"""Deterministic S4 knowledge retrieval (Phase 2).

Retrieval runs only over sha-verified entries of the frozen knowledge index.
Doc claims are verbatim spans. LAW authority comes only from the frozen rules
registry; gap-register content is uncertainty-only and never positive evidence.
"""

import hashlib
import json
import os
import re


REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_INDEX = os.path.join(REPO_ROOT, "data", "knowledge-index-v1.json")
DEFAULT_RULES = os.path.join(REPO_ROOT, "data", "rules-v1.json")

# Canonical gap register docs of the project; their content is registered
# unknowns, so records from them are uncertainty, never factual evidence.
GAP_DOC_IDS = frozenset({"28c-beslutningsstotte-gaps", "69-kunnskapshullregister"})

RULE_DOMAINS = {
    "R-PRI-4A-65D": "mental_health",
    "R-PAS-2-2A-10D": "mental_health",
    "R-EMERGENCY-113-116X": "safety",
}

STOPWORDS = frozenset(
    "og eller for jeg har min mitt av paa i a som det er hva hvor kan med fra den den et en ei skal vil men ikke".split()
)

MAX_RECORDS = 5


class KnowledgeError(Exception):
    pass


def _keywords(query):
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    return [t for t in tokens if len(t) >= 2 and t not in STOPWORDS]


def _iter_spans(content):
    """Yield verbatim candidate spans (lines, then sentence-sized pieces)."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) <= 400:
            yield stripped
            continue
        for sentence in re.findall(r"[^.]*\.", line):
            s = sentence.strip()
            if not s:
                continue
            if len(s) > 400:
                s = s[:400].rsplit(" ", 1)[0]
            yield s


def _score_span(span, keywords):
        hay = span.lower()
        return sum(1 for k in keywords if k in hay)


def load_knowledge(index_path=DEFAULT_INDEX, repo_root=REPO_ROOT):
    """Return (verified docs, failures). Fail-closed on sha/missing files."""
    try:
        with open(index_path, encoding="utf-8") as fh:
            index = json.load(fh)
    except (OSError, ValueError) as exc:
        raise KnowledgeError("knowledge index unreadable: %s" % exc) from exc
    docs, failures = [], []
    for entry in index.get("docs", []):
        path = os.path.join(repo_root, entry["path"])
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
        except OSError:
            failures.append({"doc_id": entry["id"], "reason": "FILE_MISSING"})
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entry.get("sha256"):
            failures.append({"doc_id": entry["id"], "reason": "SHA_MISMATCH"})
            continue
        docs.append({
            "doc_id": entry["id"],
            "path": entry["path"],
            "sha256": digest,
            "class": entry.get("class", "UNKNOWN"),
            "freshness_class": entry.get("freshness_class", "UNKNOWN"),
            "domains": entry.get("domains", ["general"]),
            "content": raw.decode("utf-8", errors="replace"),
        })
    return docs, failures


def _load_rules(rules_path=DEFAULT_RULES):
    try:
        with open(rules_path, encoding="utf-8") as fh:
            return json.load(fh).get("rules", [])
    except (OSError, ValueError) as exc:
        raise KnowledgeError("rules registry unreadable: %s" % exc) from exc


def _rule_record(rule, n):
    src = rule["source"]
    return {
        "record_id": "K-R%03d" % n,
        "source_type": "FROZEN_RULE",
        "domain": RULE_DOMAINS.get(rule["rule_id"], "general"),
        "claim": "%s: %s" % (rule["name"], rule.get("deadline_meaning", rule["name"])),
        "source_reference": {"kind": src["kind"], "ref": src["ref"], "url": src["url"]},
        "authority": "LAW",
        "freshness": "CURRENT",
        "evidence_id": "E-R%03d" % n,
        "provenance": {
            "artifact": "rules-v1",
            "rule_id": rule["rule_id"],
            "verified_date": rule.get("verified_date"),
        },
        "gap_state": None,
        "historical_research": False,
    }


def _doc_record(doc, claim, n):
    is_gap = doc["doc_id"] in GAP_DOC_IDS
    domains = doc.get("domains") or ["general"]
    return {
        "record_id": "K-D%03d" % n,
        "source_type": "GAP" if is_gap else "PROJECT_RESEARCH",
        "domain": domains[0],
        "domains": domains,
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": doc["path"]},
        "authority": "INTERNAL_DOC",
        "freshness": doc["freshness_class"],
        "evidence_id": "E-D%03d" % n,
        "provenance": {
            "artifact": "knowledge-index-v1",
            "doc_id": doc["doc_id"],
            "sha256": doc["sha256"],
            "class": doc["class"],
            "freshness_class": doc["freshness_class"],
        },
        "gap_state": "REGISTERED_GAP" if is_gap else None,
        "historical_research": is_gap or doc["freshness_class"] == "POINT_IN_TIME",
    }


def retrieve(query, domain, index_path=DEFAULT_INDEX, repo_root=REPO_ROOT,
             rules_path=DEFAULT_RULES):
    """Deterministic retrieval for a track domain. Max 5 records."""
    keywords = _keywords(query)
    if not keywords:
        return []
    records = []
    n = 1
    for rule in _load_rules(rules_path):
        if RULE_DOMAINS.get(rule["rule_id"]) != domain:
            continue
        rule_text = " ".join(str(rule.get(k, "")) for k in
                             ("name", "deadline_meaning", "rule_id"))
        applies = json.dumps(rule.get("applies_to", {}), ensure_ascii=False)
        if _score_span((rule_text + " " + applies).lower(), keywords) >= 1:
            records.append(_rule_record(rule, n))
            n += 1
    docs, _failures = load_knowledge(index_path, repo_root)
    scored = []
    for doc in docs:
        # RC-08: lexical scoring runs only over docs scoped to the track
        # domain; cross-domain docs are excluded before any span is scored.
        if domain not in (doc.get("domains") or ["general"]):
            continue
        best, best_score = None, 0
        for span in _iter_spans(doc["content"]):
            score = _score_span(span.lower(), keywords)
            if score > best_score:
                best, best_score = span, score
        if best is not None and best_score >= 1:
            scored.append((best_score, doc, best))
    scored.sort(key=lambda t: (-t[0], t[1]["doc_id"]))
    research_all = [t for t in scored if t[1]["doc_id"] not in GAP_DOC_IDS]
    gaps = [t for t in scored if t[1]["doc_id"] in GAP_DOC_IDS]
    # Reserve one slot for the best gap match so registered unknowns stay
    # visible instead of being crowded out by research docs.
    doc_budget = MAX_RECORDS - len(records)
    gap_budget = min(1, len(gaps)) if doc_budget > 0 else 0
    research_budget = max(0, doc_budget - gap_budget)
    # RC-07: current research outranks point-in-time snapshots; snapshots
    # fill only leftover slots so they cannot crowd out service evidence.
    current = [t for t in research_all if t[1]["freshness_class"] == "CURRENT"]
    snapshot = [t for t in research_all if t[1]["freshness_class"] != "CURRENT"]
    chosen = current[:research_budget] + gaps[:gap_budget]
    chosen += snapshot[: max(0, research_budget - len(current))]
    for _score, doc, claim in chosen:
        records.append(_doc_record(doc, claim, n))
        n += 1
    return records[:MAX_RECORDS]
