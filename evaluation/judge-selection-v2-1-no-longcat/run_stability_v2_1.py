#!/usr/bin/env python3
"""V2.1 stability screen (frozen contract: only for one-shot qualifiers).

Subset: first 8 fixtures per family in frozen ID order (24 total), 5 runs
each. Fail-closed eligibility: refuses to run unless the candidate passed
ALL one-shot gates in screening-results-v2-1-{candidate}.json AND is
complete. Modal stability: a fixture is stable iff all 5 runs produced the
same verdict; overall and per-family rates must both be >= 0.95.
No majority-vote repair.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.abspath(os.path.join(HERE, '..', 'dev-corpus-semantic-judge-v1-6a3'))
V14 = os.path.abspath(os.path.join(HERE, '..', 'dev-corpus-semantic-judge-v1-4'))
OLD = os.path.abspath(os.path.join(HERE, '..', 'judge-selection-v2-subskill'))
sys.path.insert(0, A3)
sys.path.insert(0, V14)

from boundary_preclassifier import classify  # noqa: E402
import judge_core_v1_4 as J  # noqa: E402

GOLD_SHA = '2b348e9f12603d9890e6ccb642fc245db24fc850e62db1ab91554cfc5ee2c30d'
A3_SHA = '21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b'
FAMILIES = [('a', 'family-a-fixtures.json'),
            ('b', 'family-b-fixtures.json'),
            ('c', 'family-c-fixtures.json')]
EXPL_ROWS = {'EXPLICIT_LIMITATION': 'SATISFIED', 'PARTIAL_LIMITATION': 'PARTIAL',
             'HEDGE': 'PARTIAL', 'CONTRADICTORY_LIMITATION': 'PARTIAL',
             'OVERCONFIDENT_ASSERTION': 'VIOLATED', 'NONE': 'UNRESOLVED',
             'UNRESOLVED': 'UNRESOLVED'}
CANDIDATES = {
    'mimo-v2-5': 'command-code/xiaomi/mimo-v2.5',
    'ling-3-0-flash-sante-free': 'command-code/inclusionai/ling-3.0-flash-sante:free',
    'poolside-laguna-s-2-1-free': 'command-code/poolside/laguna-s-2.1-free',
}
RUNS = 5
SUBSET_PER_FAMILY = 8
STABILITY_MIN = 0.95


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write(chr(10))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True, choices=sorted(CANDIDATES))
    args = ap.parse_args()
    model = CANDIDATES[args.candidate]
    res_path = os.path.join(HERE, 'screening-results-v2-1-' + args.candidate + '.json')
    res = json.load(open(res_path))
    if not (res.get('completeness') == 'COMPLETE' and res.get('gates_all_pass')):
        sys.exit('STABILITY_NOT_ELIGIBLE: one-shot gates not passed')

    gdoc = json.load(open(os.path.join(OLD, 'judge-selection-gold.json')))
    g2 = json.dumps({k: v for k, v in gdoc.items() if k != 'gold_sha256'},
                    sort_keys=True, separators=(',', ':'),
                    ensure_ascii=False).encode('utf-8')
    assert hashlib.sha256(g2).hexdigest() == GOLD_SHA
    assert sha(os.path.join(A3, 'boundary_preclassifier.py')) == A3_SHA
    gold = {g['fixture_id']: {'family': g['family'], 'dimension': g['dimension'],
                              'verdict': g['verdict']} for g in gdoc['gold']}

    fixtures = []
    for fam, fname in FAMILIES:
        rows = json.load(open(os.path.join(OLD, fname)))['fixtures']
        fixtures.extend(rows[:SUBSET_PER_FAMILY])
    assert len(fixtures) == 24

    J.MODEL = model
    per_fixture = {}
    for fx in fixtures:
        g = gold[fx['id']]
        verdicts = []
        meta = None
        for run_no in range(RUNS):
            if g['family'] in ('a', 'c'):
                tj = J.call_judge(g['dimension'], fx['ctx'], fx['crit'], fx['sut'])
                v = (tj.get('result') or {}).get('verdict') if tj.get('status') == 'OK' else None
            else:
                cs = fx.get('criterion_struct') or {}
                single_expl = (fx['mode'] == 'EXPLICIT_LIMITATION'
                               and bool(cs.get('required_limitations'))
                               and not bool(cs.get('prohibited_conclusions')))
                if single_expl:
                    out = classify(fx['sut'], cs)
                    unc = out['uncertainty_behavior']
                    if not unc['abstained'] and unc.get('label') != 'ABSTAIN':
                        v = EXPL_ROWS[unc['label']]
                    else:
                        tj = J.call_judge(g['dimension'], fx['ctx'], fx['crit'],
                                          fx['sut'])
                        v = (tj.get('result') or {}).get('verdict') if tj.get('status') == 'OK' else None
                else:
                    tj = J.call_judge(g['dimension'], fx['ctx'], fx['crit'], fx['sut'])
                    v = (tj.get('result') or {}).get('verdict') if tj.get('status') == 'OK' else None
            verdicts.append(v)
            meta = tj.get('status')
        per_fixture[fx['id']] = {'verdicts': verdicts, 'last_transport': meta,
                                 'stable': len(set(verdicts)) == 1 and verdicts[0] is not None}
        print(fx['id'] + ' stable=' + str(per_fixture[fx['id']]['stable']), flush=True)
    fam_stab = {}
    for fam, _ in FAMILIES:
        ids = [fx['id'] for fx in fixtures if fx['id'].startswith(fam.upper() + '-')]
        st = sum(1 for i in ids if per_fixture[i]['stable'])
        fam_stab[fam] = st / len(ids)
    overall = sum(1 for v in per_fixture.values() if v['stable']) / len(per_fixture)
    out = {'artifact': 'JUDGE SELECTION V2.1 STABILITY RESULTS',
           'task_id': 'NAV-EXPLORE-JUDGE-SELECTION-V2_1-NO-LONGCAT',
           'candidate_key': args.candidate, 'model': model,
           'runs_per_fixture': RUNS, 'fixtures': len(fixtures),
           'per_fixture': per_fixture,
           'overall_modal_stability': overall,
           'per_family_modal_stability': fam_stab,
           'stability_min': STABILITY_MIN,
           'stability_pass': overall >= STABILITY_MIN and all(
               v >= STABILITY_MIN for v in fam_stab.values())}
    save(os.path.join(HERE, 'stability-results-v2-1-' + args.candidate + '.json'), out)
    print('STABILITY ' + args.candidate + ' overall=' + str(round(overall, 4))
          + ' pass=' + str(out['stability_pass']), flush=True)


if __name__ == '__main__':
    main()
