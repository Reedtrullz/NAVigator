#!/usr/bin/env python3
"""Provenance-only repair: HUMAN_REVIEWED -> LLM_ADJUDICATED for 2 residual criteria.

Semantic observations, derived verdicts, and semantic result values are unchanged.
"""
import json, hashlib, copy
from collections import Counter

OLD = 'evaluation/measurement-v3-residual-human-adjudication-v1/'
NEW = 'evaluation/measurement-v3-final-authority-provenance-repair-v1/'
AINT = 'evaluation/measurement-v3-astra-integration-residual-v1/'
KERNEL = 'evaluation/judge-selection-v2-13-forbidden-route-specialist/judge_core_v2_13.py'
TARGETS = {'ROUT-025::forbidden:01', 'ROUT-066::forbidden:01'}

KSHA = hashlib.sha256(open(KERNEL, 'rb').read()).hexdigest()
assert KSHA == '66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682'

res_old_sha = hashlib.sha256(open(OLD + 'combined-measurement-results-complete.json', 'rb').read()).hexdigest()
agg_old_sha = hashlib.sha256(open(OLD + 'combined-aggregate-metrics-complete.json', 'rb').read()).hexdigest()

repair_info = {
    'repair_task': 'NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1',
    'rows_corrected': sorted(TARGETS),
    'semantic_observations_changed': False,
    'derived_verdicts_changed': False,
    'derivation_kernel_sha256': KSHA,
}

# 1. corrected combined results
res = copy.deepcopy(json.load(open(OLD + 'combined-measurement-results-complete.json')))
res['artifact'] = 'combined-measurement-results-complete-provenance-corrected'
res['task_id'] = 'NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1'
res['provenance_repair'] = dict(repair_info, source_artifact_sha256=res_old_sha)

changed = set()
rows_all = []
for c in res['cases']:
    for row in c['criteria']:
        rows_all.append(row)
        if row['criterion_id'] in TARGETS:
            assert row['verdict'] == 'ABSENT'
            assert row['authority'] == 'HUMAN_REVIEWED'
            row['authority'] = 'LLM_ADJUDICATED'
            prov = row['provenance']
            prov['observation_source'] = 'CHATGPT_SINGLE_REVIEW_RESIDUAL'
            prov['observation_model'] = 'chatgpt'
            prov['authority_subtype'] = 'CHATGPT_SINGLE_REVIEW_RESIDUAL'
            prov['authority_correction'] = 'PROVENANCE_CORRECTED_FROM_HUMAN_REVIEWED_2026-09-16'
            prov['prior_misclassified_as'] = 'HUMAN_REVIEWED/OWNER-01'
            prov.pop('reviewer', None)
            prov['human_adjudications_sha256'] = 'SUPERSEDED - human attribution was incorrect; file retained as historical trace of LLM-origin observations'
            prov['human_adjudication_freeze_manifest_sha256'] = 'SUPERSEDED - see repair-record.json'
            changed.add(row['criterion_id'])
assert changed == TARGETS

# proof: only authority+provenance differ on the 2 rows; verdicts/status and all other rows identical
old_rows = {(c['case_id'], r['criterion_id']): r
            for c in json.load(open(OLD + 'combined-measurement-results-complete.json'))['cases']
            for r in c['criteria']}
diff_ids = set()
for c in res['cases']:
    for row in c['criteria']:
        o = old_rows[(c['case_id'], row['criterion_id'])]
        if row == o:
            continue
        diff_ids.add(row['criterion_id'])
        a2, b2 = copy.deepcopy(row), copy.deepcopy(o)
        del a2['authority']; del a2['provenance']
        del b2['authority']; del b2['provenance']
        assert a2 == b2, ('non-provenance field diff', row['criterion_id'])
        assert row['verdict'] == o['verdict'] and row['status'] == o['status']
assert diff_ids == TARGETS

auth = Counter(r['authority'] for r in rows_all)
assert dict(auth) == {'DETERMINISTIC': 526, 'LLM_REVIEWED': 64, 'LLM_ADJUDICATED': 10}, auth
cov = res['coverage']
if 'criterion_level_coverage' in cov:
    cov = cov['criterion_level_coverage']
cov['DETERMINISTIC'] = auth['DETERMINISTIC']
cov['LLM_REVIEWED'] = auth['LLM_REVIEWED']
cov['LLM_ADJUDICATED'] = auth['LLM_ADJUDICATED']
cov['HUMAN_REVIEWED'] = 0
cov['PENDING_HUMAN_ADJUDICATION'] = 0
cov['TOTAL_CRITERIA'] = sum(auth.values())
cov['AUTHORITATIVE_TOTAL'] = sum(auth.values())
cov['AUTHORITATIVE_PCT'] = 100.0
assert cov['HUMAN_REVIEWED'] == 0 and cov['TOTAL_CRITERIA'] == 600

with open(NEW + 'combined-measurement-results-complete-provenance-corrected.json', 'w') as f:
    json.dump(res, f, indent=2, ensure_ascii=False); f.write('\n')

# 2. corrected authority map
am = copy.deepcopy(json.load(open(AINT + 'authority-map.json')))
am['artifact'] = 'authority-map-provenance-corrected'
am['task_id'] = 'NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1'
am['provenance_repair'] = dict(repair_info, source_lineage=AINT)
hits = set()
def walk(obj):
    if isinstance(obj, dict):
        cid = obj.get('criterion_id') or obj.get('criterion') or ''
        if cid in TARGETS:
            obj['authority'] = 'LLM_ADJUDICATED'
            obj['authority_subtype'] = 'CHATGPT_SINGLE_REVIEW_RESIDUAL'
            obj['provenance_corrected'] = True
            obj['prior_misclassified_as'] = 'HUMAN_REVIEWED/OWNER-01'
            hits.add(cid)
        for v in obj.values():
            walk(v)
    elif isinstance(obj, list):
        for v in obj:
            walk(v)
walk(am)
assert hits == TARGETS, hits
dist = am.get('authority_distribution')
if isinstance(dist, dict):
    dist['DETERMINISTIC'] = 526
    dist['LLM_REVIEWED'] = 64
    dist['LLM_ADJUDICATED'] = 10
    dist['HUMAN_REVIEWED'] = 0
    dist.pop('PENDING_HUMAN_ADJUDICATION', None)
    dist['TOTAL'] = 600
am['unmapped_pending_count'] = 0
am['llm_adjudicated_subtype_breakdown'] = {'DUAL_PASS_ASTRA_RESIDUAL': 8, 'CHATGPT_SINGLE_REVIEW_RESIDUAL': 2}
with open(NEW + 'authority-map-provenance-corrected.json', 'w') as f:
    json.dump(am, f, indent=2, ensure_ascii=False); f.write('\n')

# 3. corrected aggregates (authority metadata only)
agg = copy.deepcopy(json.load(open(OLD + 'combined-aggregate-metrics-complete.json')))
agg['artifact'] = 'combined-aggregate-metrics-provenance-corrected'
agg['task_id'] = 'NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1'
agg['authority_mix_honesty'] = ('526 deterministic criteria, 64 LLM-reviewed, 10 LLM-adjudicated '
                                '(8 dual-pass Astra residual + 2 ChatGPT single-review residual), '
                                '0 human-reviewed; no criterion in this baseline was decided by a human')
c = agg['criterion_level_coverage']
c['DETERMINISTIC'] = 526; c['LLM_REVIEWED'] = 64; c['LLM_ADJUDICATED'] = 10
c['HUMAN_REVIEWED'] = 0; c['PENDING_HUMAN_ADJUDICATION'] = 0
c['AUTHORITATIVE_TOTAL'] = 600; c['AUTHORITATIVE_PCT'] = 100.0
agg['llm_adjudicated_subtype_breakdown'] = {'DUAL_PASS_ASTRA_RESIDUAL': 8, 'CHATGPT_SINGLE_REVIEW_RESIDUAL': 2}
agg['provenance_repair'] = dict(repair_info, source_artifact_sha256=agg_old_sha)
with open(NEW + 'combined-aggregate-metrics-provenance-corrected.json', 'w') as f:
    json.dump(agg, f, indent=2, ensure_ascii=False); f.write('\n')

# 4. repair record (historical trace)
repair = {
    'artifact': 'authority-provenance-repair-record',
    'task_id': 'NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1',
    'repair_utc': '2026-09-16',
    'finding': ('ROUT-025::forbidden:01 and ROUT-066::forbidden:01 were classified HUMAN_REVIEWED/OWNER-01 '
                'in the terminal frozen baseline, but the semantic observations for both criteria '
                'originated from ChatGPT/LLM, not from the human owner.'),
    'original_terminal_freeze': {
        'lineage': OLD,
        'terminal_status': 'MEASUREMENT_V3_BURNED_BASELINE_COMPLETE',
        'misclassified_criteria': sorted(TARGETS),
        'original_classification': 'HUMAN_REVIEWED / OWNER-01',
        'combined_results_complete_sha256': res_old_sha,
    },
    'discovery': ('post-freeze owner audit established that the semantic decisions for both criteria '
                  'were LLM-origin: the adjudication payloads were produced by ChatGPT in the '
                  'conversation, and the owner transcribed them rather than making the semantic calls'),
    'correction': {
        'authority_before': 'HUMAN_REVIEWED',
        'authority_after': 'LLM_ADJUDICATED',
        'authority_subtype': 'CHATGPT_SINGLE_REVIEW_RESIDUAL',
        'reviewer_attribution': 'ChatGPT/LLM (single review pass per criterion); OWNER-01 was the requester/owner, not the semantic reviewer',
    },
    'invariants': {
        'SEMANTIC_OBSERVATIONS_CHANGED': False,
        'DERIVED_VERDICTS_CHANGED': False,
        'AGGREGATE_RESULT_VALUES_CHANGED': False,
        'SUT_RERUN': False,
        'GOLD_CHANGED': False,
        'PACKETS_CHANGED': False,
        'MEASUREMENT_CONTRACT_CHANGED': False,
        'LLM_SEMANTIC_REVIEW_CALLS': 0,
        'HUMAN_REVIEW_CALLS': 0,
    },
    'semantic_observations_retained': {
        'ROUT-025::forbidden:01': {'criterion_semantic_match': 'MATCH', 'speaker_commitment': 'NEGATED'},
        'ROUT-066::forbidden:01': {'criterion_semantic_match': 'MATCH', 'speaker_commitment': 'NEGATED'},
    },
    'derived_verdicts_retained': 'ABSENT (M1:NEGATED) for both criteria; kernel ' + KSHA,
    'old_freeze_status': 'SUPERSEDED_HISTORICAL_NOT_DELETED',
    'old_lineage_integrity': 'evaluation/measurement-v3-residual-human-adjudication-v1/hashes.txt 16/16 pins re-verified OK before correction; old lineage not mutated',
    'final_authority_mix': {'DETERMINISTIC': 526, 'LLM_REVIEWED': 64, 'LLM_ADJUDICATED': 10,
                            'HUMAN_REVIEWED': 0, 'PENDING': 0, 'TOTAL': 600},
    'baseline_label': 'BURNED_DEV_BASELINE_ONLY',
}
with open(NEW + 'repair-record.json', 'w') as f:
    json.dump(repair, f, indent=2, ensure_ascii=False); f.write('\n')

print('provenance repair applied: 2 rows authority-corrected; all invariants asserted')
