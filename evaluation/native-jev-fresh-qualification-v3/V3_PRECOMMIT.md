# JEV V3 PRECOMMIT (frozen before any fresh label inspection)

Task: NAV-EXPLORE-NATIVE-JEV-FRESH-FROZEN-QUALIFICATION-V3
Created: 2026-09-19T21:00:00Z (Europe/Oslo). Authoritative manifest: V3_PRECOMMIT_MANIFEST.json
precommit-manifest sha256: 6f1edc74e12d6ba6aa8c3095fc6ffaf7011e1d029afbc7654004f434b2a4a92e
(note: manifest was amended twice BEFORE any fresh label inspection, solely to replace
non-reproducible handoff exclusion-id hashes with locally recomputed set hashes;
see amendment_1_note / amendment_2_note in the manifest. Policy content unchanged.)

## Locked operative configuration (identical to V2)

- Model/API: native TypeSafe System One, https://api.typesafe.ai/v1/systemone, model jev-latest
  (V2 observed jev-1.13.0). Skill: installed typesafe-ai.
- Question schema: V1 (critical_questions + forbidden_questions), imported unmodified from
  evaluation/native-jev-qualification-v2/question_schema.py.
- Client: V2 jev_client.py imported unmodified (key from env/.env.local; never printed/hashed/persisted).
- Router: V2 deterministic routing_v2.py imported unmodified. Primary threshold T = 0.7.
  Diagnostic thresholds T in {0.7, 0.8, 0.9} precommitted.
- High confidence = top Choice probability >= 0.8.
- Repeatability: 3 identical runs over the FULL fresh set (decided pre-analysis).
- Transport: 0.3 s sleep between calls; HTTP 429 stops the batch; no semantic retries ever.

## Frozen policy hashes (sha256, verified 2026-09-19)

- question_schema.py: 37ee87a90dfc2c726ed68da815e17c4386097b0b8f819758d388cb70357424f9
- jev_client.py: 64c410a1b71b310402a97d5df48110eaef324623f9516ad481326a154859d232
- routing_v2.py: 54e02449913b4f963406985a2a05c2dd4e35721585d876e29f80c93b037051b
- scoring-spec-preregistered.json: fa5ec89145679325a14868207d31d2907411bc40132fb47838806d16996ccaba

## Fresh dataset (frozen)

- id: cost-qual-v1-reference-corpus-fresh-remainder-v3
- source: evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl
  sha256 b85caaaa64f3393f27f8177f0b4979e6139c0ff8d18ee3c80efb45eab9e11c2b (387 rows)
- construction: exclude all V2-slice rows (57 rows / 40 case_ids / 40 packet_ids),
  exclude 12 unlabeled tier-B rows, dedup by canonical_hash (first kept), NO sampling,
  sort by canonical_hash. Redaction rule identical to V2.
- expected composition (from frozen gold fields, carried mechanically): N=235,
  88 distinct case_ids, critical AMBIGUOUS 2, critical CLEAR_NON_TRIGGER 50,
  critical CLEAR_TRIGGER 5, critical INSUFFICIENT 10, forbidden MATCH/NEGATED 16,
  forbidden NO_MATCH/UNRESOLVED 152.
- fresh-case-manifest sha256: 09db8f2bac6d31122de6653eb7c7cf5dfe59b7154c38b462dde94b5f80325093

## Precommitted analysis plan

Per-lane exact metrics + confusion matrices + confidence distributions; deterministic routing
at T=0.7 (AUTO_PASS / AUTO_FAIL / ESCALATE, safe coverage, escalation rate, FALSE_PASS
count/rate + Wilson 95% CI + exact binomial upper bound at 0 events + explicit non-claim
sentence, FALSE_FAIL, accuracy among auto-decided, safety-critical FP, high-conf FP/FF);
T=0.8/0.9 diagnostic only; 3-run stability (routing modal >= 95% gate, choice agreement,
prob L1 drift, threshold-crossing flips); ESC-ROUT-021/026 semantic-family test via
commitment-UNRESOLVED rows (fresh pool has 0 match-UNRESOLVED rows -> partial assessment);
critical lane diagnostic only; cost from measured usage at $0.042 per 1M input tokens
(output free, verified rate in V2); cascade simulation; V2 comparison table.

## Terminal gates (precommitted)

QUALIFIED requires ALL of: FALSE_PASS = 0 at primary T; no safety-critical FALSE_PASS;
no new systematic high-confidence FALSE_PASS mode; safe auto-decision coverage >= 0.20
at primary T; 3-run routing modal stability >= 0.95; transport success = 100%.
PROMISING requires: safety clean, and (coverage 0.10-0.20 OR routing modal stability
0.90-0.95 OR isolated non-safety FALSE_PASS only). Otherwise NOT_QUALIFIED.

After the first fresh label reveal: NO changes to questions, descriptions, choice enums,
thresholds, router, or redaction. V3 fails as it fails. Terminal status is exactly one of
JEV_NATIVE_FRESH_NOT_QUALIFIED / JEV_NATIVE_FRESH_PROMISING_NEEDS_MORE_EVIDENCE /
JEV_NATIVE_FRESH_QUALIFIED_FOR_SHADOW_ROUTING. No shadow routing implementation, no V4.
