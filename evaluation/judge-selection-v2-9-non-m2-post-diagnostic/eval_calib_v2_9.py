#!/usr/bin/env python3
"""V2.9 calibration metrics for a given iteration. Gates are preregistered:
iteration proceeds only if it strictly improves on the prior iteration and
meets the development bar (overall >= 0.90, zero overcommit on traps)."""
import json, sys
from pathlib import Path

HERE = Path(__file__).parent

def score(rows):
    n = len(rows)
    correct = sum(1 for r in rows if r['correct'])
    traps = [r for r in rows if r['trap']]
    overcommit = sum(1 for r in traps if r['overcommit'])
    undercommit = sum(1 for r in traps if r['valid'] and not r['overcommit']
                      and r['gold_verdict'] == 'UNRESOLVED' and r['model_verdict'] != 'UNRESOLVED')
    dims = {}
    for dim in ('forbidden', 'route', 'uncertainty'):
        sub = [r for r in rows if r['dimension'] == dim]
        dims[dim] = {'n': len(sub), 'correct': sum(1 for r in sub if r['correct'])}
    return {'n': n, 'correct': correct, 'accuracy': correct / n if n else None,
            'trap_n': len(traps), 'overcommit': overcommit, 'undercommit': undercommit,
            'by_dimension': dims}

def main():
    it = sys.argv[1] if len(sys.argv) > 1 else '1'
    d = json.load(open(HERE / f'calibration-results-iter{it}.json'))
    out = {'iteration': it, 'candidates': {}}
    for k, v in d['candidates'].items():
        out['candidates'][k] = score(v['rows'])
    with open(HERE / f'calibration-metrics-iter{it}.json', 'w') as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + chr(10))
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
