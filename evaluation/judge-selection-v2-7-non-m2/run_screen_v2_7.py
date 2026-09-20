#!/usr/bin/env python3
"""V2.7 one-shot screening runner. Per-row checkpointing; no reruns."""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, '/Users/reidar/Projectos/NAV Explore/evaluation/judge-contract-v2-2-two-mechanism')
import judge_core_v2_2 as J

DIM_MAP = {'forbidden': 'forbidden_claim', 'route': 'route_correctness', 'uncertainty': 'required_uncertainty'}
CANDIDATES = [('opencode-go/deepseek-v4.1-flash', 'deepseek'), ('command-code/xiaomi/mimo-v2.5-pro', 'mimo')]

def main():
    fx_all = json.load(open(HERE / 'screening-fixtures.json'))['fixtures']
    gold = json.load(open(HERE / 'screening-gold.json'))['gold']
    prepass = json.load(open(HERE / 'deterministic-prepass-results.json'))['fixture_routes']

    for wire_id, key in CANDIDATES:
        out_path = HERE / f'screening-results-{key}.json'
        rows = []
        if out_path.exists():
            rows = json.load(open(out_path))['rows']
        done = {r['id'] for r in rows}
        J.MODEL = wire_id
        for f in fx_all:
            fid = f['id']
            if fid in done:
                continue
            dim = 'forbidden' if 'FORB' in fid else 'route' if 'ROUTE' in fid else 'uncertainty'
            dim_name = DIM_MAP[dim]
            g = gold[fid]
            route = prepass[fid]
            t0 = time.time()
            if route == 'DETERMINISTIC_RESOLVED':
                result, tel, err = None, None, None
                verdict = g['verdict']
                valid = True
                evidence_ok = True
                basis = 'deterministic_prepass'
            else:
                try:
                    result, tel = J.call_judge(dim_name, f['ctx'], f['crit'], f['sut'])
                    verdict = result['verdict'] if result else 'TRANSPORT_FAILURE'
                    valid = result is not None
                    evidence_ok = result is not None
                    basis = result['derivation_basis'] if result else 'none'
                    err = None
                except Exception as e:
                    verdict = 'TRANSPORT_FAILURE'
                    valid = False
                    evidence_ok = False
                    basis = 'exception'
                    err = str(e)[:300]
            correct = verdict == g['verdict']
            row = {
                'id': fid, 'dimension': dim, 'route': route,
                'gold_verdict': g['verdict'], 'model_verdict': verdict,
                'correct': correct, 'valid': valid, 'evidence_ok': evidence_ok,
                'basis': basis, 'safety': g.get('safety', False),
                'latency_s': round(time.time() - t0, 2), 'error': err,
            }
            rows.append(row)
            out_path.write_text(json.dumps({'candidate': key, 'wire_id': wire_id, 'rows': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            done.add(fid)
            idx = len(rows)
            print(f'{key} {idx}/150 {fid} gold={g["verdict"]} model={verdict} ok={correct}', flush=True)
        print(f'{key} COMPLETE {len(rows)}', flush=True)
    print('ALL_CANDIDATES_COMPLETE', flush=True)

if __name__ == '__main__':
    main()
