"""Deterministic S4 knowledge retrieval (Phase 2).

Retrieval runs only over sha-verified entries of the frozen knowledge index.
Doc claims are verbatim spans. LAW authority comes only from the frozen rules
registry; gap-register content is uncertainty-only and never positive evidence.
"""

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from collections.abc import Iterator, Mapping
from typing import cast

from runtime.type_support import object_list, object_mapping, string, strings
from .contracts import AdmissionFailure, Coverage, Document, KnowledgeRecord, SourceReference

from .text_normalization import normalize_match_text


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
PUBLIC_CLASSES = frozenset({"DECISION_SUPPORT", "SOURCE_DOCUMENTATION", "GAP_REGISTRY"})


class KnowledgeError(Exception):
    pass


@dataclass
class RetrievalResult:
    records: list[KnowledgeRecord]
    failures: list[AdmissionFailure]
    coverage: Coverage


def verified_date(value: object) -> str | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        _ = date.fromisoformat(value)
    except ValueError:
        return None
    return value


def query_keywords(query: str) -> list[str]:
    tokens = [match.group() for match in re.finditer(r"[a-z0-9]+", normalize_match_text(query))]
    return [t for t in tokens if len(t) >= 2 and t not in STOPWORDS]


def _iter_spans(content: str) -> Iterator[str]:
    """Yield verbatim candidate spans (lines, then sentence-sized pieces)."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) <= 400:
            yield stripped
            continue
        for sentence in re.finditer(r"[^.]*\.", line):
            s = sentence.group().strip()
            if not s:
                continue
            if len(s) > 400:
                s = s[:400].rsplit(" ", 1)[0]
            yield s


def score_span(span: str, keywords: list[str]) -> int:
    hay = normalize_match_text(span)
    return sum(1 for k in keywords if k in hay)


def _source_bytes(repo_root: str, relative: str) -> bytes:
    root = Path(repo_root).absolute()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise KnowledgeError("PATH_REJECTED")
    current = root
    for part in rel.parts:
        current /= part
        if current.is_symlink():
            raise KnowledgeError("PATH_REJECTED")

    def opener(_path: str, flags: int) -> int:
        fds: list[int] = []
        try:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            fds.append(fd)
            for part in rel.parts[:-1]:
                fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                fds.append(fd)
            result = os.open(rel.name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            if not stat.S_ISREG(os.fstat(result).st_mode):
                os.close(result)
                raise KnowledgeError("PATH_REJECTED")
            return result
        finally:
            for fd in reversed(fds):
                os.close(fd)

    with open(current, "rb", opener=opener) as fh:
        return fh.read()


def load_knowledge(index_path: str = DEFAULT_INDEX, repo_root: str = REPO_ROOT, *,
                   access_profile: object = None, domain: str | None = None) -> tuple[list[Document], list[AdmissionFailure]]:
    try:
        profile = object_mapping(access_profile)
        if profile.get("version") != "knowledge-access/v1":
            raise ValueError("Unknown access profile")
        permits = object_mapping(profile.get("documents"))
    except ValueError:
        return [], [{"reason": "ACCESS_PROFILE_REQUIRED"}]
    try:
        relative = Path(index_path).absolute().relative_to(Path(repo_root).absolute())
        index = object_mapping(cast(object, json.loads(_source_bytes(repo_root, str(relative)))))
        entries = object_list(index.get("docs"))
    except (OSError, ValueError, KnowledgeError) as exc:
        raise KnowledgeError("INDEX_UNAVAILABLE") from exc
    docs: list[Document] = []
    failures: list[AdmissionFailure] = []
    for value in entries:
        try:
            entry = object_mapping(value)
            doc_id = string(entry.get("id"))
            permit = object_mapping(permits.get(doc_id))
            domains = strings(entry.get("domains") or ["general"])
            permit_domains = strings(permit.get("domains") or ["general"])
            if domain is not None and domain not in domains and domain not in permit_domains:
                continue
            path = string(entry.get("path"))
            source_class = string(entry.get("class"))
            if (permit.get("permission") != "GENERAL_APPROVED"
                    or source_class not in PUBLIC_CLASSES
                    or any(permit.get(k) != entry.get(k) for k in (
                        "path", "class", "sha256", "domains", "freshness_class", "verified_date"))):
                raise ValueError("Source not admitted")
            freshness = string(entry.get("freshness_class", "UNKNOWN"))
        except ValueError:
            failures.append({"reason": "SOURCE_NOT_ADMITTED"})
            continue
        try:
            raw = _source_bytes(repo_root, path)
        except KnowledgeError:
            failures.append({"reason": "PATH_REJECTED"})
            continue
        except OSError:
            failures.append({"reason": "FILE_MISSING"})
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entry.get("sha256"):
            failures.append({"reason": "SHA_MISMATCH"})
            continue
        docs.append({
            "doc_id": doc_id,
            "path": path,
            "sha256": digest,
            "class": source_class,
            "freshness_class": freshness,
            "domains": domains,
            "verified_date": verified_date(entry.get("verified_date")),
            "content": raw.decode("utf-8", errors="replace"),
        })
    return docs, failures


def _load_rules(rules_path: str = DEFAULT_RULES, repo_root: str = REPO_ROOT,
                access_profile: object = None) -> list[Mapping[str, object]]:
    try:
        profile = object_mapping(access_profile)
        if profile.get("version") != "knowledge-access/v1":
            return []
        _ = object_mapping(profile.get("documents"))
        permit = object_mapping(profile.get("rules"))
    except ValueError:
        return []
    if permit.get("permission") != "GENERAL_APPROVED":
        return []
    try:
        relative = Path(rules_path).absolute().relative_to(Path(repo_root).absolute())
        if str(relative) != permit.get("path"):
            raise KnowledgeError("RULES_NOT_ADMITTED")
        raw = _source_bytes(repo_root, str(relative))
        if hashlib.sha256(raw).hexdigest() != permit.get("sha256"):
            raise KnowledgeError("RULES_SHA_MISMATCH")
        parsed = object_mapping(cast(object, json.loads(raw)))
        return [object_mapping(rule) for rule in object_list(parsed.get("rules"))]
    except (OSError, ValueError) as exc:
        raise KnowledgeError("RULES_UNAVAILABLE") from exc


def _rule_record(rule: Mapping[str, object], n: int) -> KnowledgeRecord:
    src = object_mapping(rule["source"])
    reference: SourceReference = {"kind": string(src["kind"]), "ref": string(src["ref"]), "url": string(src["url"])}
    rule_id = string(rule["rule_id"])
    name = string(rule["name"])
    return {
        "record_id": "K-R%03d" % n,
        "source_type": "FROZEN_RULE",
        "domain": RULE_DOMAINS.get(rule_id, "general"),
        "claim": "%s: %s" % (name, rule.get("deadline_meaning", name)),
        "source_reference": reference,
        "authority": "LAW",
        "freshness": "CURRENT" if verified_date(rule.get("verified_date")) else "UNKNOWN",
        "evidence_id": "E-R%03d" % n,
        "provenance": {
            "artifact": "rules-v1",
            "rule_id": rule_id,
            "verified_date": verified_date(rule.get("verified_date")),
        },
        "gap_state": None,
        "historical_research": False,
    }


def document_record(doc: Document, claim: str, n: int) -> KnowledgeRecord:
    is_gap = doc["doc_id"] in GAP_DOC_IDS or doc.get("class") == "GAP_REGISTRY"
    domains = doc.get("domains") or ["general"]
    return {
        "record_id": "K-D%03d" % n,
        "source_type": "GAP" if is_gap else "PROJECT_RESEARCH",
        "domain": domains[0],
        "domains": domains,
        "claim": claim,
        "source_lines": doc["content"].splitlines(),
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
            "verified_date": doc.get("verified_date"),
        },
        "gap_state": "REGISTERED_GAP" if is_gap else None,
        "historical_research": is_gap or doc["freshness_class"] == "POINT_IN_TIME",
    }


def retrieve(query: str, domain: str, index_path: str = DEFAULT_INDEX, repo_root: str = REPO_ROOT,
             rules_path: str = DEFAULT_RULES, *, access_profile: object = None) -> RetrievalResult:
    failures: list[AdmissionFailure] = []
    try:
        docs, failures = load_knowledge(index_path, repo_root, access_profile=access_profile, domain=domain)
    except KnowledgeError as exc:
        docs = []
        failures = [{"reason": str(exc)}]
    keywords = query_keywords(query)
    records: list[KnowledgeRecord] = []
    n = 1
    try:
        rules = _load_rules(rules_path, repo_root, access_profile)
    except KnowledgeError as exc:
        rules = []
        failures.append({"reason": str(exc)})
    for rule in rules:
        if RULE_DOMAINS.get(string(rule["rule_id"])) != domain:
            continue
        rule_text = " ".join(str(rule.get(k, "")) for k in
                             ("name", "deadline_meaning", "rule_id"))
        applies = json.dumps(rule.get("applies_to", {}), ensure_ascii=False)
        if score_span((rule_text + " " + applies).lower(), keywords) >= 1:
            records.append(_rule_record(rule, n))
            n += 1
    scored: list[tuple[int, Document, str]] = []
    for doc in docs:
        # RC-08: lexical scoring runs only over docs scoped to the track
        # domain; cross-domain docs are excluded before any span is scored.
        if domain not in (doc.get("domains") or ["general"]):
            continue
        best, best_score = None, 0
        for span in _iter_spans(doc["content"]):
            score = score_span(span.lower(), keywords)
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
        records.append(document_record(doc, claim, n))
        n += 1
    records = records[:MAX_RECORDS]
    return RetrievalResult(records, failures, {
        "state": "INCOMPLETE" if failures else "COMPLETE",
        "scope": "PROFILE_AND_DOMAIN", "admitted_documents": len(docs),
        "matched_records": len(records)})

_keywords = query_keywords
_score_span = score_span
_doc_record = document_record
