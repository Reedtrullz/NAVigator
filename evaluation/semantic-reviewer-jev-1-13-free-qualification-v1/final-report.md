# JEV 1.13 Free Qualification V1 - Final Report

Task: NAV-EXPLORE-JEV-1.13-FREE-QUALIFICATION-V1
Date: 2026-09-19
Terminal status: JEV_PROVIDER_ACCESS_FAILED

## 1. Environment

- Working dir: /Users/reidar/Projectos/NAV Explore (not a git repository; state recorded as such in TASK-LOCK).
- Local OpenCodex proxy v2.58.0 healthy at 127.0.0.1:10100.
- OpenCode CLI v1.18.21 installed and authenticated (auth.json present in ~/.local/share/opencode).
- No production files were modified; no new code paths were added.

## 2. Provider / Model ID

- Cataloged provider: opencode-free (baseUrl https://opencode.ai/zen/v1, adapter openai-chat, no local API key by design).
- Cataloged model ID: jev-1.13-free.
- Present in OpenCodex config modelDiscovery.knownModels.opencode-free.ids, recentArrivals.opencode-free, and in OpenCode CLI v1.18.21 model listing as opencode/jev-1.13-free.
- Sibling aliases in CLI catalog: opencode/jev-1.13, opencode/jev-latest.

## 3. Invocation protocol attempts

All attempts are documented non-secretly in provider-access-evidence.json. Summary:

| Path | Result |
| --- | --- |
| Direct POST https://opencode.ai/zen/v1/chat/completions (no key) | HTTP 403 Cloudflare 1010 |
| Local proxy, model opencode-free/jev-1.13-free | HTTP 500 upstream_server_error (repeated) |
| Local proxy, unprefixed jev-1.13-free | HTTP 404 "does not exist (distributor)" |
| opencode-go subscription key, model jev-1.13-free | HTTP 400 "Model is unavailable." |
| Authorized OpenCode CLI: opencode run -m opencode/jev-1.13-free | No assistant output; log: AI_APICallError: Upstream request failed: Endpoint is unavailable. (repeated) |
| Diagnostic only: opencode/jev-1.13 | No output; Insufficient account funds |
| Diagnostic only: opencode/jev-latest | No output; Model is unavailable. |

The authorized-client route is the one the task explicitly permits ("free tier only from within OpenCode"). It reached provider routing, but the upstream endpoint for jev-1.13-free was unavailable on every attempt (12:00:58Z, 12:01:01Z, 12:01:06Z, 12:01:15Z, 12:05:54Z UTC).

## 4. Stop condition

The task's Phase 1 stop condition applies:

"If jev-1.13-free cannot actually be invoked through our OpenCode provider, STOP the Jev evaluation. Report JEV_PROVIDER_ACCESS_FAILED."

Zero successful model calls were achieved. No silent fallback was activated (AGENTS.md provider-fallback policy also forbids substituting an unannounced model). Accordingly:

- Phase 2 (adapter): not started - no runnable interface to adapt.
- Phase 3 (dataset selection): not started.
- Phases 4-12 (shadow evaluation, thresholds, metrics, calibration, comparison, routing simulation, cost, stability, report body): not started.
- No sealed-reserve data, gold, SUT, or history artifacts were touched.
- No Astra, Sol, Luna, GPT-5.5, or LongCat calls were made (0 across the board).

## 5. Answer to the task's core question

With current provider state: No - Jev 1.13 Free cannot currently be invoked at all, so it cannot make semantic judgments, its confidence cannot be calibrated, and no reviewer-call reduction can be measured.

## 6. What integration change is required

Provider-side, not local:

1. jev-1.13-free upstream endpoint must become available through the authorized OpenCode client, or
2. the OpenCode account must gain funded/authorized Jev access (the jev-1.13 paid alias currently reports Insufficient account funds).

Until one of these changes, a local adapter cannot succeed regardless of implementation quality.

## 7. Limitations and non-claims

- Catalog presence is not availability: all three Jev aliases were listed but none served a single completion during this window.
- The diagnostic paid-alias probe (jev-1.13) was run only to characterize the failure and was never used as a substitute.
- No accuracy, latency, cost, or stability numbers exist for Jev; none are claimed.
- No threshold, routing, or cost conclusions are drawn.
- Provider state may change; a re-check is required before any future Jev attempt.

## 8. Recommendation

Do not build the Jev adapter now. If Jev should be revisited:

1. Confirm the upstream endpoint serves completions through "opencode run -m opencode/jev-1.13-free" (single OK-ping) after provider/account remediation.
2. Only then re-open a new bounded qualification lineage with the same phases.

Hard stop. No further work is authorized in this lineage.
