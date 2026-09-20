# RC2 Runtime Bug Audit (RC1B-0112)

## Minimal reproduction

polarity_engine.py line 474 (v0.1 module) executed
set(_actor_tokens(atom_text).values()). _actor_tokens returns a set,
and sets have no .values() -> AttributeError on any claim reaching
the actor-family division check ("Foreldre kan kontakte PPT pa eget
initiativ ...").

## Fix (Iteration A, generalized)

- set(_actor_tokens(atom_text).values()) ->
  set(_actor_tokens(atom_text)) (iterate the set itself).
- Runtime robustness cases added: actor-family repro, missing fields,
  weird punctuation, empty claim (runtime_robust group, all pass).

## Result

- 0112 now SUPPORTED (correct; direct + battery verified).
- Engine-layer runtime failures across the 120-row burned rerun: 0.
- Official RC1 outcome for RC1B-0112 remains a recorded failure; RC1
  artifacts untouched.

