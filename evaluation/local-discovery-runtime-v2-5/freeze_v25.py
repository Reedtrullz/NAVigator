"""One-shot freeze driver for the V2.5 candidate.

Hashes all candidate components, writes candidate-runtime-v2-5/
manifest.json + hashes.txt. The candidate SHA is the SHA-256 of the
manifest file itself (V2.4 convention). Run once at freeze time.
"""

import hashlib
import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V25 = REPO / "evaluation" / "local-discovery-runtime-v2-5"
CAND = V25 / "candidate-runtime-v2-5"

components = {
    "protocol_v1": "runtime/discovery/protocol.py",
    "providers_v25": "runtime/discovery_v2/providers_v25.py",
    "classification_gate_v25": "runtime/discovery_v2/classification_gate_v25.py",
    "classification_v25": "runtime/discovery_v2/classification_v25.py",
    "orchestrator_v25": "runtime/discovery_v2/orchestrator_v25.py",
    "cli_v25": "runtime/discovery_v2/cli_v25.py",
    "tests_v25": "runtime/discovery_v2/tests_v25.py",
    "roots_v24": "runtime/discovery_v2/roots_v24.py",
    "cli_v23_base": "runtime/discovery_v2/cli_v23.py",
    "providers_frozen_base": "runtime/discovery_v2/providers.py",
    "render_frozen": "runtime/discovery_v2/render.py",
    "sitemap_fetch_frozen": "runtime/discovery_v2/sitemap_fetch.py",
    "security": "runtime/discovery/security.py",
    "orchestrator_frozen_base": "runtime/discovery_v2/orchestrator.py",
    "harness": "evaluation/local-discovery-runtime-v2-5/run_v25_harness.py",
    "driver_ralingen": "evaluation/local-discovery-runtime-v2-5/ralingen_driver.py",
    "driver_benchmark": "evaluation/local-discovery-runtime-v2-5/run_full_benchmark.py",
    "driver_replay": "evaluation/local-discovery-runtime-v2-5/run_replay.py",
    "driver_live": "evaluation/local-discovery-runtime-v2-5/run_live.py",
    "driver_access": "evaluation/local-discovery-runtime-v2-5/run_access.py",
    "driver_audit": "evaluation/local-discovery-runtime-v2-5/run_audit.py",
    "task_lock": "evaluation/local-discovery-runtime-v2-5/TASK-LOCK.json",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


shas = {name: sha(REPO / path) for name, path in components.items()}

manifest = {
    "candidate": "LOCAL_DISCOVERY_RUNTIME_V2_5",
    "release_name": "LOCAL-DISCOVERY-RUNTIME-V2.5",
    "status": "LOCAL_DISCOVERY_RUNTIME_V2_5_CANDIDATE_FROZEN",
    "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
    "task_id": "NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_5-ENGINEERING",
    "base_lineage": (
        "LOCAL-DISCOVERY-RUNTIME-V2.4 (canonical_roots_v24 reused unchanged; "
        "frozen base providers/render/orchestrator reused byte-identically "
        "via subclass/wrapper)"),
    "architecture_version": "DISCOVERY_FALLBACK_V25",
    "purpose": (
        "Repair the generalized V2.4 fresh-holdout failure classes "
        "(sitemapindex traversal, render-on-empty nav, FV section-page "
        "overclaim) in a new lineage; re-certify on burned data; no fresh "
        "municipalities, no external search providers, no Protocol V1 "
        "change."),
    "repairs": {
        "sitemapindex_follow": (
            "SiteDirectProviderV25 follows up to 4 sitemapindex children "
            "(bounded, validated) when direct extraction is empty; method "
            "SITEMAP_INDEX_FOLLOW."),
        "render_on_empty": (
            "One bounded root render when nav+sitemap yield zero candidates; "
            "method RENDERED_NAVIGATION_LINK; fail-closed preserved."),
        "fv_gate": (
            "is_service_specific_url gate + RouteEvaluatorV25 caps FV on "
            "generic section pages; orchestrator_v25 = verbatim copy of "
            "frozen run_v2 with three documented deltas (name, "
            "discovery_v2_5 field, V25 evaluator)."),
    },
    "budget_repair_during_validation": {
        "what": "URL budget raised 8 -> 16 in providers_v25.__init__ for V23/V24 parity",
        "why": (
            "Dead root variants exhaust the frozen base budget before the "
            "live platform root is reached (observed as RATE_LIMITED); "
            "V2.3/V2.4 raised the same budget in their subclasses."),
        "tests": "tests_v25 7/7 after change; all frozen suites re-run green.",
    },
    "components": components,
    "shas256": shas,
    "official_artifacts": [
        "evaluation/local-discovery-runtime-v2-5/ralingen-regression.json",
        "evaluation/local-discovery-runtime-v2-5/site-direct-benchmark.json",
        "evaluation/local-discovery-runtime-v2-5/benchmark-results.json",
        "evaluation/local-discovery-runtime-v2-5/replay-regression.json",
        "evaluation/local-discovery-runtime-v2-5/access-regression.json",
        "evaluation/local-discovery-runtime-v2-5/live-burned-results.json",
        "evaluation/local-discovery-runtime-v2-5/network-call-audit.json",
    ],
    "known_limitations": [
        "site-direct-benchmark.json carries inherited task_id from the frozen V2.3 runner (cosmetic).",
        "Access regression 7/9 with the two documented V2.3 source-drift pairs (Alta T2 FV->EXISTENCE_ONLY downgrade, Hasvik T9 EXISTENCE_ONLY->FV upgrade); 0 existence-safety regressions.",
        "Raelingen gate re-run three times during validation: two aborted (foreground timeout 400; background process-group kill) + one pre-budget-fix run (RATE_LIMITED); final frozen artifact is the 9/9 SUCCESS run executed_at 2026-09-09T21:47:31Z.",
    ],
}

CAND.mkdir(exist_ok=True)
(CAND / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")

m_sha = sha(CAND / "manifest.json")
lines = [f"{m_sha}  candidate-runtime-v2-5/manifest.json (CANDIDATE_SHA256)"]
for name, path in components.items():
    lines.append(f"{shas[name]}  {path}")
(CAND / "hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("CANDIDATE_SHA256:", m_sha)
print("components hashed:", len(shas))
