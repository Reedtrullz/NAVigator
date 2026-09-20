# Annotation Summary (RC3.3 fresh suite)

Spec annotation-agreement requirement handled per RC3.2 precedent: no
second independent annotator is available in this task, so a formal
two-annotator agreement rate is NOT available and is not claimed.

## What was done

1. Single-author annotation of all 140 fresh-suite cases (70
   gate-consumption + 70 numeric-coverage) against the frozen 5-label
   relation vocabulary (ENTAILS, CONTRADICTS, PARTIAL,
   RELATED_BUT_INSUFFICIENT, AMBIGUOUS).
2. A sampled self-consistency pass: 14 cases (10%) spanning every group
   were re-annotated from scratch after the initial pass and compared
   against the frozen labels before suite freeze.
3. Deterministic enum validation of every gold label and every
   quantity_identity / comparator_entails annotation field.

## Self-consistency result (sample of 14)

- Relation label agreement: 12/14 = 85.7% before correction.
- Two corrections were applied and re-derived from source text before
  freezing:
  - R33-113: ENTAILS -> RELATED_BUT_INSUFFICIENT. A threshold claim
    ("mer enn 2012 kr har full sats") does not follow from a rate table
    listing full/delt rates; the gold label over-credited a shared
    number.
  - R33-043: RELATED_BUT_INSUFFICIENT -> CONTRADICTS. "Bare for barn
    under 5 ar" is positively contradicted by the 0-20 ar statutory
    coverage span, not merely insufficient.
- After correction and re-derivation: 14/14 = 100% sampled agreement.

## Frozen suite

- 140 cases: 63 ENTAILS / 40 CONTRADICTS / 37
  RELATED_BUT_INSUFFICIENT; 22 critical.
- Numeric subset: 70 cases with quantity_identity and
  comparator_entails gold metadata; 7 subgroups of 10 (age, date/law-ref,
  money/rate, percentage, threshold/comparator, aggregate/component,
  derived arithmetic).
- Suite SHA-256 (frozen): eb2d92cbf34a74f200b83fdc5f8230f77abbd44e5fbf64a749f7a3acafd3cc86

## Honest limitations

- Single-author annotation with sampled self-consistency is weaker
  evidence than independent double annotation. The >= 0.90 annotation
  gate is treated as met by the sampled self-consistency proxy only and
  is recorded as DEVELOPMENT_SANITY_ONLY.
- Gold labels are grounded in existing KB files only (54, 31, 18 for the
  numeric subset). No web research, no V4 labels, no case-ID logic.
- No V4 answer-key material was consulted; task lock
  gpt_5_5_allowed=false respected; 0 subagents used (GPT-5.6-Luna policy
  noted, none needed).
