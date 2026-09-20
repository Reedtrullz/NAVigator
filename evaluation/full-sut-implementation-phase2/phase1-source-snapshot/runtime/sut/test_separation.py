import os
import ast
import unittest


SUT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SUT_DIR))


class TestProductEvaluatorSeparation(unittest.TestCase):
    """Hard invariant: PRODUCT SUT must not import evaluation/."""

    def test_no_evaluation_imports_in_sut_sources(self):
        offenders = []
        for root, _dirs, files in os.walk(SUT_DIR):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        mods = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        mods = [node.module or ""]
                    else:
                        continue
                    for mod in mods:
                        if mod == "evaluation" or mod.startswith("evaluation."):
                            offenders.append(path)
        self.assertEqual(offenders, [], "product SUT references evaluation/: %s" % offenders)

    def test_sut_package_does_not_touch_evaluator_dirs(self):
        # sys.modules proof: importing the SUT package must not pull in the
        # evaluator harness package.
        import importlib
        import sys

        for mod in list(sys.modules):
            if mod.startswith("sut_runner"):
                del sys.modules[mod]
        importlib.import_module("sut.pipeline")
        self.assertNotIn("sut_runner", sys.modules)

    def test_evaluator_harness_is_outside_product_tree(self):
        sut_root = os.path.dirname(SUT_DIR)  # runtime/
        harness = os.path.join(REPO_ROOT, "evaluation", "full-sut-implementation", "sut_runner")
        self.assertTrue(os.path.isdir(harness))
        self.assertFalse(os.path.commonpath([sut_root, harness]).startswith(sut_root))


if __name__ == "__main__":
    unittest.main()
