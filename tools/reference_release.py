#!/usr/bin/env python3
"""Explicit-profile derivation. Structural checks do not certify private-data review."""
import argparse,hashlib,json,re
from pathlib import Path,PurePosixPath
from urllib.parse import unquote,urlparse

def digest(data):return hashlib.sha256(data).hexdigest()
def safe_path(root,name):
 path=PurePosixPath(name)
 if not isinstance(name,str) or path.is_absolute() or not path.parts or any(p in ['.','..'] for p in path.parts) or '\\' in name:raise ValueError('Unsafe path')
 target=root/str(path)
 if any(p.is_symlink() for p in [target,*target.parents] if p.is_relative_to(root)) or not target.resolve().is_relative_to(root.resolve()):raise ValueError('Unsafe path boundary')
 return target

def select_sections(text,selectors):
 if selectors=='ALL':return text
 if not isinstance(selectors,list) or not selectors or not all(isinstance(s,str) for s in selectors) or len(set(selectors))!=len(selectors):raise ValueError('Explicit section selectors required')
 headings=list(re.finditer(r'^(#{1,6})\s+(.+?)\s*$',text,re.M));selected=[]
 for title in selectors:
  matches=[(i,h) for i,h in enumerate(headings) if h.group(2)==title]
  if len(matches)!=1:raise ValueError('Missing or ambiguous section')
  i,h=matches[0];end=next((n.start() for n in headings[i+1:] if len(n.group(1))<=len(h.group(1))),len(text));selected.append((h.start(),text[h.start():end]))
 return '\n'.join(part.rstrip() for _,part in sorted(selected))+'\n'

def check_links(documents,domains):
 for name,text in documents.items():
  if re.search(r'<\s*(?:script|iframe|a|img)\b',text,re.I):raise ValueError('Embedded HTML is outside this reference profile')
  links=re.findall(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)',text)+re.findall(r'^\s*\[[^\]]+\]:\s*(\S+)',text,re.M)+re.findall(r'<([^<>\s]+:[^<>\s]*)>',text)
  for link in links:
   link=unquote(link.strip('<>'));parsed=urlparse(link)
   if parsed.scheme or parsed.netloc:
    if parsed.scheme!='https' or parsed.hostname not in domains or parsed.username or parsed.password:raise ValueError('External reference is not allowed')
   elif parsed.path:
    target=PurePosixPath(name).parent/PurePosixPath(parsed.path)
    if '..' in target.parts or target.is_absolute() or str(target) not in documents:raise ValueError('Unadmitted internal reference')

def build_candidate(source_root:Path,profile_path:Path,output_dir:Path)->dict:
 source_root=Path(source_root);output_dir=Path(output_dir)
 if source_root.is_symlink():raise ValueError('Symlink source root')
 profile_bytes=Path(profile_path).read_bytes();profile=json.loads(profile_bytes)
 if profile.get('status')!='UTKAST' or profile.get('distribution_gate')!='BLOCKED':raise ValueError('Review gates must remain explicit')
 rows=profile.get('documents');domains=profile.get('external_domains',['www.nav.no','www.helsenorge.no'])
 if not isinstance(rows,list):raise ValueError('Positive profile required')
 admitted={};provenance={};seen=set()
 for row in rows:
  name=row.get('path');disposition=row.get('disposition')
  if not isinstance(name,str) or name in seen:raise ValueError('Duplicate/invalid source identity')
  seen.add(name)
  if disposition in ['EXCLUDED_PRIVATE','EXCLUDED_DERIVED']:continue # Reject before file open; excluded paths never dereferenced.
  if disposition!='GENERAL_APPROVED':raise ValueError('Missing source permission')
  p=safe_path(source_root,name);payload=p.read_bytes()
  if digest(payload)!=row.get('sha256'):raise ValueError('Source hash drift')
  text=select_sections(payload.decode('utf-8'),row.get('selectors'))
  admitted[name]=text;provenance[name]={'source_sha256':digest(payload),'derived_sha256':digest(text.encode()),'selectors':row['selectors']}
 if not admitted:raise ValueError('No admitted general documents')
 check_links(admitted,domains)
 if output_dir.is_symlink() or any(p.is_symlink() for p in output_dir.parents) or output_dir.exists() and any(output_dir.iterdir()):raise ValueError('Output must be empty and without symlinks')
 manifest={'status':'UTKAST','distribution_gate':'BLOCKED','source_profile_sha256':digest(profile_bytes),'documents':provenance,'external_domains':domains,'privacy_review':'NOT_RUN','domain_review':'NOT_RUN'}
 output_dir.mkdir(parents=True,exist_ok=True)
 for name,text in admitted.items():
  p=safe_path(output_dir,name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 (output_dir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 return check_candidate(output_dir)

def check_candidate(candidate_root:Path)->dict:
 root=Path(candidate_root)
 if root.is_symlink():raise ValueError('Symlink candidate root')
 manifest=json.loads(safe_path(root,'manifest.json').read_text())
 if manifest['status']!='UTKAST' or manifest['distribution_gate']!='BLOCKED':raise ValueError('Candidate gate drift')
 expected=set(manifest['documents'])|{'manifest.json'};found=set()
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('Symlink candidate member')
  if p.is_file():found.add(str(p.relative_to(root)))
 if found!=expected:raise ValueError('Unexpected or missing candidate member')
 documents={}
 for name,row in manifest['documents'].items():
  data=safe_path(root,name).read_bytes()
  if digest(data)!=row['derived_sha256']:raise ValueError('Candidate hash drift')
  documents[name]=data.decode('utf-8')
 check_links(documents,manifest['external_domains'])
 return {'ok':True,'files':sorted(found),'manifest_sha256':digest((root/'manifest.json').read_bytes()),'privacy_review':'NOT_RUN','domain_review':'NOT_RUN'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source_root',type=Path);p.add_argument('profile',type=Path);p.add_argument('output',type=Path);args=p.parse_args();print(json.dumps(build_candidate(args.source_root,args.profile,args.output)))
