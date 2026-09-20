# RC2 Blind Set V4 (NAV-EXPLORE-RC2-BLIND-V4)

Re-sealed blind certification set for NAV-EXPLORE-EVALUATOR-RC2. Case content is
byte-identical to V3 (same 160 CORE + 122 reserve); only answer-key construction
changed.

## Files

- `blind-cases.json` / `blind-cases.schema.json` - public blind cases, no labels,
  byte-identical to V3
- `blind-manifest.json` - sanitized manifest (no case IDs, no expected verdicts)
- `phase1-firewall-manifest.json` - Phase-1 allowlist, forbidden paths, firewall status
- `answer-key.sealed` - AES-256-GCM sealed answer key (160 CORE, 62 compound with
  141 complete atoms)
- `construction-audit.sealed` - AES-256-GCM sealed construction evidence (passes,
  adjudication, consistency, relabel details)
- `v4_qa.py` + `qa-tests/` - construction QA (live leak gate + 7 regressions)
- `label-leakage-inventory.json` - full-project leak scan findings
- Docs: `annotation-atom-summary.md`, `certification-metrics.md`,
  `future-certification-protocol.md`, `leakage-audit.md`, `construction-qa-report.md`,
  `final-report.md`

## Rules

- RC2 must never run on this set outside the Phase-1 prediction run
  (`rc2_executed` = false).
- The V4 key is memory-only, delivered once to the owner; never in prompt, env,
  shell, repo, or Phase-1 context.
- The V3 key is RETIRED and was not reused (fingerprint checked).
- Phase 1 reads only the four allowlisted V4 files plus the frozen RC2 runtime,
  in a fresh session, without the key.
