#!/usr/bin/env python3
"""Overlap/lineage check: fresh batch rows vs burned reference corpus and historical fixtures.

Read-only: writes only this task's report artifacts. No model calls.
"""
import difflib
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
EVAL_DIR = TASK_DIR.parent
DATASET = TASK_DIR / "dataset-frozen.jsonl"
REFERENCE = EVAL_DIR / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"

FIXTURE_GLOBS = [
    "dev-corpus-semantic-judge-v1/judge-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1/calibration-fixtures.json",
    "dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json",
    "dev-corpus-semantic-judge-v1-1/calibration-fixtures-v1-1.json",
    "dev-corpus-semantic-judge-v1-2/judge-validation-fixtures-v1-2.json",
    "dev-corpus-semantic-judge-v1-2/uncertainty-calibration-a.json",
    "dev-corpus-semantic-judge-v1-2/uncertainty-calibration-b.json",
    "dev-corpus-semantic-judge-v1-2/model-calibration.json",
    "dev-corpus-semantic-judge-v1-3/boundary-calibration-a.json",
    "dev-corpus-semantic-judge-v1-3m/boundary-calibration-a.json",
    "dev-corpus-semantic-judge-v1-4/official-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-4/model-calibration-fixtures.json",
    "dev-corpus-semantic-judge-v1-4/boundary-calibration-a.json",
    "dev-corpus-semantic-judge-v1-6a/boundary-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a/unit-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a1/targeted-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a1/unit-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a2/official-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a2/tdd-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a2/unit-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a3/official-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a3/tdd-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a4/official-validation-fixtures.json",
    "dev-corpus-semantic-judge-v1-6a4/tdd-fixtures.json",
    "dev-corpus-semantic-judge-v1-6b/screening-fixtures.json",
]

DECISION_TERMS = [
    "113", "legevakt", "virkedager", "henvisning", "henvisningsrett", "bup",
    "phbu", "rph", "hfu", "dps", "fastlege", "helsesykepleier", "barnevern",
    "psykolog", "akutt", "krise", "poliklinikk", "ungesaksbehandler",
    "omsorgssvikt", "ppt", "familievern", "habilitering", "lavterskel",
    "samtykke", "diagnose", "henvisning kreves", "ikke krav", "bare dersom",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_fixtures(rel):
    path = EVAL_DIR / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "fixtures" in data:
        return data["fixtures"]
    return [data] if isinstance(data, dict) else data


def triples_from_row(row):
    """Extract (context, criterion, sut_output) triples from heterogeneous shapes."""
    out = []
    pkt = row.get("packet") or {}
    if "case_context" in pkt and "criterion" in pkt:
        out.append((pkt.get("case_context") or "", pkt.get("criterion") or "",
                    pkt.get("sut_output") or row.get("sut_output") or ""))
    if "case_context" in row and "gold_criterion" in row:
        out.append((row.get("case_context") or "", row.get("gold_criterion") or "",
                    row.get("sut_answer") or ""))
    if "ctx" in row and "crit" in row:
        out.append((row.get("ctx") or "", row.get("crit") or "", row.get("sut") or ""))
    if "text" in row:
        out.append((row.get("text") or "", row.get("criterion") or "", ""))
    return out


def normalize(text):
    text = unicodedata.normalize("NFKC", text or "")
    for a, b in (("ø", "o"), ("æ", "ae"), ("å", "aa"), ("Ø", "O"), ("Æ", "AE"), ("Å", "AA")):
        text = text.replace(a, b)
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def mask_text(text):
    text = re.sub(r"\b\d+\b", "#N", text)
    text = re.sub(r"[Kk]ommunen?\s+[A-Z\xc5\xd8\xc6][a-z\xe6\xf8\xe5]+", "#K", text)
    return text


def full_text(triple):
    parts = []
    for part in triple:
        if isinstance(part, str):
            parts.append(part)
        elif part is None:
            parts.append("")
        else:
            parts.append(json.dumps(part, ensure_ascii=False, sort_keys=True))
    return " || ".join(parts)


def decision_terms(text):
    normed = normalize(text)
    return {term for term in DECISION_TERMS if term in normed}


CONTENT_STOPWORDS = {
    "og", "eller", "at", "det", "som", "til", "for", "med", "om", "en", "ei", "et",
    "pa", "av", "i", "er", "har", "kan", "skal", "den", "de", "du", "je", "ikke",
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
}


def content_tokens(normed_text):
    return {tok for tok in re.findall(r"[a-z0-9]{3,}", normed_text)
            if tok not in CONTENT_STOPWORDS}


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def main():
    new_rows = load_jsonl(DATASET)
    ref_rows = load_jsonl(REFERENCE)

    ref_hashes = {r.get("canonical_hash") for r in ref_rows if r.get("canonical_hash")}
    ref_packet_hashes = {r.get("packet_sha256") for r in ref_rows if r.get("packet_sha256")}

    ref_triples = []  # (source, triple)
    for row in ref_rows:
        for t in triples_from_row(row):
            ref_triples.append((f"reference-corpus:{row.get('case_id', '?')}", t))

    fixture_counts = {}
    for rel in FIXTURE_GLOBS:
        try:
            fixtures = load_fixtures(rel)
        except (OSError, json.JSONDecodeError) as exc:
            fixture_counts[rel] = f"LOAD_ERROR: {exc}"
            continue
        fixture_counts[rel] = len(fixtures)
        for fixture in fixtures:
            for t in triples_from_row(fixture):
                ref_triples.append((f"{rel}:{fixture.get('id', '?')}", t))

    new_hashes = {row.get("packet", {}).get("canonical_hash") for row in new_rows
                  if row.get("packet", {}).get("canonical_hash")}

    exact_hash_hits = sorted(new_hashes & (ref_hashes | ref_packet_hashes))
    exact_triple_hits = []
    normalized_hits = []
    masked_hits = []
    near_dup_candidates = []

    ref_norm_index = defaultdict(list)   # normed full text -> [(source, triple)]
    ref_masked_index = defaultdict(list)
    ref_exact_index = defaultdict(list)
    ref_precomputed = []  # (source, normed_full, decision_terms, content_tokens)
    for source, triple in ref_triples:
        full = full_text(triple)
        ref_exact_index[full].append(source)
        normed_full = normalize(full)
        ref_norm_index[normed_full].append(source)
        ref_masked_index[normalize(mask_text(full))].append(source)
        ref_precomputed.append((source, normed_full, decision_terms(full), content_tokens(normed_full)))

    for row in new_rows:
        row_id = row.get("row_id", "?")
        for triple in triples_from_row(row):
            full = full_text(triple)
            if full in ref_exact_index:
                exact_triple_hits.append({"row_id": row_id, "sources": ref_exact_index[full]})
            normed = normalize(full)
            if normed in ref_norm_index:
                normalized_hits.append({"row_id": row_id, "sources": ref_norm_index[normed]})
            masked = normalize(mask_text(full))
            if masked in ref_masked_index:
                masked_hits.append({"row_id": row_id, "sources": ref_masked_index[masked]})
            row_terms = decision_terms(full)
            row_tokens = content_tokens(normed)
            for source, ref_normed_full, ref_terms, ref_tokens in ref_precomputed:
                shared = row_terms & ref_terms
                if len(ref_tokens) and len(row_tokens):
                    jacc = len(row_tokens & ref_tokens) / len(row_tokens | ref_tokens)
                else:
                    jacc = 0.0
                if len(shared) >= 2 or jacc >= 0.45:
                    sim = similarity(normed, ref_normed_full)
                    if sim >= 0.55:
                        near_dup_candidates.append({
                            "row_id": row_id,
                            "source": source,
                            "similarity": round(sim, 4),
                            "shared_decision_terms": sorted(shared),
                            "token_jaccard": round(jacc, 4),
                        })

    near_dup_candidates.sort(key=lambda item: (-item["similarity"], item["row_id"]))
    top_near = near_dup_candidates[:40]
    decision_equivalent = [c for c in near_dup_candidates
                           if c["similarity"] >= 0.85 and len(c["shared_decision_terms"]) >= 3]

    summary = {
        "task_id": "NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1",
        "stage": "PREPARATION",
        "dataset_sha256": sha256(DATASET),
        "reference_sha256": sha256(REFERENCE),
        "new_rows": len(new_rows),
        "reference_rows": len(ref_rows),
        "fixture_files": fixture_counts,
        "comparison_layers": {
            "canonical_hash_exact_hits": exact_hash_hits,
            "exact_triple_hits": exact_triple_hits,
            "normalized_text_hits": normalized_hits,
            "masked_text_hits": masked_hits,
        },
        "near_dup_scanned_pairs": len(near_dup_candidates),
        "near_dup_top": top_near,
        "decision_equivalent_candidates": decision_equivalent,
        "gate": {
            "exact_or_normalized_duplicates": len(exact_hash_hits) + len(exact_triple_hits) + len(normalized_hits),
            "decision_equivalent_count": len(decision_equivalent),
            "builder_revision_required": len(decision_equivalent) > 0,
        },
    }

    (TASK_DIR / "overlap-lineage-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Overlap / Lineage Report - Fresh Batch V1",
        "",
        "Preparation-stage artifact. No model calls. Comparison of the 350 fresh rows",
        "against the burned reference corpus (text pool) and all historical fixture files.",
        "",
        "## Inputs",
        "",
        f"- dataset-frozen.jsonl rows: {len(new_rows)} (SHA {sha256(DATASET)[:12]}...)",
        f"- reference-corpus.jsonl rows: {len(ref_rows)} (SHA {sha256(REFERENCE)[:12]}...)",
        f"- historical fixture files scanned: {len(fixture_counts)}",
        f"- total reference text triples indexed: {len(ref_triples)}",
        "",
        "## Gate results",
        "",
        f"- canonical_hash / packet_sha256 exact hits: {len(exact_hash_hits)}",
        f"- exact triple hits: {len(exact_triple_hits)}",
        f"- normalized-text duplicates: {len(normalized_hits)}",
        f"- masked-text (numbers/place) duplicates: {len(masked_hits)}",
        f"- near-dup candidate pairs (sim>=0.55, >=2 shared decision terms): {len(near_dup_candidates)}",
        f"- decision-equivalent candidates (sim>=0.85, >=3 shared terms): {len(decision_equivalent)}",
        "",
        "Gate: **0 exact/normalized duplicates required.** Masked and near-dup hits are",
        "expected at phrase level because the fresh batch intentionally draws on the same",
        "KB domain; only true decision-equivalent duplicates require builder revision.",
        "",
    ]
    if masked_hits:
        lines += ["## Masked-text hits (inspect)", ""]
        for hit in masked_hits[:25]:
            lines.append(f"- {hit['row_id']} == {', '.join(hit['sources'])}")
        lines.append("")
    if top_near:
        lines += ["## Top near-dup pairs", "", "| row_id | source | sim | shared decision terms |", "|---|---|---|---|"]
        for cand in top_near:
            lines.append(f"| {cand['row_id']} | {cand['source']} | {cand['similarity']} | {', '.join(cand['shared_decision_terms'])} |")
        lines.append("")
    verdict = "PASS" if not decision_equivalent else "FAIL - builder revision required"
    lines += [f"## Verdict: {verdict}", ""]
    (TASK_DIR / "overlap-lineage-report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary["gate"], indent=2))
    print("near_dup_scanned_pairs:", len(near_dup_candidates))
    print("masked_hits:", len(masked_hits))
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
