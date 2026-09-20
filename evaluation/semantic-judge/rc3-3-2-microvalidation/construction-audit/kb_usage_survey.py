#!/usr/bin/env python3
"""Survey which KB files prior evaluator corpora consumed (novelty planning only)."""
import json, re
from pathlib import Path
from collections import Counter
SEM = Path('/Users/reidar/Projectos/NAV Explore/evaluation/semantic-judge')
corpora = {
 'rc33-targeted': SEM/'rc3-3-1-residual-contradiction/fresh-targeted-cases.json',
 'rc33': SEM/'rc3-3-gate-consumption-numeric/fresh-cases.json',
 'rc32': SEM/'rc3-2-boundary-aware-relation/fresh-architecture-cases.json',
 'rc31-relation': SEM/'rc3-1-relation-repair/fresh-relation-cases.json',
 'rc31-boundary': SEM/'rc3-1-support-boundary/fresh-boundary-cases.json',
 'rc3g': SEM/'rc3-generalization-holdout/generalization-cases.json',
}
tally = Counter()
for name, p in corpora.items():
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    cases = d.get('cases', d if isinstance(d, list) else [])
    for c in cases:
        for s in c.get('sources', []):
            kb = s.get('kb_ref','')
            kb = re.sub(r'^kb/','',kb)
            tally[kb] += 1
for kb, n in sorted(tally.items()):
    print(f'{n:4d}  {kb}')
