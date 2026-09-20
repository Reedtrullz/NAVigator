#!/usr/bin/env python3
"""V2.7 stability suite: first 36 residual fixture IDs, 3 runs each, one candidate.
Usage: python3 run_stability_v2_7.py <candidate_key>
Diagnostics only; no majority-vote repair. Per-row checkpointing; resumes cleanly.
"""
import json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).parent
WIRE = {'deepseek': 'opencode-go/deepseek-v4.1-flash',
        'mimo': 'command-code/xiaomi/mimo-v2.5-pro'}
DIM_MAP = {'forbidden': 'forbidden_claim', 'route': 'route_correctness', 'uncertainty': 'required_uncertainty'}
N_FIXTURES, N_RUNS = 36, 3
def main():
    key = sys.argv[1]
    sys.path.insert(0, '/Users/reidar/Projectos/NAV Explore/evaluation/judge-contract-v2-2-two-mechanism')
    import judge_core_v2_2 as J
    fx = {f['id']: f for f in json.load(open(HERE / 'screening-fixtures.json'))['fixtures']}
    residual_ids = json.load(open(HERE / 'execution-order.json'))['residual_fixture_ids']
    selected = sorted(residual_ids)[:N_FIXTURES]
    out_path = HERE / f'stability-results-{key}.json'
    state = json.load(open(out_path)) if out_path.exists() else {'candidate': key, 'wire_id': WIRE[key], 'runs': N_RUNS, 'rows': []}
    done = {(r['id'], r['run']) for r in state['rows']}
    J.MODEL = WIRE[key]
    for fid in selected:
        f = fx[fid]
        dim = 'forbidden' if 'FORB' in fid else 'route' if 'ROUTE' in fid else 'uncertainty'
        for run in range(1, N_RUNS + 1):
            if (fid, run) in done: continue
            t0 = time.time()
            try:
                result, tel = J.call_judge(DIM_MAP[dim], f['ctx'], f['crit'], f['sut'])
                row = {'id': fid, 'run': run, 'verdict': result['verdict'] if result else 'TRANSPORT_FAILURE',
                       'valid': result is not None,
                       'latency_s': round(time.time() - t0, 2),
                       'error': None if result else 'null result'}
            except Exception as e:
                row = {'id': fid, 'run': run, 'verdict': 'TRANSPORT_FAILURE', 'valid': False,
                       'latency_s': round(time.time() - t0, 2), 'error': str(e)[:300]}
            state['rows'].append(row)
            out_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
            print(f'{key} {fid} run{run} {row["verdict"]}', flush=True)
    print(f'{key} STABILITY_CALLS_COMPLETE', flush=True)
if __name__ == '__main__':
    main()
