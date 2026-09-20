# Reviewer Evidence Coverage - Stage 0 (read-only)

Generated: 2026-09-19T19:49:43Z
Gold corpus rows: 387  sha256 prefix: b85caaaa64f3393f

## Sources

- cost-qual-v1-screen: 90 rows
- cost-qual-v1-screen: 90 rows
- cost-qual-v1-screen: 90 rows
- cost-qual-v1-screen: 90 rows
- cost-qual-v2-screen: 90 rows
- cost-qual-v2-screen: 90 rows
- cost-qual-v1-transport-retry: 19 rows
- cost-qual-v1-transport-retry: 19 rows
- cost-qual-v1-transport-retry: 19 rows
- cost-qual-v1-transport-retry: 19 rows
- cost-qual-v1-transport-retry: 0 rows
- cost-qual-v2-transport-retry: 19 rows
- cost-qual-v2-transport-retry: 19 rows
- cost-qual-v2-transport-retry: 19 rows
- luna-qual-screen: 90 rows
- luna-qual-screen: 90 rows
- luna-qual-dualpass-A: 147 rows
- luna-qual-dualpass-A: 80 rows
- luna-qual-dualpass-B: 147 rows
- luna-qual-dualpass-B: 80 rows
- bai-v3-dualpass: 160 rows

## Registered incompatible / out-of-scope

- evaluation/judge-deepseek-v2-4-m2-validation (deepseek-v4.1-flash): INCOMPATIBLE_CONTRACT - different judge contract and calibration-fixture format; not row-level comparable against shared frozen gold
- evaluation/native-jev-qualification-v2 + native-jev-fresh-qualification-v3 (jev-1.13.0): OUT_OF_SCOPE_ROUTER_CANDIDATE - Jev is the router candidate under evaluation in this task, not a reviewer tier with comparable correctness evidence

## Per-model cell states (union universe 387 rows)

Model | CORRECT | INCORRECT | INVALID | TRANSPORT_ERROR | UNKNOWN
- bai-deepseek: 44 / 22 / 14 / 0 / 0
- gemma-4-26b-a4b-it: 0 / 0 / 0 / 19 / 0
- gemma-4-31b-it: 17 / 8 / 1 / 83 / 0
- laguna-s-2.1: 32 / 33 / 34 / 10 / 0
- ling-3.0-flash-sante: 26 / 18 / 41 / 24 / 0
- luna-high: 223 / 50 / 44 / 0 / 0
- luna-max: 53 / 14 / 23 / 0 / 0
- mimo-v2.5-pro: 30 / 11 / 66 / 2 / 0
- nemotron-3-ultra: 17 / 3 / 4 / 85 / 0
- nex-n2.5-pro: 42 / 18 / 43 / 6 / 0

## Gold family coverage (corpus rows)

- forbidden_no_match_unresolved: 202
- non_trigger_support: 77
- forbidden_match_negated: 32
- unresolved: 32
- trigger_support: 13
- critical:AMBIGUOUS_OR_CONFLICTING: 13
- forbidden_match_asserted: 6

## Family gaps

- forbidden_no_match_unresolved: 202 rows; correct per model: {"bai-deepseek": 0, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 11, "laguna-s-2.1": 13, "ling-3.0-flash-sante": 14, "luna-high": 155, "luna-max": 39, "mimo-v2.5-pro": 13, "nemotron-3-ultra": 13, "nex-n2.5-pro": 7}
- forbidden_match_asserted: 6 rows; correct per model: {"bai-deepseek": 0, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 1, "laguna-s-2.1": 0, "ling-3.0-flash-sante": 1, "luna-high": 3, "luna-max": 0, "mimo-v2.5-pro": 0, "nemotron-3-ultra": 0, "nex-n2.5-pro": 2}
- forbidden_match_negated: 32 rows; correct per model: {"bai-deepseek": 0, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 0, "laguna-s-2.1": 5, "ling-3.0-flash-sante": 5, "luna-high": 15, "luna-max": 6, "mimo-v2.5-pro": 4, "nemotron-3-ultra": 2, "nex-n2.5-pro": 8}
- unresolved: 32 rows; correct per model: {"bai-deepseek": 0, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 1, "laguna-s-2.1": 4, "ling-3.0-flash-sante": 0, "luna-high": 13, "luna-max": 1, "mimo-v2.5-pro": 3, "nemotron-3-ultra": 0, "nex-n2.5-pro": 6}
- trigger_support: 13 rows; correct per model: {"bai-deepseek": 4, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 2, "laguna-s-2.1": 1, "ling-3.0-flash-sante": 1, "luna-high": 5, "luna-max": 2, "mimo-v2.5-pro": 0, "nemotron-3-ultra": 0, "nex-n2.5-pro": 2}
- non_trigger_support: 77 rows; correct per model: {"bai-deepseek": 40, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 2, "laguna-s-2.1": 9, "ling-3.0-flash-sante": 5, "luna-high": 32, "luna-max": 5, "mimo-v2.5-pro": 10, "nemotron-3-ultra": 2, "nex-n2.5-pro": 17}
- critical:AMBIGUOUS_OR_CONFLICTING: 13 rows; correct per model: {"bai-deepseek": 0, "gemma-4-26b-a4b-it": 0, "gemma-4-31b-it": 0, "laguna-s-2.1": 0, "ling-3.0-flash-sante": 0, "luna-high": 0, "luna-max": 0, "mimo-v2.5-pro": 0, "nemotron-3-ultra": 0, "nex-n2.5-pro": 0}

## Key reading

- Only the 90-row screening core has broad multi-model coverage; Luna dual-pass extends Luna to the full labeled corpus.
- Forbidden MATCH/ASSERTED gold rows are the rarest family and historically under-covered by cheap tiers.
- NOT_RUN cells are coverage gaps, not model failures, and must not be read as stronger-model-required.
