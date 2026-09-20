#!/usr/bin/env python3
"""V2.9 burned calibration runner. Per-row checkpointing; no reruns.

Usage: python3 run_calib_v2_9.py <iteration>
Writes calibration-results-iter<N>.json. Fresh calls each iteration
(iteration metrics are measured only on the burned calibration set).
"""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import judge_core_v2_9 as J

DIM_MAP = {'forbidden': 'forbidden_claim', 'route': 'route_correctness', 'uncertainty': 'required_uncertainty'}
CANDIDATES = [('opencode-go/deepseek-v4.1-flash', 'deepseek'),
              ('command-code/xiaomi/mimo-v2.5-pro', 'mimo')]

def main():
    iteration = sys.argv[1] if len(sys.argv) > 1 else '1'
    fx_all = json.load(open(HERE / 'calibration-fixtures-v2-9.json'))['fixtures']
    out_path = HERE / f'calibration-results-iter{iteration}.json'
    results = {}
    if out_path.exists():
        results = json.load(open(out_path))
    results.setdefault('iteration', iteration)
    results.setdefault('candidates', {})

    for wire_id, key in CANDIDATES:
        rows = results['candidates'].get(key, {}).get('rows', [])
        done = {r['id'] for r in rows}
        J.MODEL = wire_id
        for f in fx_all:
            fid = f['id']
            if fid in done:
                continue
            dim_name = DIM_MAP[f['dim']]
            t0 = time.time()
            try:
                result, tel = J.call_judge(dim_name, f['ctx'], f['crit'], f['sut'])
                verdict = result['verdict'] if result else 'TRANSPORT_FAILURE'
                valid = result is not None
                err = (tel or {}).get('error')
            except Exception as e:
                verdict = 'TRANSPORT_FAILURE'
                valid = False
                err = str(e)[:300]
            gold = f['verdict']
            correct = verdict == gold
            overcommit = gold == 'UNRESOLVED' and verdict in ('SATISFIED', 'PARTIAL', 'VIOLATED',
                                                              'PRESENT', 'ABSENT', 'ACCEPTABLE',
                                                              'NO_ACCEPTABLE_ROUTE', 'NOT_REQUIRED')
            rows.append({
                'id': fid, 'dimension': f['dim'], 'trap': f.get('trap', False),
                'gold_verdict': gold, 'model_verdict': verdict,
                'correct': correct, 'overcommit': overcommit, 'valid': valid,
                'latency_s': round(time.time() - t0, 2), 'error': err,
            })
            results['candidates'][key] = {'model': wire_id, 'rows': rows}
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            print(json.dumps({'candidate': key, 'id': fid, 'verdict': verdict,
                              'gold': gold, 'correct': correct}))
    print(json.dumps({'status': 'CALIBRATION_CALLS_COMPLETE', 'iteration': iteration}))

if __name__ == '__main__':
    main()
