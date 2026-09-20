# Packet schema v2.1 (packet-v2.1)

Schema addendum on top of the frozen v1.1 reviewer semantics (spec 32).
No semantic rules changed; the prompt diff is purely syntactic (rules 8-11)
and is registered by SHA.

## Prompt diff (exact)

Base: reviewer.py SYSTEM_PROMPT v1.1 (rules 1-7, unchanged, verbatim).
Appended rules:

    8. Packet-skjema: claimet er delt i atomer (A1, A2, ...). Hvert atom
       har kandidat-evidence (span_id, roles, relation) og det finnes en
       felles candidate_spans-liste med selve span-teksten.
    9. relation single_support: spanet alene dekker atomet.
       relation joint_support: spans i evidence_set maa kombineres for aa
       dekke atomet. relation qualifier: kontekst.
       group_type RULE_WITH_CONDITION/RULE_WITH_EXCEPTION markerer
       koblede regler.
    10. Output per atom, KUN gyldig JSON, ingen annen tekst:
        {"atoms": [{"atom_id": "A1", "verdict": "SUPPORTED",
                    "evidence_span_ids": ["S2"], "confidence": 0.95,
                    "needs_human_review": false}],
         "reason_code": "kort_snake_case"}
    11. Alle atomer skal vaere representert i output.
        evidence_span_ids maa vaere span_id-er fra atomets egen
        kandidat-evidence-liste.

Prompt SHA256 (first 16 hex): 7377d10307e2fb7d
Model: openai/gpt-5.6-luna, temperature 0, max_tokens 300 (unchanged).

## Packet JSON structure

    {
      "schema": "packet-v2.1",
      "claim_atoms": ["..."],
      "candidate_spans": [{"span_id": "S1", "text": "...", "score": 0.83,
                           "roles": ["NUMERIC", "MAIN_RULE"]}],
      "atoms": [{"atom_id": "A1", "claim_atom": "...",
                 "candidate_evidence": [{"span_id": "S1", "roles": [...],
                                         "atom_coverage": 0.8,
                                         "relation": "single_support"}],
                 "evidence_set": ["S1", "S2"],
                 "joint_coverage": 0.9,
                 "group_type": "RULE_WITH_CONDITION"}],
      "deterministic_findings": {...}
    }

## Fidelity validation (deterministic, before fusion)

* output is a JSON object with an atoms list
* every atom_id exists in the packet; no duplicates
* verdicts in {SUPPORTED, CONTRADICTED, PARTIAL, INSUFFICIENT}
* confidence in [0, 1]
* evidence_span_ids reference packet spans AND belong to that atom's
  own candidate group (rejects cross-atom binding)
* SUPPORTED/CONTRADICTED/PARTIAL without evidence is rejected

Failures route to REVIEW_REQUIRED (route = fidelity_failed:<reason>).

## Deterministic fusion (unchanged doctrine)

1. no output or fidelity failure -> REVIEW_REQUIRED
2. needs_human_review -> REVIEW_REQUIRED
3. per-atom confidence below classify_threshold -> atom INSUFFICIENT
4. hard-contradiction lock and injection lock -> REVIEW_REQUIRED
5. any atom PARTIAL -> claim PARTIAL
6. otherwise frozen aggregate() over atom verdicts (compound-aware)
