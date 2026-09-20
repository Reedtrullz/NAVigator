"""Construction toolkit: novelty checker, KB sentence index, and
deterministic quality validators for the RC3 generalization holdout.

Firewall design (spec 12): case authors pass only rejection metadata
through check_novelty(); the tool itself reads old corpora, but the
author never sees their claims. Validators here never consult any
runtime engine and never read sealed or frozen artifacts.
"""
import json
import os
import re
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
KB = Path("/Users/reidar/Projectos/NAV Explore")

# ---------------- KB sentence index (allowed source of cases) ------

def kb_sentences():
    """Yield (rel_path, sentence) for every KB markdown sentence."""
    skip = ("/evaluation/", "/.git/", "/scripts/", "/data/")
    for md in sorted(KB.rglob('*.md')):
        rel = str(md.relative_to(KB))
        if any(s in rel for s in skip):
            continue
        text = md.read_text(encoding='utf-8', errors='replace')
        for para in re.split(r"\n\s*\n", text):
            para = re.sub(r"^#+\s*", "", para.strip())
            if not para or para.startswith(('|', '-', '*', '>', '```')):
                continue
            for sent in re.split(r"(?<=[.!?:])\s+", para):
                sent = re.sub(r"\s+", " ", sent).strip()
                if 40 <= len(sent) <= 600:
                    yield rel, sent


# ---------------- mechanical novelty checker -----------------------

def _shingle_set(text):
    toks = re.findall(r"[a-z\xe6\xf8\xe50-9]+", text.lower())
    if len(toks) < 3:
        toks = toks or ['<short>']
    return {tuple(toks[i:i + 3])
            for i in range(max(1, len(toks) - 2))}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def _load_reference_texts():
    refs = []
    roots = [
        SEM / "blind-recertification",
        SEM / "v0.3",
        SEM / "v0.4",
        SEM / "v0.4.1",
        SEM / "operator-regression",
        SEM / "tier1-coverage-repair",
        SEM / "tier1-proof",
        SEM / "rc2-development",
        SEM / "rc3-development",
        SEM / "hybrid",
    ]
    for root in roots:
        if not root.exists():
            continue
        for jf in root.rglob('*.json'):
        # mechanical reader only; authors never see contents
            try:
                data = json.loads(jf.read_text(encoding='utf-8'))
            except Exception:
                continue
            def walk(x, depth=0):
                if depth > 6:
                    return
                if isinstance(x, str):
                    if 20 <= len(x) <= 600 and any(
                        c.isalpha() for c in x):
                        yield x
                elif isinstance(x, list):
                    for i in x:
                        yield from walk(i, depth + 1)
                elif isinstance(x, dict):
                    for k, v in x.items():
                        yield from walk(v, depth + 1)
            yield from walk(data)
    return refs

_REFS = None

def check_novelty(candidate_claims, max_report=5):
    """Return rejection metadata per candidate claim.

    Firewall: returns only per-candidate {claim_ref, max_similarity,
    verdict}; never any reference text. candidate_claims is a list of
    (claim_ref, claim_text) pairs; claim_ref is an author-local handle.
    """
    global _REFS
    if _REFS is None:
        _REFS = [(_shingle_set(r), r) for r in _load_reference_texts()]
    report = []
    for ref_id, claim in candidate_claims:
        cs = _shingle_set(claim)
        best = 0.0
        for rs, _ in _REFS:
            sim = jaccard(cs, rs)
            if sim > best:
                best = sim
                if best > 0.9:
                    break
        verdict = ('REJECT_NEAR_DUPLICATE' if best >= 0.75 else
                   "REJECT_MINIMAL_VARIANT" if best >= 0.55 else
                   "OK")
        report.append({'claim_ref': ref_id,
                       "max_similarity": round(best, 3),
                       "verdict": verdict})
    return report


# ---------------- deterministic validators -------------------------

SEMANTIC_VALUES = {'SUPPORTED', 'CONTRADICTED',
                   'PARTIALLY_SUPPORTED', "INSUFFICIENT_EVIDENCE"}
PROOF_SAFE_VALUES = {'SUPPORTED', 'CONTRADICTED',
                     'INSUFFICIENT_EVIDENCE', "REVIEW_REQUIRED"}
PRODUCT_VALUES = {'AUTO_SUPPORTED', 'AUTO_CONTRADICTED',
                  'REVIEW_REQUIRED', "ABSTAIN_INSUFFICIENT"}

VALID_PRODUCT_FOR_SEMANTIC = {
    "SUPPORTED": {"AUTO_SUPPORTED", "REVIEW_REQUIRED"},
    "CONTRADICTED": {"AUTO_CONTRADICTED", "REVIEW_REQUIRED"},
    "PARTIALLY_SUPPORTED": {"REVIEW_REQUIRED"},
    "INSUFFICIENT_EVIDENCE": {"ABSTAIN_INSUFFICIENT",
                              "REVIEW_REQUIRED"},
}

def validate_case(c):
    """Deterministic construction-quality check for one case dict.
    Returns list of violation strings (empty = pass). No engine use.
    """
    errs = []
    cid = c.get('case_id', '<no-id>')
    for f in ('case_id', 'claim', 'sources', 'evidence', 'track'):
        if f not in c:
            errs.append(cid + ":missing:" + f)
    if not re.fullmatch(r"RC3G-\d{4}", c.get("case_id", "")):
            errs.append(cid + ":bad_id_format")
    if c.get("track") not in ("A", "B"):
        errs.append(cid + ":bad_track")
    srcs = c.get('sources') or []
    if not srcs:
        errs.append(cid + ":no_sources")
    evidence = c.get('evidence') or []
    if not evidence:
        errs.append(cid + ":no_evidence")
    src_texts = [s.get("text", "") for s in srcs]
    joined = '\n\n'.join(src_texts)
    for ev in evidence:
            span = ev.get("text", "")
            if not span or span not in joined:
                errs.append(cid + ":span_not_in_sources:" +
                            ev.get("span_id", "?"))
    if c.get("compound"):
        atoms = c.get('atoms') or []
        if len(atoms) < 2:
            errs.append(cid + ":compound_needs_2_atoms")
        for i, a in enumerate(atoms, 1):
            for f in ('atom_id', 'text', 'semantic_truth',
                      "evidence_span_ids", "required_inference"):
                if f not in a:
                    errs.append("%s:atom%d:missing:%s" % (cid, i, f))
            if a.get("semantic_truth") not in SEMANTIC_VALUES:
                errs.append("%s:atom%d:bad_semantic" % (cid, i))
        ids = [a.get("atom_id") for a in atoms]
        if ids != ["A%d" % i for i in range(1, len(atoms) + 1)]:
            errs.append(cid + ":atom_ids_not_stable")
    return errs


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


if __name__ == '__main__':
    n = sum(1 for _ in kb_sentences())
    print("kb_sentences_indexed:", n)
