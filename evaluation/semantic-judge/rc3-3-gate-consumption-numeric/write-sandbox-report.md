# Write sandbox report

## Policy

All task writes are confined to
evaluation/semantic-judge/rc3-3-gate-consumption-numeric/.

Forbidden write targets (hard fail):

- rc2-development/
- rc3-1-proof-semantics/ (including the sealed validation tree)
- rc3-1-support-boundary/
- rc3-1-relation-repair/
- rc3-2-boundary-aware-relation/
- rc3-generalization-holdout/ (RC3G)
- any path outside the task root (traversal)
- Obsidian vault

Reads outside the task root are allowed (KB files, frozen lattices,
legacy runners with explicit task-local outputs).

## Implementation

sandbox_guard.py in this task directory exposes
assert_writable(path), which resolves the absolute path and fails
unless it is inside the task root. It additionally rejects resolved
paths that land in any forbidden tree even under symlink or ..
traversal. The --output handler in this task's runner validates every
requested output through the guard before any file is created.

## Tests

test_sandbox_guard.py proves:

1. A write attempt to the RC3.1 source engine path FAILS.
2. A write attempt to the RC3.2 task directory FAILS.
3. A traversal attempt (task_dir/../../rc3-1-support-boundary/x)
   FAILS after resolution.
4. A write inside the task root SUCCEEDS.

No historical file is modified by these tests; the guard rejects the
attempt before any filesystem mutation is attempted.
