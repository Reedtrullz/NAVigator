"""Phase 2 corpus loader: Phase 1 loader verbatim + location passthrough.

The Phase 1 loader (evaluation/full-sut-implementation/sut_runner/loader.py)
is loaded by file path, not by package import: both runners live in
sut_runner/ directories, so a package-level import would resolve to this
module itself. File-path loading preserves the Phase 1 bytes exactly.
The only Phase 2 extension: a case may carry an optional location_context
(schema-valid per sut-input/v1); corpus cases without it stay unchanged.
"""

import importlib.util
import json
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PHASE1_LOADER_PATH = os.path.normpath(os.path.join(
    _THIS_DIR, "..", "..", "full-sut-implementation", "sut_runner", "loader.py"))

_spec = importlib.util.spec_from_file_location("_phase1_loader", _PHASE1_LOADER_PATH)
_phase1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_phase1)

# Re-exported verbatim from Phase 1 (loaded by file path, see docstring).
GOLD_FIELDS = _phase1.GOLD_FIELDS
GoldLeakError = _phase1.GoldLeakError
_GUARD_KEYS = _phase1._GUARD_KEYS
_assert_no_gold = _phase1._assert_no_gold
_registry_key_for = _phase1._registry_key_for
load_corpus = _phase1.load_corpus


def strip_gold(case, *, executed_at):
    """Phase 1 strip_gold + optional location_context passthrough."""
    sut_input = {
        "case_id": case["id"],
        "user_query": case["utterance"],
        "profile": case["profile"],
        "context": {},
        "location_context": case.get("location_context", {}),
        "timestamp_context": {"executed_at": executed_at},
    }
    _assert_no_gold(json.dumps(sut_input), case["id"])
    return sut_input


def iter_inputs(corpus_file, *, executed_at):
    for case in corpus_file["cases"]:
        yield strip_gold(case, executed_at=executed_at)
