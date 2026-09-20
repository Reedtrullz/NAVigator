"""Gold-stripping corpus loader (evaluator side only).

The loader is the only component that touches gold before scoring, and its
only gold operation is stripping. The leak guard runs on the serialized JSON
of the constructed input object, so nested leaks cannot slip through a
Python-view key check.
"""

import hashlib
import json


GOLD_FIELDS = (
    "safety_priority",
    "acceptable_routes",
    "forbidden_claims",
    "required_uncertainty",
    "required_evidence_fields",
    "critical_error_if",
)

_GUARD_KEYS = GOLD_FIELDS + ("gold", "expected", "scorer")


class GoldLeakError(Exception):
    pass


def load_corpus(case_file, *, sha_registry):
    with open(case_file, "rb") as f:
        raw = f.read()
    rel = _registry_key_for(case_file)
    expected = sha_registry.get(rel)
    if expected is None:
        raise GoldLeakError("no registry entry for %r" % (rel,))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise GoldLeakError(
            "integrity drift for %r: registry %s != actual %s" % (rel, expected, actual)
        )
    doc = json.loads(raw.decode("utf-8"))
    if doc.get("case_count") != len(doc.get("cases", [])):
        raise GoldLeakError("case_count mismatch in %r" % (rel,))
    return doc


def _registry_key_for(case_file):
    # Registry keys are relative to evaluation/dev-corpus-v1/.
    return "cases/" + case_file.rstrip("/").split("/")[-1]


def strip_gold(case, *, executed_at):
    sut_input = {
        "case_id": case["id"],
        "user_query": case["utterance"],
        "profile": case["profile"],
        "context": {},
        "location_context": {},
        "timestamp_context": {"executed_at": executed_at},
    }
    _assert_no_gold(json.dumps(sut_input), case["id"])
    return sut_input


def iter_inputs(corpus_file, *, executed_at):
    for case in corpus_file["cases"]:
        yield strip_gold(case, executed_at=executed_at)


def _assert_no_gold(serialized, case_id):
    for key in _GUARD_KEYS:
        if '"%s"' % key in serialized:
            raise GoldLeakError(
                "gold/evaluation field %r detected in SUT input for case %s"
                % (key, case_id)
            )
