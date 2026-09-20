# Source Integrity

Runtime for baseline and implementation is the task-local copy of the RC3.3
engine: evaluation/semantic-judge/rc3-3-gate-consumption-numeric/engine_local/
(read-only import; never edited in place). The RC3.3.1 copy is created inside
this task directory only after contract freeze. Gate 0 verified py_compile,
actual import, runtime path, engine/numeric/boundary SHAs (matching the RC3.3
freeze exactly), Python 3.14.6, C0 control-character scan (clean), and a
write-sandbox probe (PASS).

The frozen 140-case suite (fresh-cases.json, SHA eb2d92cb6353121db917f7223c9a354588814bd42bf86d096dc24445b22c4d1) is burned development data for regression only.
The sealed 60-case validation remains sealed for the whole task (hash check
before and after; never decrypted, inspected, executed, or scored).
