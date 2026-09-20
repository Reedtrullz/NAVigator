"""ProtocolLoader: load and validate the frozen discovery protocol V1.

The protocol file is the authoritative contract. This module never mutates it.
"""

import hashlib
import json
from pathlib import Path


class ProtocolLoadError(Exception):
    """Protocol file missing, unreadable, or structurally invalid."""


class ProtocolShaMismatch(ProtocolLoadError):
    """Protocol file does not match the frozen SHA."""


EXPECTED_PROTOCOL_SHA = "fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca"


def sha256_file(path):
    """Return the hex SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class ProtocolLoader:
    """Load the frozen protocol, verify its SHA, and expose its sections."""

    def __init__(self, path, expected_sha=EXPECTED_PROTOCOL_SHA):
        self.path = Path(path)
        self.expected_sha = expected_sha
        self.actual_sha = None
        self._data = None

    def load(self):
        if not self.path.exists():
            raise ProtocolLoadError("Protocol file not found: %s" % self.path)
        self.actual_sha = sha256_file(self.path)
        if self.actual_sha != self.expected_sha:
            raise ProtocolShaMismatch(
                "Protocol SHA mismatch: expected %s, got %s"
                % (self.expected_sha, self.actual_sha)
            )
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProtocolLoadError("Protocol file is not valid JSON: %s" % exc) from exc
        self._validate_structure()
        return self._data

    def _validate_structure(self):
        required_keys = [
            "protocol_id",
            "levels",
            "query_family_templates",
            "access_evidence_rules",
            "service_state_model",
            "route_confidence_model",
            "stop_states",
            "canonical_access_taxonomy",
            "uncertainty_outputs",
        ]
        missing = [k for k in required_keys if k not in self._data]
        if missing:
            raise ProtocolLoadError("Protocol missing required keys: %s" % missing)

    @property
    def protocol_id(self):
        return self._data["protocol_id"]

    @property
    def levels(self):
        return self._data["levels"]

    @property
    def query_templates(self):
        return self._data["query_family_templates"]

    @property
    def access_rules(self):
        return self._data["access_evidence_rules"]

    @property
    def canonical_access_taxonomy(self):
        return self._data["canonical_access_taxonomy"]

    @property
    def route_states(self):
        return list(self._data["route_confidence_model"].keys())

    @property
    def stop_states(self):
        return [s["state"] for s in self._data["stop_states"]]

    @property
    def uncertainty_outputs(self):
        return self._data["uncertainty_outputs"]
