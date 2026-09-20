# V1.6A Boundary Pre-Classifier

Deterministic, model-free boundary pre-classifier for the semantic judge
measurement system. Resolves route commitment, uncertainty behavior, and
assertion scope with high precision and explicit abstention; never produces
final verdicts. See boundary-preclassifier-design.md, rule-registry.json,
and boundary-label-contract.json.

Unit suite: 67 fixtures (RED evidence preserved in unit-test-results-red-run.json).
Run unit tests: python3 run_unit_tests.py --phase GREEN.

After freeze, the classifier must not be edited during official validation;
any post-freeze change invalidates the run (V1_6A_INVALID).

Terminal status: V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY. The route_commitment
family gate (precision >= 0.98) failed at 0.9778 on the official 120-fixture
one-shot (single false deterministic VR-H-08, an out-of-inventory service-noun
coverage probe). Engine stays frozen; the fix belongs in a NEW task. See
final-report.md for the full 50-item SLUTTRAPPORT and protocol deviations.
