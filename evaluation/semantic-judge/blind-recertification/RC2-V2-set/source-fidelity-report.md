# Source fidelity report - RC2 blind set V2 construction

Method: deterministic checker (validation/source_fidelity.py, spec 28). Excerpts are canon-normalized for whitespace only; any other deviation from knowledge-base bytes fails.

| Wave | Candidates checked | Verbatim excerpts | File refs valid | Failures |
|---|---|---|---|---|
| a1 | 32 | 32 | 32 | 0 |
| a2 | 34 | 34 | 34 | 0 |
| b1 | 40 | 40 | 40 | 0 |
| c | 48 | 48 | 48 | 0 |
| d | 65 | 65 | 65 | 0 |
| e | 58 | 58 | 58 | 0 |
| Total | 277 | 277 | 277 | 0 |

Result: all_pass = true for every wave. Every retained case excerpt exists verbatim in the referenced knowledge-base file.

Construction-session follow-up verification: all 303 source spans referenced across the full 277-case pool were re-resolved byte-identical against the knowledge base. The 160-case public blind set (blind-cases.json) resolves against the same KB refs with matching line spans. KB content was not modified during this task (spec: no KB changes).
