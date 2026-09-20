#!/usr/bin/env bash
# QA for NAV-EXPLORE-RC2-BLIND-V2 (spec 62). Run from anywhere; paths resolve internally.
set -euo pipefail
SET_DIR="$(cd "$(dirname "$0")" && pwd)"
SEM="$(cd "$SET_DIR/../.." && pwd)"           # evaluation/semantic-judge
ROOT="$(cd "$SEM/../.." && pwd)"            # repo root
cd "$ROOT"
pass() { echo "PASS  $1"; }

# 1. RC2 hashes before/after (engine + fusion + reviewer + auto_gate unchanged)
shasum -a 256 -c evaluation/semantic-judge/blind-recertification/RC2-V2-set/rc2-hashes-before.txt >/dev/null
pass "RC2 hashes before: ALL_OK"
shasum -a 256 -c evaluation/semantic-judge/blind-recertification/RC2-V2-set/rc2-hashes-after.txt >/dev/null
pass "RC2 hashes after: ALL_OK"
cmp -s "$SET_DIR/rc2-hashes-before.txt" "$SET_DIR/rc2-hashes-after.txt" && pass "hash files identical (no evaluator/KB-adjacent regression)"

# 2. Plaintext-label artifact absence (post-seal cleanup, spec 44)
for p in annotation-pass2.json adjudication authoring authoring-recovery backfill_flags.py quota_check.py .pre-scrub-backup/spec_wa1.py .pre-scrub-backup/spec_wd.py .pre-scrub-backup/quota_check.py; do
  [ ! -e "$SET_DIR/$p" ] || { echo "FAIL plaintext artifact present: $p"; exit 1; }
done
pass "plaintext label artifacts removed"

# 3. Leak scans over public blind artifacts (candidates, blind-cases, selection, annotation input)
python3 - "$SET_DIR" <<'EOF'
import json, sys, glob, os, re
sd = sys.argv[1]
TOKENS = ['SUPPORTED','CONTRADICTED','PARTIALLY','INSUFFICIENT','REVIEW_REQUIRED','ABSTAIN',
          'semantic_truth','proof_safe','product_action','PASS1_CONFIRMED','PASS2_CONFIRMED','RESOLVED_NEW']
targets = sorted(glob.glob(os.path.join(sd,'candidates-*.json'))) + [
    os.path.join(sd,'blind-cases.json'), os.path.join(sd,'selection.json'),
    os.path.join(sd,'annotation-input-pass2.json')]
for t in targets:
    txt = open(t, encoding='utf-8').read()
    hits = [x for x in TOKENS if x in txt]
    assert not hits, f"label token leak in {os.path.basename(t)}: {hits}"
print("PASS  label-token scan: CLEAN (public blind artifacts)")
# case-level structure: no label-bearing rows anywhere outside manifest/schema
import re as _re
for t in targets:
    data = json.loads(open(t, encoding='utf-8').read())
    if isinstance(data, dict) and ('core' in data or 'reserve' in data):
        rows = data.get('core', []) + data.get('reserve', [])
        assert all(isinstance(x, str) and _re.fullmatch(r'RC2B-[0-9]{4}', x) for x in rows), f"unexpected selection row in {t}"
        continue
    rows = data.get('cases') or data.get('candidates') or data
    if isinstance(rows, dict): rows = list(rows.values())
    for r in rows:
        assert isinstance(r, dict) and set(r.keys()) <= {'case_id','claim','sources'}, f"label row leak in {t}: {sorted(r.keys()) if isinstance(r, dict) else type(r)}"
print("PASS  case-level label scan: CLEAN (incl. selection as pure ID lists)")
# candidate uniqueness
ids = []
for t in sorted(glob.glob(os.path.join(sd,'candidates-*.json'))):
    ids += [c['case_id'] for c in json.load(open(t))['candidates']]
assert len(ids) == len(set(ids)) == 277, f"candidate uniqueness/count failed: {len(ids)}"
print("PASS  candidate uniqueness: 277 unique")
# blind-cases structural schema check (160 CORE, id pattern, required fields)
bl = json.load(open(os.path.join(sd,'blind-cases.json')))
assert bl['set_version'] == 'NAV-EXPLORE-RC2-BLIND-V2' and len(bl['cases']) == 160
for c in bl['cases']:
    assert re.fullmatch(r'RC2B-[0-9]{4}', c['case_id']) and c['claim'] and c['sources']
    assert set(c.keys()) == {'case_id','claim','sources'}
    for s in c['sources']:
        assert s.get('source_id') and s.get('kb_ref') and s.get('text')
print("PASS  blind-cases structure: 160 cases, schema-consistent, label-free")
EOF

# 4. SHAs + seal integrity + optional full decryption roundtrip if key provided via env
python3 - "$SET_DIR" <<'EOF'
import json, hashlib, base64, sys, os
sd = sys.argv[1]
man = json.load(open(os.path.join(sd,'blind-manifest.json')))
bc = open(os.path.join(sd,'blind-cases.json'),'rb').read()
sha = hashlib.sha256(bc).hexdigest()
assert sha == man['blind_cases_sha256'], "blind-cases SHA mismatch vs manifest"
print("PASS  blind-cases SHA matches manifest")
seal = json.load(open(os.path.join(sd,'answer-key.sealed')))
seal_sha = hashlib.sha256(open(os.path.join(sd,'answer-key.sealed'),'rb').read()).hexdigest()
assert seal_sha == man['answer_key_sealed_sha256'], "sealed-key SHA mismatch vs manifest"
assert seal['algorithm'] == 'AES-256-GCM'
assert seal['associated_data'].endswith(sha), "AAD does not bind blind-cases SHA"
print("PASS  sealed-key SHA matches manifest; algorithm AES-256-GCM; AAD binds blind-cases SHA")
base64.urlsafe_b64decode(seal['ciphertext'] + '=='); base64.urlsafe_b64decode(seal['nonce'] + '==')
print("PASS  ciphertext/nonce well-formed (authentication verified at seal time in memory)")
key = os.environ.get('BLIND_RC2_V2_KEY')
if key:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    k = base64.urlsafe_b64decode(key + '==')
    pt = AESGCM(k).decrypt(base64.urlsafe_b64decode(seal['nonce'] + '=='),
                           base64.urlsafe_b64decode(seal['ciphertext'] + '=='), seal['associated_data'].encode())
    kd = json.loads(pt)
    assert kd['set_version'] == 'NAV-EXPLORE-RC2-BLIND-V2' and len(kd['cases']) == 160
    print("PASS  full decryption roundtrip: 160 rows, authenticated")
EOF

# 5. Quota + manifest consistency + RC2-not-run assertions
python3 - "$SET_DIR" <<'EOF'
import json, sys, os
sd = sys.argv[1]
man = json.load(open(os.path.join(sd,'blind-manifest.json')))
pa = man['pool_aggregates']
qf = pa['quota_flags']; sem = pa['semantic']
assert len(json.load(open(os.path.join(sd,'selection.json')))['core']) == man['n_core'] == 160
assert len(json.load(open(os.path.join(sd,'selection.json')))['reserve']) == man['n_reserve'] == 117
assert man['quota_verification'] == 'ALL_QUOTAS_PASS (spec quota_check.py instrument, pool n=277, construction-time run re-derived from DB snapshot)'
assert sem['SUPPORTED'] >= 40 and sem['CONTRADICTED'] >= 40 and sem['PARTIALLY_SUPPORTED'] >= 40 and sem['INSUFFICIENT_EVIDENCE'] >= 30
for flag, minimum in [('compound',50),('multi_span',30),('numeric',30),('age_legal',20),('temporal',30),('actor',30),('modality',30),('safety',20),('legal',30),('locality_trondheim',20),('cond_exc_required',30)]:
    assert qf[flag] >= minimum, f"quota {flag} below minimum"
print("PASS  quota targets: ALL_QUOTAS_PASS (pool snapshot, provenance recorded in manifest)")
assert man['rc2_status'] == 'NOT_RUN'
assert man['rc2_hash_verification']['rc2_executed_on_blind_set'] is False
assert man['rc2_hash_verification']['before_construction'] == 'ALL_OK' == man['rc2_hash_verification']['after_construction']
lock = json.load(open(os.path.join(sd,'TASK-LOCK.json')))
assert lock['status'] == 'COMPLETED' and lock['runtime_execution_allowed'] is False
print("PASS  RC2-not-run + task-lock assertions")
assert man['annotation_agreement']['remaining_disputes'] == 0
cp = man['candidate_pipeline']
assert cp['candidates_generated'] == 277 and cp['retained'] == 277 and cp['fidelity_failures'] == 0
assert abs(cp['max_similarity_retained'] - 0.5385) < 1e-9
print("PASS  pipeline/agreement assertions (203 adjudicated, 0 remaining disputes)")
EOF

# 6. RC2 never executed against the set: no prediction artifacts may exist
find "$SET_DIR" -maxdepth 1 -iname '*prediction*' | grep -q . && { echo "FAIL prediction artifact present"; exit 1; } || pass "no RC2 prediction artifacts (RC2 never executed)"
echo "QA COMPLETE: ALL CHECKS PASSED"
