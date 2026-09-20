"""Discovery runtime V2: provider architecture layer.

V2 replaces the single external search dependency with a composite
discovery provider (site-direct first, budgeted external fallback). Route
semantics, classification, and the frozen protocol are reused unchanged
from runtime.discovery (V1).
"""
