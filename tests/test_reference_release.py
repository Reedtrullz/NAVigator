import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
MODULE=BASE/'tools/reference_release.py'
def tempdir():
 scratch=BASE/'outputs/reference-tests';scratch.mkdir(parents=True,exist_ok=True)
 return tempfile.TemporaryDirectory(dir=scratch)
class ReferenceBoundary(unittest.TestCase):
 def build(self,source,profile,out):
  self.assertTrue(MODULE.exists(),'Positive-profile exporter is not implemented')
  spec=importlib.util.spec_from_file_location('reference_release',MODULE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  return m.build_candidate(source,profile,out)
 def fixture(self,temp,body='General reference.\n'):
  root=Path(temp)/'source';root.mkdir();(root/'public.md').write_text(body);(root/'private.md').write_text('PRIVATE CANARY')
  rows=[{'path':'public.md','disposition':'GENERAL_APPROVED','sha256':hashlib.sha256(body.encode()).hexdigest(),'selectors':'ALL'},{'path':'private.md','disposition':'EXCLUDED_PRIVATE'}]
  profile=Path(temp)/'profile.json';profile.write_text(json.dumps({'status':'UTKAST','distribution_gate':'BLOCKED','documents':rows}));return root,profile,Path(temp)/'out'
 def test_private_file_is_never_opened_or_copied(self):
  with tempdir() as temp:
   root,p,out=self.fixture(temp);(root/'private.md').unlink();(root/'private.md').symlink_to('/not-readable/private')
   result=self.build(root,p,out);self.assertTrue(result['ok']);self.assertFalse((out/'private.md').exists());self.assertNotIn('PRIVATE CANARY',(out/'public.md').read_text())
 def test_unreviewed_derived_missing_permission_or_hash_drift_rejected(self):
  for disposition in ['UNREVIEWED','EXCLUDED_DERIVED',None]:
   with self.subTest(disposition=disposition),tempdir() as temp:
    root,p,out=self.fixture(temp);v=json.loads(p.read_text());v['documents'][0]['disposition']=disposition;p.write_text(json.dumps(v))
    with self.assertRaises(ValueError):self.build(root,p,out)
    self.assertFalse(out.exists())
  with tempdir() as temp:
   root,p,out=self.fixture(temp);(root/'public.md').write_text('Changed')
   with self.assertRaises(ValueError):self.build(root,p,out)
   self.assertFalse(out.exists())
 def test_private_cross_reference_rejected(self):
  with tempdir() as temp:
   root,p,out=self.fixture(temp,'See [case](private.md).\n')
   with self.assertRaises(ValueError):self.build(root,p,out)
   self.assertFalse(out.exists())
 def test_traversal_and_symlink_rejected(self):
  for path in ['../private.md','/private.md','public.md']:
   with self.subTest(path=path),tempdir() as temp:
    root,p,out=self.fixture(temp);v=json.loads(p.read_text());v['documents'][0]['path']=path;p.write_text(json.dumps(v))
    if path=='public.md':(root/path).unlink();(root/path).symlink_to(root/'private.md')
    with self.assertRaises(ValueError):self.build(root,p,out)
    self.assertFalse(out.exists())
 def test_explicit_sections_only_and_internal_reference_integrity(self):
  with tempdir() as temp:
   root,p,out=self.fixture(temp,'# General\nSafe.\n\n# Derived\nPRIVATE CANARY\n')
   v=json.loads(p.read_text());v['documents'][0]['selectors']=['General'];p.write_text(json.dumps(v))
   result=self.build(root,p,out);self.assertTrue(result['ok']);self.assertNotIn('PRIVATE CANARY',(out/'public.md').read_text())
 def test_angle_autolinks_obey_external_domain_policy(self):
  with tempdir() as temp:
   root,p,out=self.fixture(temp,'See <https://outside.example/private>.\n')
   with self.assertRaises(ValueError):self.build(root,p,out)
   self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
