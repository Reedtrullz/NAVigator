"""Phase 2 runner integration tests: port of Phase 1 test_runner.py."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUNNER_DIR = os.path.abspath(os.path.dirname(__file__))

GOLD_FIELDS = [
    "acceptable_routes",
    "forbidden_claims",
    "required_uncertainty",
    "required_evidence_fields",
    "critical_error_if",
]


def _run_cli(corpus_name, out_dir):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.dirname(RUNNER_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [
            sys.executable, "-m", "sut_runner.run",
            "--corpus", os.path.join("evaluation", "dev-corpus-v1", "cases", corpus_name),
            "--out", out_dir,
            "--mode", "replay",
        ],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return proc


class TestRunnerFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp(prefix="sut-phase2-test-")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def _run(self, corpus):
        out = os.path.join(self.base, corpus.replace(".json", ""))
        proc = _run_cli(corpus, out)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        return out, proc

    def test_safety_freeze(self):
        out, proc = self._run("safety_cases.json")
        self.assertIn("FULL_SUT", proc.stdout)
        preds = sorted(os.listdir(os.path.join(out, "predictions")))
        self.assertEqual(len(preds), 20)
        manifest = json.load(open(os.path.join(out, "predictions-manifest.json")))
        self.assertEqual(manifest["prediction_count"], 20)
        self.assertEqual(manifest["artifact"], "sut-predictions-manifest-v1-phase2")
        self.assertEqual(manifest["harness_version"], "sut_runner/2.0-phase2")
        for entry in manifest["predictions"]:
            path = os.path.join(out, "predictions", entry["file"])
            self.assertEqual(
                hashlib.sha256(open(path, "rb").read()).hexdigest(),
                entry["sha256"],
            )

    def test_routing_freeze(self):
        out, _ = self._run("routing_cases.json")
        preds = os.listdir(os.path.join(out, "predictions"))
        self.assertEqual(len(preds), 75)

    def test_discovery_freeze(self):
        out, _ = self._run("discovery_adversarial_cases.json")
        preds = os.listdir(os.path.join(out, "predictions"))
        self.assertEqual(len(preds), 25)

    def test_run_log_has_stage_state_latency(self):
        out, _ = self._run("safety_cases.json")
        lines = open(os.path.join(out, "run-log.jsonl"), encoding="utf-8").read().splitlines()
        self.assertEqual(len(lines), 20)
        rec = json.loads(lines[0])
        self.assertIn("case_id", rec)
        self.assertIn("stages", rec)
        self.assertIn("total_latency_ms", rec)
        self.assertIn("execution_status", rec)
        stages = rec["stages"]
        self.assertEqual(len(stages), 11)
        for s in stages:
            self.assertIn("stage", s)
            self.assertIn("state", s)
            self.assertIn("latency_ms", s)

    def test_no_gold_fields_in_any_prediction(self):
        out, _ = self._run("routing_cases.json")
        pred_dir = os.path.join(out, "predictions")
        leaks = []
        for name in os.listdir(pred_dir):
            blob = open(os.path.join(pred_dir, name), encoding="utf-8").read()
            for field in GOLD_FIELDS:
                if '"%s"' % field in blob:
                    leaks.append((name, field))
        self.assertEqual(leaks, [])

    def test_no_secrets_in_outputs(self):
        out, _ = self._run("safety_cases.json")
        for root, _dirs, files in os.walk(out):
            for name in files:
                blob = open(os.path.join(root, name), encoding="utf-8").read().lower()
                for marker in ("api_key", "password", "bearer", "token="):
                    self.assertNotIn(marker, blob, (name, marker))

    def test_mode_recorded_in_manifest(self):
        out, _ = self._run("safety_cases.json")
        manifest = json.load(open(os.path.join(out, "predictions-manifest.json")))
        self.assertEqual(manifest["mode"], "replay")
        self.assertIn("sut_component_shas", manifest)
        self.assertIn("corpus_sha256", manifest)


if __name__ == "__main__":
    unittest.main()
