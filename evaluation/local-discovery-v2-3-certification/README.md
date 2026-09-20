# V2.3 Candidate Certification

Task: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION

Adjudication-only certification of the frozen V2.3 site-direct-only runtime
candidate. No runtime, protocol, provider-config, or candidate changes; no
fresh municipalities; no external search.

Terminal status: V2_3_CERTIFICATION_FAIL_RUNTIME_CHANGE_REQUIRED.

Root cause of the three failed gates: runtime/discovery_v2/roots.py constructs
the platform root as https://<slug>.bedinnsats.no/ while the frozen config,
docstring, and gold corpus specify bedreinnsats.no. All nine Raelingen
benchmark failures trace to this runtime implementation defect; probe evidence
shows the authoritative host ralingen.bedreinnsats.no was reachable and served
content usable by the frozen provider logic.

Read candidate-certification.json for the terminal status, gate outcomes, and
root cause. final-report.md answers the task doc's 53-point sluttrapport.

Artifacts:

- TASK-LOCK.json - task lock and terminal status
- candidate-integrity.json - manifest/config/protocol SHA verification
- historical-integrity-adjudication.md - write-incident restoration record
- source-availability-adjudication-contract.md - frozen before probes
- source-availability-results.json - adjudication gate outcome (FAIL)
- probe-evidence-raw.json / probe-evidence-nav.json - durable probe copies
- benchmark-certification.json - 117/108/9 preserved + adjudication
- replay-certification.json - clean replay 22/22
- live-burned-certification.json - live burned re-run 12/13 complete
- test-report.md - 130/130 across V1/V2/V2.1/V2.2/V2.3
- security-report.md - credential and secret handling PASS
- network-call-audit.json - external search calls = 0
- candidate-certification.json - terminal status + gates
- final-report.md - 53-point sluttrapport
