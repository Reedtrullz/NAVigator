import unittest

from score_generalization_frozen import exact_metric


class FrozenScorerTests(unittest.TestCase):
    def test_exact_semantic_metric_counts_only_matching_cases(self):
        prediction = {"case_id": "C1", "semantic_verdict": "SUPPORTED", "runtime_status": "OK"}
        truth = {"semantic_verdict": "SUPPORTED"}
        result = exact_metric([prediction], [truth], "semantic_verdict")
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["denominator"], 1)


if __name__ == "__main__":
    unittest.main()
