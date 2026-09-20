import hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))

def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def w(name, obj):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')

# ---------- TASK-LOCK ----------
lock = {
    "task_id": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_2-UNCERTAINTY-CONTRACT-REPAIR",
    "status": "ACTIVE",
    "created": "2026-09-10",
    "scope": "uncertainty_contract_and_fixture_design",
    "corpus_changes_allowed": False,
    "scorer_v1_changes_allowed": False,
    "semantic_judge_v1_changes_allowed": False,
    "semantic_judge_v1_1_changes_allowed": False,
    "route_score_contract_changes_allowed": False,
    "critical_contract_changes_allowed": False,
    "forbidden_contract_changes_allowed": False,
    "full_sut_run_allowed": False,
    "runtime_changes_allowed": False,
    "fresh_product_holdout_allowed": False,
    "threshold_derivation_allowed": False,
    "gpt_5_5_allowed": False,
    "judge_model": "GPT-5.6-Luna",
    "prior_status": "SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY",
    "prior_lineage": "evaluation/dev-corpus-semantic-judge-v1-1/",
    "authoritative_scorer": "evaluation/dev-corpus-scorer-v1/",
    "authoritative_corpus": "evaluation/dev-corpus-v1/",
    "model_calls_before_human_contract_pass": 0,
    "terminal_statuses": [
        "DEV_CORPUS_SEMANTIC_JUDGE_V1_2_READY",
        "SEMANTIC_JUDGE_V1_2_UNCERTAINTY_CONTRACT_NOT_READY",
        "SEMANTIC_JUDGE_V1_2_ANNOTATION_CONTRACT_NOT_READY",
        "DEV_CORPUS_SEMANTIC_JUDGE_V1_2_NOT_READY",
        "DEV_CORPUS_SEMANTIC_JUDGE_V1_2_INVALID"
    ]
}
w('TASK-LOCK.json', lock)

# ---------- baseline-integrity ----------
def v(p, expected=None):
    got = sha(os.path.join(BASE, p))
    return {
        "path": p, "sha256": got,
        "expected_prefix": expected,
        "match": (got.startswith(expected) if expected else None)
    }

bi = {
    "verified_at": "2026-09-10",
    "dev_corpus_v1": v("evaluation/dev-corpus-v1/manifest.json", "9c265731"),
    "scorer_v1": v("evaluation/dev-corpus-scorer-v1/scorer-manifest.json", "cca4a577"),
    "semantic_judge_v1_artifacts": {
        "contract": v("evaluation/dev-corpus-semantic-judge-v1/semantic-judge-contract-v1.json", "c61b9ad8"),
        "validation_gold": v("evaluation/dev-corpus-semantic-judge-v1/judge-validation-gold.json", "e1925e60"),
        "official_results": v("evaluation/dev-corpus-semantic-judge-v1/official-validation-results.json", "31a3e012"),
        "stability_results": v("evaluation/dev-corpus-semantic-judge-v1/stability-results.json", "73ecdee1"),
        "judge_manifest": v("evaluation/dev-corpus-semantic-judge-v1/semantic-judge-manifest.json", "44a8ed00"),
        "combined_scorer_manifest": v("evaluation/dev-corpus-semantic-judge-v1/scorer-v1-semantic-manifest.json", "9fb6fc67"),
        "v1_adapter": v("evaluation/dev-corpus-scorer-v1-semantic/semantic_adapter.py", "385a7b5e"),
        "v1_integration_test": v("evaluation/dev-corpus-scorer-v1-semantic/integration_test.py", "d875b42f")
    },
    "semantic_judge_v1_1_artifacts": {
        "task_lock": v("evaluation/dev-corpus-semantic-judge-v1-1/TASK-LOCK.json", "fc7211ad"),
        "contract": v("evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-contract-v1-1.json"),
        "manifest": v("evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-manifest-v1-1.json", "b4b128b7"),
        "fixtures_80": v("evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json", "442f34fd"),
        "gold_unfrozen": v("evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-gold-v1-1.UNFROZEN.json", "9bc2c4c5"),
        "annotation_agreement": v("evaluation/dev-corpus-semantic-judge-v1-1/annotation-agreement.json", "e4c5cb3d"),
        "final_report": v("evaluation/dev-corpus-semantic-judge-v1-1/final-report.md", "40cc03c3")
    },
    "historical_files_modified": 0,
    "note": "SHAs registrert ved task-start; re-verifiseres ved task-lukking. V1 og V1.1 terminalstatuser forblir uendret."
}
w('baseline-integrity.json', bi)

# ---------- burned-data-registry ----------
reg = {
    "registry": "V1_2_BURNED_DATA",
    "created": "2026-09-10",
    "entries": {
        "v1_1_80_fixture_set": {
            "path": "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json",
            "sha256": v("evaluation/dev-corpus-semantic-judge-v1-1/jauge-placeholder.json" if False else "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json")["sha256"],
            "marked": "BURNED_CONTRACT_DEVELOPMENT_DATA",
            "reason": "V1.2-kontrakten designes med kunnskap om V1.1 disagreement patterns; hele settet er diagnostisk. Ingen fixtures fra dette settet skal brukes i V1.2 official validation (inkludert de 75 agreed).",
            "reuse_in_official_validation_allowed": False,
            "agreed_fixtures_reused": "FORBIDDEN",
            "disputed_fixtures_replaced": "IRRELEVANT - hele settet burned"
        },
        "v1_official_66": {
            "path": "evaluation/dev-corpus-semantic-judge-v1/",
            "marked": "BURNED_VALIDATION_DATA",
            "reason": "V1 official valideringssett er burned fra tidligere tasker.",
            "reuse_in_official_validation_allowed": False
        },
        "uncertainty_calibration_sets_a_b": {
            "marked": "BURNED_AFTER_HUMAN_CALIBRATION",
            "reason": "Set A og B brukes kun til menneskelig kalibrering i denne tasken; de skal ikke brukes som official model validation senere.",
            "reuse_in_official_validation_allowed": False
        },
        "model_calibration_set": {
            "marked": "BURNED_AFTER_MODEL_CALIBRATION",
            "reason": "Separat syntetisk modellkalibrering, aldri official validation.",
            "reuse_in_official_validation_allowed": False
        }
    }
}
w('burned-data-registry.json', reg)

print("initial artifacts written")
