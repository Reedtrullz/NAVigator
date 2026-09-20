"""ResultSerializer: canonical byte-stable JSON output."""

import json


class ResultSerializer:
    """Serialise a discovery result dict to normalized, deterministic JSON."""

    @staticmethod
    def serialize(result):
        """Return a byte-stable JSON string with sorted keys and 2-space indent."""
        normalized = ResultSerializer._normalize(result)
        return json.dumps(normalized, sort_keys=True, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize(obj):
        """Recursively normalise lists and dicts for byte stability."""
        if isinstance(obj, dict):
            return {k: ResultSerializer._normalize(v) for k, v in sorted(obj.items())}
        if isinstance(obj, list):
            return [ResultSerializer._normalize(v) for v in obj]
        if isinstance(obj, float):
            # Avoid platform float repr differences for simple metrics
            if obj == int(obj):
                return int(obj)
            return round(obj, 6)
        return obj
