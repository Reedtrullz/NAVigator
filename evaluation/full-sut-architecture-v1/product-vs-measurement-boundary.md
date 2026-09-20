# Product vs Measurement Boundary

Hard rule:

    PRODUCT SUT != MEASUREMENT SYSTEM

Measurement components are evaluator-side and MUST NOT become runtime
dependencies of the product just because they exist in the same repo.

## Classification of existing components

| Component | Path | Side |
|---|---|---|
| Dev corpus scorer v1 | evaluation/dev-corpus-scorer-v1/ | evaluator |
| Combined measurement V3 engine | evaluation/measurement-v3-combined-freeze/ | evaluator |
| M2 human-review lane | measurement-v2-6 lineage (frozen) | evaluator |
| Uncertainty human-review lane | measurement-v2-12 lineage (frozen) | evaluator |
| Generic semantic human-review lane | measurement-v2-15 lineage (frozen) | evaluator |
| Dev corpus 120 cases (with gold) | evaluation/dev-corpus-v1/ | evaluator |
| Local discovery runtime V1 | runtime/discovery/ | product (frozen component) |
| Local discovery V2.4/V2.5 candidates | runtime/discovery_v2/ | product (frozen candidates) |
| Discovery result schema | data/local-discovery-runtime-result-v1.schema.json | product |
| Knowledge artifacts 00-75 | repo root and subfolders | product (data) |
| Gap register | 69-kunnskapshullregister.md | product (data, fail-closed) |

## Direction of dependency

    SUT runner (evaluator-side tool)
      -> gold-stripped case
      -> PRODUCT pipeline (the SUT)
      -> raw structured output
      -> frozen prediction files
      -> scorer + measurement V3 (evaluator)

The product pipeline imports runtime/discovery and reads knowledge artifacts.
It never imports evaluation/. The runner and loader live on the evaluator side
of the boundary but execute the product; scoring happens only after prediction
freeze.

## Gold and gold-blindness

- Gold lives in evaluation/dev-corpus-v1/cases/*.json under each case's
  gold key.
- The loader strips gold before the SUT sees the case.
  GOLD_VISIBLE_TO_SUT = 0 is a hard invariant (corpus-loader-design.md).
- The scorer reads gold; the SUT cannot.

## Human review

Human review in this repo is a MEASUREMENT mechanism: the M2 lane (critical
conditions), the uncertainty lane, and the generic V2.15 four-dimension lane
are how humans adjudicate what automation cannot. They are evaluator-side.

Product-side human review is NOT a current requirement and is NOT introduced
by this architecture. If the product later needs an operator queue (for
example, safety-edge cases), that is a separate owner decision and a separate
task; the SUT output schema already carries safety priority and failure state,
so an operator surface could be added without schema surgery.

## M2-workflow classification

Which cases enter the M2 lane is a property of case + measurement policy, not
of SUT behavior. It stays evaluator-side. The corpus files may later gain
explicit M2 routing metadata, but that is an evaluator task; the SUT neither
knows nor uses it.
