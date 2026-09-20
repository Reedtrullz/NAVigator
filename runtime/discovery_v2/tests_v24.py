"""V2.4 root-resolution regression tests (new lineage, TDD).

RED expectation before roots_v24.py exists: importing the module fails, and
the honest failure is the missing V2.4 lineage itself, not a passing test.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.discovery_v2.roots import canonical_roots  # noqa: E402


class TestRootResolutionV24(unittest.TestCase):
    def test_v24_module_exists(self):
        import runtime.discovery_v2.roots_v24 as m  # noqa: F401

    def test_raelingen_canonical_platform_root(self):
        from runtime.discovery_v2.roots_v24 import canonical_roots_v24
        roots = canonical_roots_v24("Rælingen")
        self.assertIn("https://ralingen.bedreinnsats.no/", roots)
        self.assertNotIn("https://ralingen.bedinnsats.no/", roots)

    def test_synthetic_slug_generalization(self):
        from runtime.discovery_v2.roots_v24 import canonical_roots_v24
        roots = canonical_roots_v24("Sør-Trøndelag Syndtest")
        platform = [r for r in roots if "bedreinnsats" in r]
        self.assertEqual(platform, ["https://sor-trondelag-syndtest.bedreinnsats.no/"])
        self.assertFalse(any("bedinnsats" in r for r in roots))

    def test_kommune_no_variants_unchanged(self):
        from runtime.discovery_v2.roots_v24 import canonical_roots_v24
        roots = canonical_roots_v24("Hasvik")
        self.assertEqual(roots[:2], ["https://www.hasvik.kommune.no/",
                                     "https://hasvik.kommune.no/"])
        self.assertTrue(roots[-1].endswith("bedreinnsats.no/"))


if __name__ == "__main__":
    unittest.main()
