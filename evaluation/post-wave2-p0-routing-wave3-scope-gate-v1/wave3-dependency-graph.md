# Wave-3 Dependency Graph

W3-RC-A: Structured route-proposition construction + evidence binding  [PRIMARY]
  |
  +-> unblocks: 89 R0 criteria + 19 R1 criteria (route funnel reaches R2+ semantics)
  +-> enables:  meaningful RC-10 semantic-support check (evidence now has a target)
  +-> enables:  RC-04 uncertainty re-assessment (product shape stable)
  +-> reduces:  structured/prose divergence that triggered the R3 scorer rule
  |
  +-[independent]- W3-RC-B: Renderer block dedup (can run after A; low risk)
  |
Measurement-lane (separate owner authorization, NOT Wave-3 SUT work):
  M-SENS-1 R3 condition-awareness    depends on: RC-A landed (re-baseline before touching scorer)
  M-SENS-2 CERTAINTY_MARKERS         independent of RC-A
  M-SENS-3 route paraphrase judge    depends on: RC-A + judge-capability decision
  RC-04 uncertainty depth            depends on: RC-A

Order rationale: route construction is the only repair that moves the dominant bottleneck (89/108).
Scorer changes must come after re-baselining, or measurement drifts into tuning territory.
