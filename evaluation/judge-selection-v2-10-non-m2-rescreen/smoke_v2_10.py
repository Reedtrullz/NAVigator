#!/usr/bin/env python3
"""V2.10 transport smoke. One synthetic non-benchmark call per candidate."""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import judge_core_v2_10 as J

CTX = 'Røyketest: syntetisk kontekst for transportverifisering.'
CRIT = 'Kommunen gir gratis busskort til alle innbyggere over 70.'
SUT = 'Kommunen gir gratis busskort til alle innbyggere over 70.'

def main():
    results = {'task_id': 'NAV-EXPLORE-JUDGE-SELECTION-V2_10-BOUNDARY-EXTENSION-AND-RESCREEN',
               'purpose': 'transport smoke: auth, model identity, JSON/schema, evidence span transport',
               'smokes': []}
    for wire_id, key in [('opencode-go/deepseek-v4.1-flash', 'deepseek'),
                         ('command-code/xiaomi/mimo-v2.5-pro', 'mimo')]:
        J.MODEL = wire_id
        t0 = time.time()
        try:
            res, tel = J.call_judge('forbidden_claim', CTX, CRIT, SUT)
            ok = res is not None and res['verdict'] == 'PRESENT'
            results['smokes'].append({
                'candidate': key, 'model': wire_id,
                'auth': 'PASS' if tel.get('http_status') == 200 else 'FAIL',
                'http_status': tel.get('http_status'),
                'schema_valid': res is not None,
                'evidence_span_transport': 'PASS' if ok else 'FAIL',
                'verdict': res['verdict'] if res else None,
                'latency_s': round(time.time() - t0, 2),
                'retries': tel.get('retries', 0),
                'error': tel.get('error'),
            })
        except Exception as e:
            results['smokes'].append({'candidate': key, 'model': wire_id, 'auth': 'FAIL',
                                      'schema_valid': False, 'error': str(e)[:300]})
    (HERE / 'smoke-results.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results['smokes'], ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
