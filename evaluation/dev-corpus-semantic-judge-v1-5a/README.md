# Semantic Judge V1.5A - Model Selection

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_5A-MODEL-SELECTION

Burned model-selection task on the frozen V1.4 judge contract and the
100 burned V1.4 official fixtures. The V1.4 mimo-v2.5 official run
(overall 0.8265) is the frozen baseline and is never rerun.

Candidates benchmarked (all user-authorized, one execution per fixture):
LongCat 2.0, MiMo v2.5 Pro, Ling 3.0 Flash Sante, Laguna S 2.1.
Authorization amendment (wire ids, second user message):
authorization-amendment.json.

TERMINAL STATUS: V1_5A_NO_MODEL_MEETS_SELECTION_FLOOR.
No model passed the selection floors (best: MiMo v2.5 Pro, overall 0.84
vs floor 0.95). No stability screen, no model selected, nothing eligible
for V1.5B. See final-report.md and candidate-comparison.json.
