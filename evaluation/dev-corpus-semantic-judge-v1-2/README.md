# Dev Corpus Semantic Judge V1.2

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_2-UNCERTAINTY-CONTRACT-REPAIR
Prior: SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY (V1.1 lineage)
Terminal status: **SEMANTIC_JUDGE_V1_2_ANNOTATION_CONTRACT_NOT_READY**

Human uncertainty contract repaired and calibrated (Set B 20/20), contract
and prompt frozen, fresh official 80-fixture set built and dual blind
labeled at 70/80 = 87.5% (gates require >=95% overall, >=95% route,
>=95% uncertainty). Official model validation NOT started.

Entry points:
- final-report.md - terminal report with gates, root causes, non-claims
- semantic-judge-contract-v1-2.json - frozen contract (uncertainty
  applicability-first schema, 4-point clarification embedded)
- prompt-freeze-v1-2.json - frozen judge prompt hash
- fixture-design-rules.md + uncertainty-contract-clarification.md - frozen
  design/clarification docs
- judge-validation-fixtures-v1-2.json + annotation-agreement-v1-2.json -
  official fixtures and the failing agreement result
- judge-validation-gold-v1-2.UNFROZEN.json - NOT frozen gold (gate failed)
- burned-data-registry.json - V1.1 80-set and calibration sets burned

Historical V1/V1.1 artifacts untouched (17/17 baseline SHAs verified at
close). No scorer freeze, no Phase B, no runtime changes, no product
holdout in this lineage.
