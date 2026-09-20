# dev-corpus-semantic-judge-v1-6b

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6B-RESCREEN

Terminal status: **V1_6B_NO_JUDGE_QUALIFIES**

One-shot rescreen of two preregistered judge candidates (LongCat-2.0,
MiMo v2.5 Pro) over 120 fresh fixtures through the frozen deterministic +
V1.6A.3 pre-classifier pipeline. Both candidates failed the frozen one-shot
floors; per contract, no best-of-bad selection, no stability screen, no
V1.6C.

Key artifacts:

- final-report.md - full terminal report
- screening-results-longcat-2-0-free.json - LongCat one-shot results (gates FAIL)
- screening-results-mimo-v2-5-pro.json - MiMo Pro one-shot results (gates FAIL)
- burned-data-registry.json - what is now burned and why
- run_stability_v1_6b.py - stability runner (fail-closed; never triggered)
- TASK-LOCK.json - terminal task lock
- curator-pass1/2.json, annotation-qa.json, disputed-fixture-registry.json,
  preclassifier-screening-results.json, candidate-comparison.json -
  packaging artifacts mechanically derived post-terminal from the frozen
  gold/checkpoint/result files (no new judgment); see final-report.md
  Packaging note

Pipeline components remain frozen and unmodified: V1.6A.3 pre-classifier
engine (21047fda...f2563b), V1.4 judge core, V1.4 semantic contract.

Intentionally absent: selected-judge-for-v1-6c.json. No candidate passed
the frozen gates, so no selection was made.

Post-terminal diagnostic artifacts (DIAGNOSTIC_ONLY, burned-data
debugging; no stage started): failure-taxonomy-diagnostic.json,
next-stage-design-brief-diagnostic.md, and the ready-to-run draft task
prompt next-task-draft-prompt-v1_6a4.md (DRAFT ONLY - awaiting
explicit user authorization).
