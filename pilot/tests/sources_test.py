import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CandidateBuild(unittest.TestCase):
 def test_candidate_root_is_independent_and_reproducible(self):
  base=ROOT.parent/'outputs'/'build-tests'
  base.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=base) as temp:
   outputs=[]
   for name in ['one','two']:
    out=Path(temp)/name
    run=subprocess.run([sys.executable,'-S',str(ROOT/'build/build_pilot.py'),'--generated-at','2026-10-08T12:00:00Z','--output-dir',str(out)],capture_output=True,text=True,cwd=ROOT)
    self.assertEqual(run.returncode,0,run.stderr)
    outputs.append((out/'NAVigator-pilot.html').read_bytes())
    manifest=json.loads((out/'manifest.json').read_text())
    self.assertEqual(manifest['distribution_gate'],'BLOCKED')
    self.assertEqual(manifest['outputs']['NAVigator-pilot.html'],hashlib.sha256(outputs[-1]).hexdigest())
   self.assertEqual(outputs[0],outputs[1])
 def test_output_must_be_bounded(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tests') as temp:
   out=Path(temp)/'forbidden'
   run=subprocess.run([sys.executable,'-S',str(ROOT/'build/build_pilot.py'),'--generated-at','2026-10-08T12:00:00Z','--output-dir',str(out)],capture_output=True,text=True)
   self.assertNotEqual(run.returncode,0)
   self.assertFalse(out.exists())
 def test_output_symlink_cannot_overwrite_another_file(self):
  base=ROOT.parent/'outputs'/'build-tests';base.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=base) as temp:
   victim=Path(temp)/'private.txt';victim.write_text('DO NOT CHANGE')
   out=Path(temp)/'out';out.mkdir();(out/'NAVigator-pilot.html').symlink_to(victim)
   run=subprocess.run([sys.executable,'-S',str(ROOT/'build/build_pilot.py'),'--generated-at','2026-10-08T12:00:00Z','--output-dir',str(out)],capture_output=True,text=True)
   self.assertNotEqual(run.returncode,0)
   self.assertEqual(victim.read_text(),'DO NOT CHANGE')
if __name__=='__main__':unittest.main()
