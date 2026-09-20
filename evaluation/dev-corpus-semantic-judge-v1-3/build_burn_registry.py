#!/usr/bin/env python3
"""Register the V1.2 official annotation set as burned contract data.
The V1.3 contract is derived directly from its disagreement patterns.
"""
import json
import os
from lib_common import write_json
HERE = os.path.dirname(os.path.abspath(__file__))

fixtures = json.load(open(os.path.join(
    HERE, "..", "dev-corpus-semantic-judge-v1-2",
    "judge-validation-fixtures-v1-2.json"), encoding="utf-8"))["fixtures"]
ids = [f["id"] for f in fixtures]

write_json("burned-data-registry.json", {
    "task": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3-BOUNDARY-CLARIFICATION",
    "created": "2026-09-10",
    "burned_sets": [
        {
            "set": "DEV_CORPUS_SEMANTIC_JUDGE_V1_OFFICIAL_66",
            "status": "BURNED_OFFICIAL_VALIDATION_DATA",
            "note": "carried burned from V1.2 lineage; no reuse in V1.3",
        },
        {
            "set": "DEV_CORPUS_SEMANTIC_JUDGE_V1_1_ANNOTATION_80",
            "status": "BURNED_CONTRACT_DEVELOPMENT_DATA",
            "note": "carried burned from V1.2 lineage; no reuse in V1.3",
        },
        {
            "set": "DEV_CORPUS_SEMANTIC_JUDGE_V1_2_OFFICIAL_80",
            "status": "BURNED_CONTRACT_DEVELOPMENT_DATA",
            "registered": "2026-09-10",
            "fixture_count": len(ids),
            "agreed_fixture_count": 70,
            "disagreed_fixture_count": 10,
            "justification": "V1.3 boundary contract derives directly from the 10 disagreement patterns observed in this set; reuse of any fixture or near-variant would contaminate V1.3 official validation",
            "reusable_for_official_validation": False,
            "near_variant_reuse_allowed": False,
            "fixture_ids": ids,
        },
        {
            "set": "SEMANTIC_JUDGE_V1_2_HUMAN_CALIBRATION_A_B",
            "status": "BURNED_CONTRACT_DEVELOPMENT_DATA",
            "note": "carried burned from V1.2 lineage",
        },
        {
            "set": "SEMANTIC_JUDGE_V1_2_MODEL_CALIBRATION_16",
            "status": "BURNED_MODEL_DEVELOPMENT_DATA",
            "note": "carried burned from V1.2 lineage",
        },
    ],
    "protocol_reuse_allowed": True,
    "data_reuse_allowed": False,
})
print("burned-data-registry.json written;", len(ids), "V1.2 official fixtures burned")
