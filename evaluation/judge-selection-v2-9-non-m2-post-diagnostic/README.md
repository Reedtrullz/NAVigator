# Judge Selection V2.9 - Non-M2 Post-Diagnostic Screening

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_9-NON-M2-POST-DIAGNOSTIC-SCREENING

Terminal status: V2_9_NO_NON_M2_JUDGE_QUALIFIES

## What this was

One-shot screening of two owner-authorized candidates (opencode-go/deepseek-v4.1-flash,
command-code/xiaomi/mimo-v2.5-pro) on a fresh 180-fixture benchmark built after the
V2.8 post-terminal diagnostic showed shared overcommitment on contract-mandated
UNRESOLVED boundaries. LongCat 2.0 and GPT-5.5 were excluded. Deterministic-resolved
fixtures (80/180) bypass the judge by construction; 100 semantic residuals were judged
per candidate. No reruns. No gate edits. No best-of-bad selection.

## Result

Both candidates failed the frozen gates. DeepSeek passed overall (96.1%), forbidden
(100%), and route (96.7%) gates but failed uncertainty (91.7% < 95%) and the uncertainty
repair subset (79.2% < 95%, 5 UNRESOLVED-to-PARTIAL confusions). MiMo Pro failed overall
(92.2%), route (91.7%), uncertainty (86.7%), structured-validity (two transport/schema
invalid rows, no reruns), and repair (70.8%). Both committed overcommitments on gold-UNRESOLVED rows
(DeepSeek 5, MiMo 8) despite UNRESOLVED-forcing prompt additions; report-only metric.

No stability runs: the spec restricts stability to qualifying candidates.

## Key files

- final-report.md - full terminal report
- combined-scores.json - frozen gate evaluator output (authoritative metrics)
- screening-gold.json - frozen gold (embedded SHA re-verified)
- deterministic-prepass-results.json - deterministic/residual partition
- uncertainty-repair-subset-report.json - V29-UNC-25..48 repair subset
- overcommitment-report.json - report-only trap metric
- baseline-integrity.json - SHA pin verification incl. embedded-canonical re-verification
- burned-data-registry.json - burned data registration
- prompt-freeze-v2-9.json - frozen prompt (iteration 2 of 3)
- TASK-LOCK.json - task lock with terminal status

Predecessor lineages (V2.8, V2.8 post-repair, V2.7D/E, V2.6, V2.3, V2.2) remain
unchanged. The V2.8 diagnostic basis is copied into diagnostic-basis.md; the V2.8
final report remains authoritative for that finding.
