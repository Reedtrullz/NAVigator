# Historical Integrity (before-state)

## Verified at task start

| Artifact | SHA-256 | Status |
|---|---|---|
| rc3-3 engine_local/engine.py | fb6f943f8b90eed46003f57168914c877fa11482c5c581885d067923986f9b20 | MATCH RC3.3 freeze |
| rc3-3 engine_local/numeric.py | 9e76fb9c70f5942d6c7751a640f1e56d621bc738a6f5aa1c24bf8b60c8a958d4 | MATCH RC3.3 freeze |
| rc3-3 engine_local/boundary.py | 9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c48c3ef026343fc1e | MATCH RC3.3 freeze |
| rc3-1 sealed validation | 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159 | UNCHANGED, not opened |

## RC2 official history

RC2_NOT_CERTIFIED remains permanent and immutable. No RC2 artifact is
modified by this task. Blind V4 data stays BURNED_DEVELOPMENT_ONLY and is
used only for forensic regression, never as an optimization target.

## Write protection

All writes are restricted to
evaluation/semantic-judge/rc3-3-1-residual-contradiction/. A full SHA-256
snapshot of the six historical task directories (172 files) was recorded to
results/integrity-before.json before any runtime change. An after-state
diff is required at task close (HISTORICAL_FILES_MODIFIED must be 0).
