#!/usr/bin/env python3
"""Build only this candidate's positive input list; never load the corpus."""
import argparse,hashlib,json,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
INPUTS=['src/template.html','src/styles.css','src/safety.js','src/state-plan.js','src/summary.js','src/ui.js','data/pilot3-tiltak-vnext.json','data/pilot3-tiltak-vnext.schema.json','data/session-v3.schema.json','data/input-policy.json','kilder/safety-triage-rules-v2.json','package.json','package-lock.json','build/build_pilot.py','build/test_pilot.js']
def sha(data):return hashlib.sha256(data).hexdigest()
def read_input(name):
 p=ROOT/name
 if p.is_symlink() or any(x.is_symlink() for x in p.parents if x!=ROOT.parent) or not p.is_file() or not p.resolve().is_relative_to(ROOT):raise ValueError('Missing or unsafe declared input: '+name)
 return p.read_bytes()
def validate_json(node,data,schema):
 script="const fs=require('fs');const Ajv=require('./node_modules/ajv');const a=new Ajv({strict:false,allErrors:true});if(!a.validate(JSON.parse(fs.readFileSync(process.argv[1])),JSON.parse(fs.readFileSync(process.argv[2])))){console.error(JSON.stringify(a.errors));process.exit(1)}"
 result=subprocess.run([node,'-e',script,str(ROOT/schema),str(ROOT/data)],cwd=ROOT,capture_output=True,text=True)
 if result.returncode:raise ValueError('Schema validation failed: '+result.stderr)
def build_candidate(output_dir,generated_at):
 stamp=datetime.fromisoformat(generated_at.replace('Z','+00:00'))
 if stamp.tzinfo is None:raise ValueError('Build timestamp requires timezone')
 stamp=stamp.astimezone(timezone.utc).isoformat(timespec='seconds')
 inputs={name:read_input(name) for name in INPUTS}
 policy=json.loads(inputs['data/input-policy.json'])
 if policy['distribution_gate']!='BLOCKED' or policy['status']!='UTKAST' or policy['runtime_enabled'] is not False:raise ValueError('Candidate release gate drift')
 if sha(inputs['kilder/safety-triage-rules-v2.json'])!=policy['triage_sha256']:raise ValueError('Frozen triage input drift')
 node=shutil.which('node')
 if not node or not (ROOT/'node_modules/ajv').is_dir():raise ValueError('Install pinned local dependencies with npm ci in pilot/')
 validate_json(node,'data/pilot3-tiltak-vnext.json','data/pilot3-tiltak-vnext.schema.json')
 content=json.loads(inputs['data/pilot3-tiltak-vnext.json']);source_ids={s['id'] for s in content['sources']}
 if len(source_ids)!=len(content['sources']) or len({a['id'] for a in content['actions']})!=len(content['actions']):raise ValueError('Duplicate source/action identity')
 for row in [*content['sources'],*content['contacts'].values()]:
  url=urlparse(row['url'])
  if url.scheme!='https' or url.hostname not in {'www.nav.no','www.helsenorge.no'} or url.username or url.password:raise ValueError('Unsupported contact/source URL')
 for action in content['actions']:
  if not set(action['sourceIds']).issubset(source_ids) or action['contactId'] not in content['contacts']:raise ValueError('Unbound contact/source')
 data={'content':content,'triage':json.loads(inputs['kilder/safety-triage-rules-v2.json']),'generatedAt':stamp}
 template=inputs['src/template.html'].decode()
 scripts='\n\n'.join(inputs['src/'+name].decode() for name in ['safety.js','state-plan.js','summary.js','ui.js'])
 html=template.replace('__STYLES__',inputs['src/styles.css'].decode()).replace('__DATA_JSON__',json.dumps(data,ensure_ascii=False,sort_keys=True).replace('<','\\u003c')).replace('__SCRIPT__',scripts).replace('__GENERATED_AT__',stamp)
 if re.search(r'__[A-Z_]+__',html) or '<script src=' in html:raise ValueError('Template/runtime boundary drift')
 out=Path(output_dir)
 if not out.resolve().is_relative_to(ROOT.parent/'outputs') or out.is_symlink():raise ValueError('Output must be within this checkout outputs/')
 for name in ['NAVigator-pilot.html','manifest.json']:
  target=out/name
  if target.is_symlink() or (target.exists() and not target.is_file()):raise ValueError('Unsafe output member: '+name)
 payload=html.encode();manifest={'candidate_id':'navigator-contact-review-2026-10-08','generated_at':stamp,'content_version':content['content_version'],'status':'UTKAST','distribution_gate':'BLOCKED','runtime_enabled':False,'inputs':{name:sha(value) for name,value in inputs.items()},'outputs':{'NAVigator-pilot.html':sha(payload)}}
 # All validation precedes output creation; originals are never an output target.
 out.mkdir(parents=True,exist_ok=True);(out/'NAVigator-pilot.html').write_bytes(payload);(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 return manifest
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--generated-at',required=True);parser.add_argument('--output-dir',required=True);args=parser.parse_args()
 try:
  manifest=build_candidate(args.output_dir,args.generated_at);print('BUILD OK',manifest['outputs']['NAVigator-pilot.html'])
 except (ValueError,KeyError,OSError,json.JSONDecodeError) as error:print('BUILD BLOCKED:',error,file=sys.stderr);sys.exit(1)
