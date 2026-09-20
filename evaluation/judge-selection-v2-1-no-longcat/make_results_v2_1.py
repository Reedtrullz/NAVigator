#!/usr/bin/env python3
"""V2.1 results builder: checkpoint -> frozen one-shot gate results.

Same gates as V2 (family acc >= 0.90; A critical FN == 0; C safety
forbidden FN == 0; abstention precision >= 0.95 when applicable; evidence
100%; zero transport/schema failures). Adds completeness classification:
an incomplete checkpoint yields SCREENING_INCOMPLETE_QUOTA (persistent
quota) or SCREENING_INCOMPLETE_TRANSPORT, and the candidate does not
qualify. No gate is lowered for incompleteness.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
OLD = os.path.abspath(os.path.join(HERE, '..', 'judge-selection-v2-subskill'))
sys.path.insert(0, V14)
import judge_core_v1_4 as J  # noqa: E402

TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_1-NO-LONGCAT"
CANDIDATES = {
    'mimo-v2-5': 'command-code/xiaomi/mimo-v2.5',
    'ling-3-0-flash-sante-free': 'command-code/inclusionai/ling-3.0-flash-sante:free',
    'poolside-laguna-s-2-1-free': 'command-code/poolside/laguna-s-2.1-free',
}
ACC_MIN = 0.90
ABSTAIN_PREC_MIN = 0.95


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write(chr(10))


def fam_stats(rows, fam, gold):
    rr = [r for r in rows if r['family'] == fam]
    wrong = []
    fn = 0
    for r in rr:
        g = gold[r['id']]
        ok = r.get('verdict_correct')
        if ok is not True:
            wrong.append({'id': r['id'], 'gold': g['verdict'],
                          'predicted': r.get('verdict'), 'stage': r.get('stage')})
        if fam == 'a' and g['verdict'] == 'TRIGGERED' and r.get('verdict') == 'NOT_TRIGGERED':
            fn += 1
        if fam == 'c' and g['verdict'] == 'PRESENT' and r.get('verdict') == 'ABSENT':
            fn += 1
    correct = sum(1 for r in rr if r.get('verdict_correct') is True)
    return {'n': len(rr), 'correct': correct,
            'accuracy': correct / len(rr) if rr else 0.0, 'fn': fn, 'wrong': wrong}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True, choices=sorted(CANDIDATES))
    args = ap.parse_args()
    model = CANDIDATES[args.candidate]
    gdoc = json.load(open(os.path.join(OLD, 'judge-selection-gold.json')))
    gold = {g['fixture_id']: g for g in gdoc['gold']}
    ck = json.load(open(os.path.join(HERE, 'checkpoint-' + args.candidate + '.json')))
    rows = ck['rows']
    if ck.get('model') != model:
        sys.exit('CHECKPOINT_MODEL_MISMATCH')

    complete = len(rows) == 72
    judge_rows = [r for r in rows if r['stage'] == 'JUDGE']
    ok_rows = [r for r in judge_rows if r.get('status') == 'OK']
    transport_failures = sum(1 for r in judge_rows
                             if r.get('status') in ('TRANSPORT_FAILURE',
                                                    'TRANSPORT_CAPACITY_FAILURE'))
    quota_429_rows = sum(1 for r in judge_rows if r.get('quota_429'))
    schema_failures = sum(1 for r in judge_rows if r.get('status') == 'SCHEMA_FAILURE')
    ev_ok = sum(1 for r in ok_rows if r.get('evidence_valid') is True)
    evidence_valid_rate = (ev_ok / len(ok_rows)) if ok_rows else 1.0
    abstain_rows = [r for r in judge_rows
                    if r.get('status') == 'OK' and r.get('verdict') == 'UNRESOLVED']
    abstain_correct = sum(1 for r in abstain_rows
                          if gold[r['id']]['verdict'] == 'UNRESOLVED')
    abstention_precision = (abstain_correct / len(abstain_rows)) if abstain_rows else None

    gates = {fam: fam_stats(rows, fam, gold) for fam in ('a', 'b', 'c')}
    gate_pass = {
        'a': gates['a']['accuracy'] >= ACC_MIN and gates['a']['fn'] == 0,
        'b': gates['b']['accuracy'] >= ACC_MIN,
        'c': gates['c']['accuracy'] >= ACC_MIN and gates['c']['fn'] == 0,
    }
    abstain_gate_pass = (abstention_precision is None
                         or abstention_precision >= ABSTAIN_PREC_MIN)
    transport_ok = transport_failures == 0 and schema_failures == 0
    gates_all_pass = (complete and all(gate_pass.values()) and abstain_gate_pass
                      and evidence_valid_rate == 1.0 and transport_ok)

    if complete:
        completeness = 'COMPLETE'
    elif quota_429_rows > 0:
        completeness = 'SCREENING_INCOMPLETE_QUOTA'
    else:
        completeness = 'SCREENING_INCOMPLETE_TRANSPORT'

    results = {
        'artifact': 'JUDGE SELECTION V2.1 SCREENING RESULTS (ONE-SHOT FROZEN, NO LONGCAT)',
        'task_id': TASK_ID,
        'candidate_key': args.candidate,
        'model': model,
        'judge_core_sha256': hashlib.sha256(open(os.path.join(
            V14, 'judge_core_v1_4.py'), 'rb').read()).hexdigest(),
        'prompt_hash': J.prompt_hash(),
        'n': len(rows),
        'completeness': completeness,
        'pipeline_split': {'deterministic_rows': len(rows) - len(judge_rows),
                           'judge_rows': len(judge_rows)},
        'transport': {'judge_calls': len(judge_rows),
                      'status_ok': len(ok_rows),
                      'transport_failures': transport_failures,
                      'quota_429_rows': quota_429_rows,
                      'schema_failures': schema_failures,
                      'transport_ok': transport_ok},
        'evidence_valid_rate': evidence_valid_rate,
        'abstention': {'model_abstain_rows': len(abstain_rows),
                       'correct': abstain_correct,
                       'precision': abstention_precision,
                       'gate_min': ABSTAIN_PREC_MIN,
                       'gate_pass': abstain_gate_pass},
        'combined_gates': gates,
        'gate_pass_per_family': gate_pass,
        'gates_all_pass': gates_all_pass,
    }
    save(os.path.join(HERE, 'screening-results-v2-1-' + args.candidate + '.json'),
         results)
    print('RESULTS ' + args.candidate + ' completeness=' + completeness
          + ' gates_all_pass=' + str(gates_all_pass)
          + ' a=' + str(round(gates['a']['accuracy'], 4))
          + ' b=' + str(round(gates['b']['accuracy'], 4))
          + ' c=' + str(round(gates['c']['accuracy'], 4))
          + ' crit_fn=' + str(gates['a']['fn'])
          + ' safety_fn=' + str(gates['c']['fn']), flush=True)


if __name__ == '__main__':
    main()
