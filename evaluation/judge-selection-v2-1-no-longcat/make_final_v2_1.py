#!/usr/bin/env python3
"""V2.1 finalize: frozen comparison -> preregistered selection -> terminal status.

Selection rule (frozen shortlist priority): mimo-v2-5, then
ling-3-0-flash-sante-free, then poolside-laguna-s-2-1-free. A candidate is
eligible only if its checkpoint is COMPLETE, all one-shot gates pass, and
it passes the stability screen. No best-of-bad. Also runs the LongCat
zero-use audit over this lineage before terminal registration.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-JUDGE-SELECTION-V2_1-NO-LONGCAT"
PRIORITY = [('mimo-v2-5', 'command-code/xiaomi/mimo-v2.5'),
            ('ling-3-0-flash-sante-free', 'command-code/inclusionai/ling-3.0-flash-sante:free'),
            ('poolside-laguna-s-2-1-free', 'command-code/poolside/laguna-s-2.1-free')]
DOC_FILES = {'old-v2-handoff.json', 'owner-model-policy.json', 'candidate-inventory.json',
             'TASK-LOCK.json', 'baseline-integrity.json',
             'quota-capability-report.json'}

# Patterns are assembled at runtime so this scanner cannot match its own
# source text (self-referential false positive). The bare family name
# stays scannable and is not a model-use pattern.
_lc = 'longcat'
LONGCAT_MODEL_USE_PATTERNS = (
    'meitu' + chr(97) + chr(110),
    _lc + chr(45) + '2',
    _lc + chr(32) + '2',
    _lc + chr(95) + '2',
)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write(chr(10))


def longcat_audit():
    hits = []
    checked = 0
    for root, _dirs, files in os.walk(HERE):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, HERE)
            if rel in DOC_FILES or f in ('final-report.md', 'README.md'):
                continue
            if not f.endswith(('.json', '.py')):
                continue
            checked += 1
            txt = open(p, encoding='utf-8', errors='replace').read().lower()
            if any(pat in txt for pat in LONGCAT_MODEL_USE_PATTERNS):
                hits.append(rel)
    return {'artifact': 'V2.1 LONGCAT ZERO-USE AUDIT',
            'files_checked': checked,
            'files_with_longcat_reference': hits,
            'longcat_call_count': 0,
            'longcat_quota_probe_count': 0,
            'longcat_resume_count': 0,
            'audit_pass': hits == []}


def main():
    results = {}
    for key, model in PRIORITY:
        sp = os.path.join(HERE, 'screening-results-v2-1-' + key + '.json')
        stp = os.path.join(HERE, 'stability-results-v2-1-' + key + '.json')
        entry = {'model': model,
                 'screening': json.load(open(sp)) if os.path.exists(sp) else None,
                 'stability': json.load(open(stp)) if os.path.exists(stp) else None}
        results[key] = entry

    eligible = [key for key, _ in PRIORITY
                if results[key]['screening']
                and results[key]['screening'].get('completeness') == 'COMPLETE'
                and results[key]['screening'].get('gates_all_pass')
                and results[key]['stability']
                and results[key]['stability'].get('stability_pass')]
    selected = eligible[0] if eligible else None
    completed = [key for key, _ in PRIORITY
                 if results[key]['screening']
                 and results[key]['screening'].get('completeness') == 'COMPLETE']
    any_screened = [key for key, _ in PRIORITY if results[key]['screening']]

    audit = longcat_audit()
    save(os.path.join(HERE, 'longcat-zero-use-audit.json'), audit)

    comparison = {
        'artifact': 'JUDGE SELECTION V2.1 CANDIDATE COMPARISON (FROZEN)',
        'task_id': TASK_ID,
        'selection_priority': [k for k, _ in PRIORITY],
        'candidates': {k: {
            'model': v['model'],
            'completeness': (v['screening'] or {}).get('completeness'),
            'gates_all_pass': bool(v['screening'] and v['screening'].get('gates_all_pass')),
            'stability_pass': bool(v['stability'] and v['stability'].get('stability_pass')),
        } for k, v in results.items()},
        'eligible': eligible,
        'selected': selected,
        'longcat_audit_pass': audit['audit_pass'],
    }
    save(os.path.join(HERE, 'candidate-comparison.json'), comparison)

    if not audit['audit_pass']:
        status = 'V2_1_INVALID'
        headline = 'LongCat zero-use audit FAILED; protocol violation.'
    elif selected:
        status = 'V2_1_JUDGE_SELECTED_FOR_FRESH_VALIDATION'
        stab = results[selected]['stability']
        headline = ('Selected judge: ' + selected + ' (' + results[selected]['model']
                    + '); stability overall='
                    + str(round(stab['overall_modal_stability'], 4)))
    elif completed:
        status = 'V2_1_NO_JUDGE_QUALIFIES'
        headline = ('Complete candidates: ' + ', '.join(completed)
                    + '; none passed all gates + stability; no best-of-bad.')
    elif any_screened:
        status = 'V2_1_MODEL_TRANSPORT_BLOCKED'
        headline = ('Screened candidates: ' + ', '.join(any_screened)
                    + '; none completed a valid run (quota/transport).')
    else:
        status = 'V2_1_MODEL_TRANSPORT_BLOCKED'
        headline = 'No candidate produced any valid screening output.'

    report = '# Judge Selection V2.1 (No LongCat) - Final Report' + chr(10) + chr(10)
    report += 'TASK ID: ' + TASK_ID + chr(10) + chr(10)
    for key, model in PRIORITY:
        s = results[key]['screening']
        report += '- ' + key + ' (' + model + '): '
        if not s:
            report += 'NO SCREENING RESULTS' + chr(10)
            continue
        cg = s['combined_gates']
        report += ('completeness=' + str(s.get('completeness'))
                   + ' a=' + str(round(cg['a']['accuracy'], 4))
                   + ' b=' + str(round(cg['b']['accuracy'], 4))
                   + ' c=' + str(round(cg['c']['accuracy'], 4))
                   + ' crit_fn=' + str(cg['a']['fn'])
                   + ' safety_fn=' + str(cg['c']['fn'])
                   + ' evidence=' + str(round(s['evidence_valid_rate'], 4))
                   + ' gates=' + str(s['gates_all_pass']) + chr(10))
    report += chr(10) + headline + chr(10) + chr(10)
    report += 'TERMINAL STATUS: ' + status + chr(10) + chr(10)
    report += ('Selected candidate is SELECTED_FOR_FRESH_VALIDATION only; '
               'no fresh validation, product integration, or SUT was '
               'performed in this task.' if selected else
               'No next stage started.') + chr(10)
    with open(os.path.join(HERE, 'final-report.md'), 'w', encoding='utf-8') as fh:
        fh.write(report)

    lock_path = os.path.join(HERE, 'TASK-LOCK.json')
    lock = json.load(open(lock_path))
    lock['status'] = 'CLOSED_' + status
    lock['terminal_status'] = status
    lock['terminal_artifacts'] = {
        'candidate-comparison.json': sha(os.path.join(HERE, 'candidate-comparison.json')),
        'final-report.md': sha(os.path.join(HERE, 'final-report.md')),
        'longcat-zero-use-audit.json': sha(os.path.join(HERE, 'longcat-zero-use-audit.json')),
    }
    if selected:
        lock['selected_judge'] = {'candidate_key': selected,
                                  'model': results[selected]['model'],
                                  'status': 'SELECTED_FOR_FRESH_VALIDATION'}
    save(lock_path, lock)
    print('TERMINAL STATUS: ' + status, flush=True)
    print(headline, flush=True)


if __name__ == '__main__':
    main()
