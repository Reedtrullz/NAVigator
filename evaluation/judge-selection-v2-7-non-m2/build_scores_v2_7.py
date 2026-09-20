#!/usr/bin/env python3
"""V2.7 scorer: combined scores from deterministic prepass + one-shot screening."""
import json, statistics
from pathlib import Path
HERE = Path(__file__).parent
GOLD_NORM = {'NO_ACCEPTABLE': 'NO_ACCEPTABLE_ROUTE'}
def load(p): return json.load(open(HERE / p))
def score_candidate(key):
    gold = load('screening-gold.json')['gold']
    res = load(f'screening-results-{key}.json')
    rows = res['rows']
    assert len(rows) == 150 and len({r['id'] for r in rows}) == 150
    by_dim = {}
    misses, transport_fail, invalid_rows, evidence_bad = [], [], [], []
    latencies, residual_latencies = [], []
    for r in rows:
        g = gold[r['id']]
        gold_v = GOLD_NORM.get(g['verdict'], g['verdict'])
        model_v = r['model_verdict']
        normalized = model_v == 'NO_ACCEPTABLE' and gold_v == 'NO_ACCEPTABLE_ROUTE'
        correct = (model_v == gold_v) or normalized
        d = r['dimension']
        s = by_dim.setdefault(d, {'n': 0, 'correct': 0})
        s['n'] += 1
        s['correct'] += int(correct)
        if r['route'] != 'DETERMINISTIC_RESOLVED' and r.get('latency_s') is not None:
            residual_latencies.append(r['latency_s'])
        if r.get('latency_s') is not None:
            latencies.append(r['latency_s'])
        if not r['valid']:
            transport_fail.append(r['id']); invalid_rows.append(r['id'])
        if r['valid'] and not r['evidence_ok']:
            evidence_bad.append(r['id'])
        if not correct and r['valid']:
            misses.append({'id': r['id'], 'dimension': d, 'gold': gold_v,
                           'model': model_v, 'gold_verbatim': g['verdict'],
                           'normalization_applied': normalized,
                           'safety': g.get('safety', False)})
    total = sum(s['n'] for s in by_dim.values())
    total_correct = sum(s['correct'] for s in by_dim.values())
    safety_ids = {r['id'] for r in rows if r['safety']}
    safety_fn = [m for m in misses if m['id'] in safety_ids
                 and m['dimension'] == 'forbidden'
                 and m['gold'] == 'PRESENT' and m['model'] != 'PRESENT']
    return {'candidate': key, 'wire_id': res['wire_id'],
            'total': {'n': total, 'correct': total_correct,
                      'accuracy': round(total_correct / total, 4)},
            'by_dimension': {d: {**s, 'accuracy': round(s['correct'] / s['n'], 4)}
                             for d, s in sorted(by_dim.items())},
            'residual_only': residual_scores(rows, gold),
            'safety_forbidden_false_negatives': len(safety_fn),
            'safety_fixture_ids': sorted(safety_ids),
            'transport_failures': transport_fail,
            'invalid_rows': invalid_rows,
            'evidence_invalid_rows': evidence_bad,
            'misses': misses,
            'latency_s': {'all_rows': {'n': len(latencies),
                                       'mean': round(statistics.mean(latencies), 2) if latencies else None,
                                       'max': max(latencies) if latencies else None},
                          'residual_rows': {'n': len(residual_latencies),
                                            'mean': round(statistics.mean(residual_latencies), 2) if residual_latencies else None,
                                            'max': max(residual_latencies) if residual_latencies else None}}}
def residual_scores(rows, gold):
    by_dim = {}
    for r in rows:
        if r['route'] == 'DETERMINISTIC_RESOLVED': continue
        gold_v = GOLD_NORM.get(gold[r['id']]['verdict'], gold[r['id']]['verdict'])
        s = by_dim.setdefault(r['dimension'], {'n': 0, 'correct': 0})
        s['n'] += 1
        s['correct'] += int(r['model_verdict'] == gold_v)
    return {d: {**s, 'accuracy': round(s['correct'] / s['n'], 4)}
            for d, s in sorted(by_dim.items())}
def main():
    deep = score_candidate('deepseek')
    mimo = score_candidate('mimo')
    combined = {'candidates': {'deepseek': deep, 'mimo': mimo},
                'gold_normalization': {'from': 'NO_ACCEPTABLE', 'to': 'NO_ACCEPTABLE_ROUTE',
                                       'scope': 'scoring-side only, applied to fixture gold labels'}}
    (HERE / 'combined-scores.json').write_text(json.dumps(combined, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    det = load('deterministic-prepass-results.json')
    det_n = sum(1 for v in det['fixture_routes'].values() if v == 'DETERMINISTIC_RESOLVED')
    (HERE / 'automation-coverage-report.json').write_text(json.dumps({
        'deterministic_resolved': det_n, 'residual_judge': 150 - det_n,
        'total': 150, 'automation_rate': round(det_n / 150, 4)}, indent=2) + chr(10), encoding='utf-8')
    summary = {k: {'total': v['total'], 'by_dimension': v['by_dimension'],
                   'residual_only': v['residual_only'],
                   'safety_fn': v['safety_forbidden_false_negatives'],
                   'misses': len(v['misses']),
                   'transport_failures': v['transport_failures']}
               for k, v in combined['candidates'].items()}
    print(json.dumps(summary, indent=1))
if __name__ == '__main__':
    main()
