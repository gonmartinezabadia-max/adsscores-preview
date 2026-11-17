import pathlib,tempfile,unittest
from provenance import generate,verify,publication_mode
class ProvenanceTests(unittest.TestCase):
 def make(self):
  tmp=tempfile.TemporaryDirectory();r=pathlib.Path(tmp.name);out=r/'out';source=r/'source';(out/'app/aprobaciones').mkdir(parents=True);(out/'app/aprobaciones/index.html').write_text('<script src="chunk.js"></script>');(out/'chunk.js').write_text('rename-r4');source.mkdir();(source/'component.tsx').write_text('source-v1');generate(out,source,'test-release','postbuild_source_and_export_inventory');return tmp,out,source
 def test_generated_export_verifies(self):
  t,o,s=self.make();verify(o);t.cleanup()
 def test_each_missing_provenance_file_fails(self):
  for name in ['build-source.json','build-files.json','build-inputs.json','build-commit.txt']:
   t,o,s=self.make();(o/name).unlink()
   with self.assertRaises((SystemExit,FileNotFoundError)):verify(o)
   t.cleanup()
 def test_changed_chunk_or_html_fails(self):
  for name in ['chunk.js','app/aprobaciones/index.html']:
   t,o,s=self.make();(o/name).write_text('altered')
   with self.assertRaises(SystemExit):verify(o)
   t.cleanup()
 def test_new_or_removed_file_fails(self):
  for remove in [False,True]:
   t,o,s=self.make()
   if remove:(o/'chunk.js').unlink()
   else:(o/'new.js').write_text('new')
   with self.assertRaises(SystemExit):verify(o)
   t.cleanup()
 def test_regeneration_changes_source_and_export_digests(self):
  import json
  t,o,s=self.make();old=json.loads((o/'build-source.json').read_text());(s/'component.tsx').write_text('source-v2');(o/'chunk.js').write_text('build-v2');generate(o,s,'test-v2','postbuild_source_and_export_inventory');new=json.loads((o/'build-source.json').read_text());self.assertNotEqual(old['source']['tree_sha256'],new['source']['tree_sha256']);self.assertNotEqual(old['export']['manifest_sha256'],new['export']['manifest_sha256']);self.assertEqual(new['release'],'test-v2');t.cleanup()
 def test_changed_source_rejected_by_publisher_verification(self):
  t,o,s=self.make();(s/'component.tsx').write_text('unreviewed change')
  with self.assertRaises(SystemExit):verify(o,s)
  t.cleanup()
 def test_backend_not_inferred(self):
  import json
  t,o,s=self.make();self.assertFalse(json.loads((o/'build-source.json').read_text())['backend']['included']);t.cleanup()
 def test_publisher_propagates_retrospective_mode(self):
  import json
  t,o,s=self.make();generate(o,s,'retrospective','retrospective_existing_export');mode=publication_mode(o);generate(o,s,'published',mode);self.assertEqual(json.loads((o/'build-source.json').read_text())['provenance_mode'],'retrospective_existing_export');t.cleanup()
 def test_unknown_mode_rejected(self):
  import json
  t,o,s=self.make();j=json.loads((o/'build-source.json').read_text());j['provenance_mode']='fabricated';(o/'build-source.json').write_text(json.dumps(j))
  with self.assertRaises(SystemExit):publication_mode(o)
  t.cleanup()
 def test_missing_release_env_fails_and_variable_release_is_used(self):
  import subprocess,os,json
  t,o,s=self.make();env=os.environ.copy();env.pop('TEST_ADS_RELEASE',None);cmd=['python3',str(pathlib.Path(__file__).parent/'provenance.py'),'generate',str(o),'--source',str(s),'--release-env','TEST_ADS_RELEASE'];p=subprocess.run(cmd,env=env,capture_output=True);self.assertNotEqual(p.returncode,0);env['TEST_ADS_RELEASE']='unique-test-release';p=subprocess.run(cmd,env=env,capture_output=True);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads((o/'build-source.json').read_text())['release'],'unique-test-release');t.cleanup()
if __name__=='__main__':unittest.main()
