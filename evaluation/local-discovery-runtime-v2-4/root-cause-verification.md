# Root-Cause Verification (task section 4) - no code change

## Reproduction

Import smoke test of the historical resolver (runtime/discovery_v2/roots.py,
SHA e2ee31ee...abdf0bf) on this machine, before any edit:

- Input: municipality = Raelingen (Rælingen)
- Historical resolver produces as its platform root:
  https://ralingen.bedinnsats.no/

Expected canonical platform root, per the frozen V2.3 provider config
root_candidates list, the roots.py docstring, the burned/gold corpus domain
(ralingen.bedreinnsats.no), and the V2.3 certification probe evidence:

- https://ralingen.bedreinnsats.no/

## Expected-suffix corroboration (4 independent sources)

1. Frozen config: evaluation/local-discovery-site-direct-only-v2-3/provider-config-v2-3.json lists "https://<slug-ae-compressed>.bedreinnsats.no/" in root_candidates.
2. Docstring: runtime/discovery_v2/roots.py states "<slug>.bedreinnsats.no" as the secondary platform pattern.
3. Burned/gold corpus: evaluation/local-discovery-provider-arch-v2/benchmark-corpus.json contains ralingen.bedreinnsats.no gold URLs.
4. Certification evidence: evaluation/local-discovery-v2-3-certification/probe-evidence-raw.json records ralingen.bedreinnsats.no DNS stable x2, root HTTP 200 (176590 B), sitemap 200, gold PDF 200 (2022924 B), and frozen nav-link logic returning 2 keyword-passing links on that root.

## Conclusion

ROOT CAUSE REPRODUCED. The historical resolver constructs the platform root
from the literal string "bedinnsats.no" while every authoritative source
specifies "bedreinnsats.no". Task proceeds to new-lineage TDD.
