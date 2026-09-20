# V1.3M Migration Rationale

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3M-MIMO-MIGRATION

The V1.3 boundary-clarification lineage (GPT-5.6-Luna) never reached semantic
evaluation: all 64 Set A annotation calls failed with HTTP 429
account-usage-window errors before any label output. Zero valid semantic
observations exist, so Set A is semantically unburned and reusable unchanged.

The user explicitly authorized migrating the judge model from GPT-5.6-Luna to
commandcode-auth mimo-v2.5. Per the frozen V1.3 resume policy this model switch
would otherwise be forbidden; the authorization is the sole reason it happens.

## Why Set A may be reused

The 64 failed Luna calls were transport observations, not label observations:

- every request was rejected with HTTP 429 before any model verdict was
  delivered;
- no partial label output exists (label1/label2/agreement files were never
  written; only the transport-failure log is preserved in the V1.3 lineage);
- Set A has not influenced any semantic judge repair after model results.

Therefore VALID_LUNA_LABELS_OBSERVED = 0 and reusing Set A byte-identically
introduces no contamination.

## What changes and what does not

Changed: judge model binding only (openai/gpt-5.6-luna ->
command-code/xiaomi/mimo-v2.5), a mechanical zero-gate guard bug in the
copied runner (stray unary + tokens; behavioral no-op otherwise), and
adapter-level max_tokens 120 -> 2000 (transport headroom only; mimo-v2.5
exhausted 120 completion tokens with finish_reason=length and empty content
before emitting JSON, reproduced deterministically on synthetic input; prompt
semantics, output schema and labels untouched).

Unchanged: semantic contract, uncertainty-requirement modes, route-commitment
semantics, score labels, decision trees, both instruction phrasings, fixture
bytes, order, temperature, retry policy (one 30s transport-only backoff),
fail-closed schema guards, deterministic-first invariant.
