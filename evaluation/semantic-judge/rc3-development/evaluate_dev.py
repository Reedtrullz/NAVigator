"""RC3 development-corpus evaluation (DEVELOPMENT_SANITY_ONLY).

The corpus is previously tuned during RC2 iterations: results are
sanity evidence, not generalization evidence (spec 38). No case IDs
are referenced; cases stream from the frozen dev file.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "rc3_engine"))
import engine_rc3 as eng  # noqa: E402
import arbitration as arb  # noqa: E402
import reviewer_bridge as rb  # noqa: E402
import routing as rt  # noqa: E402

CACHE = json.loads(Path("/tmp/rc3_review_cache.json").read_text())

EXPECTED_TO_PRODUCT = {
    "SUPPORTED": "AUTO_SUPPORTED",
    "CONTRADICTED": "AUTO_CONTRADICTED",
    "PARTIALLY_SUPPORTED": "PARTIALLY_SUPPORTED",
}


def main():
    dev = json.load(open(HERE.parent / "hybrid" / "development-set.json"))
    rows = []
    for case in dev["cases"]:
        claim, source = case["claim"], case["source"]
        expected = case["expected"]
        out = eng.judge_claim(claim, source)
        # Every atom passes arbitration (R1/R2 apply to accepted
        # proofs too); NO_PROOF atoms fall back to the frozen
        # sufficiency classifier when no proposal is available.
        proposal = CACHE.get(case["id"])
        ok, errs = (arb.validate_reviewer_output(proposal, source)
                    if proposal else (False, ["no_proposal"]))
        routes = []
        reasons = []
        for atom in out["atoms"]:
            if ok:
                r = arb.arbitrate(atom, proposal, source)
                if r == "REVIEW_REQUIRED":
                    if atom["proof_state"] == "ENGINE_PROOF_ACCEPTED" \
                            and proposal.get("counter_proof"):
                        reasons.append("counter_proof")
                    elif atom["proof_state"] == "ENGINE_PROOF_ACCEPTED":
                        reasons.append("reviewer_downgrade")
                    elif atom["proof_state"] == "ENGINE_UNSAFE":
                        reasons.append("engine_unsafe_guard")
                    else:
                        reasons.append("no_bounded_proof")
                routes.append(r)
            else:
                r = rt.route_atom(atom, claim, source)
                if r == "REVIEW_REQUIRED":
                    reasons.append("no_bounded_proof")
                routes.append(r)
        product = rt.aggregate_atoms(
            [{"route": r} for r in routes])["product_action"]
        if product == "REVIEW_REQUIRED" and not reasons:
            reasons.append("mixed_atom_review")
        exp_product = EXPECTED_TO_PRODUCT.get(expected, "ABSTAIN_OR_REVIEW")
        rows.append({
            "id": case["id"],
            "expected_semantic": expected,
            "expected_product": exp_product,
            "product": product,
            "proof_state": out["atoms"][0]["proof_state"],
            "review_reasons": reasons,
            "atom_count": out["atom_count"],
            "correct": product == exp_product if exp_product !=
                "ABSTAIN_OR_REVIEW" else product in
                ("ABSTAIN_INSUFFICIENT", "REVIEW_REQUIRED"),
        })

    n = len(rows)
    semantic_exact = sum(
        1 for r in rows if r["expected_product"] == r["product"]) / n
    product_exact = sum(1 for r in rows if r["correct"]) / n
    # Auto actions and their correctness.
    autos = [r for r in rows if r["product"] in
             ("AUTO_SUPPORTED", "AUTO_CONTRADICTED")]
    auto_prec = (sum(1 for r in autos if r["expected_product"] ==
                     r["product"]) / len(autos)) if autos else 0.0
    # Review routing quality.
    reviews = [r for r in rows if r["product"] == "REVIEW_REQUIRED"]
    unnecessary = sum(1 for r in reviews if r["expected_product"] in
                      ("AUTO_SUPPORTED", "AUTO_CONTRADICTED",
                       "PARTIALLY_SUPPORTED"))
    # Spec 36 definition: an unnecessary review is one that overturns
    # a CORRECT accepted proof without counter-evidence. Counter-proof
    # and unsafe-guard reviews are adjudication, not noise.
    overturning = sum(1 for r in reviews
                      if r["expected_product"] in
                      ("AUTO_SUPPORTED", "AUTO_CONTRADICTED",
                       "PARTIALLY_SUPPORTED")
                      and "reviewer_downgrade" in r["review_reasons"])
    unnec_rate = unnecessary / len(reviews) if reviews else 0.0
    # Expected-abstain recall (expected INSUFFICIENT_EVIDENCE).
    exp_abs = [r for r in rows if r["expected_semantic"] ==
               "INSUFFICIENT_EVIDENCE"]
    abs_recall = (sum(1 for r in exp_abs if r["product"] in
                      ("ABSTAIN_INSUFFICIENT", "REVIEW_REQUIRED")) /
                  len(exp_abs)) if exp_abs else 0.0
    # Unsound accepted proofs: accepted auto without grounded proof.
    unsound = []
    for r in rows:
        if r["product"] in ("AUTO_SUPPORTED", "AUTO_CONTRADICTED"):
            c = next(c for c in dev["cases"] if c["id"] == r["id"])
            out = eng.judge_atom(c["claim"], c["source"])
            p = out.get("proof")
            if out["proof_state"] == "ENGINE_PROOF_ACCEPTED" and (
                    not p or not p.get("source_span") or
                    p["source_span"] not in c["source"]):
                unsound.append(r["id"])
    # Engine-layer dev numbers (DEVELOPMENT_SANITY_ONLY: this corpus
    # was tuned for the looser RC2 routing doctrine, so exactness
    # against RC2 labels is sanity evidence, never generalization).
    eng_sem = eng_psafe = 0
    for c in dev["cases"]:
        out = eng.judge_claim(c["claim"], c["source"])
        exp = c["expected"]
        fv = out["atoms"][0]["frozen_verdict"] \
            if out["atom_count"] == 1 else out["final_verdict"]
        eng_sem += fv == exp
        fin = out["final_verdict"]
        psafe = {"AUTO_SUPPORTED": "SUPPORTED",
                 "AUTO_CONTRADICTED": "CONTRADICTED"}.get(
            fin, "INSUFFICIENT_EVIDENCE"
            if fin in ("REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT")
            else fin)
        eng_psafe += psafe == exp
    summary_doc = {
        "corpus_tag": "DEVELOPMENT_SANITY_ONLY",
        "n": n,
        "semantic_exact": round(semantic_exact, 4),
        "product_exact": round(product_exact, 4),
        "engine_layer_semantic_exact": round(eng_sem / n, 4),
        "engine_layer_proof_safe_exact": round(eng_psafe / n, 4),
        "auto_count": len(autos),
        "auto_precision": round(auto_prec, 4),
        "review_count": len(reviews),
        "unnecessary_review_rate": round(unnec_rate, 4),
        "unnecessary_review_overturning": overturning,
        "expected_abstain_n": len(exp_abs),
        "abstain_or_review_recall": round(abs_recall, 4),
        "unsound_accepted_proofs": unsound,
        "rows": rows,
    }
    out_path = HERE / "development-results.json"
    out_path.write_text(json.dumps(summary_doc, ensure_ascii=False,
                                   indent=1))
    print(json.dumps({k: v for k, v in summary_doc.items()
                      if k != "rows"}, ensure_ascii=False, indent=1))
    out_path = HERE / "development-results.json"
    out_path.write_text(json.dumps(summary_doc, ensure_ascii=False,
                                   indent=1))


if __name__ == "__main__":
    main()
