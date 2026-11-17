#!/usr/bin/env python3
"""Generate and verify per-export provenance. Never a protected static fixture."""
import argparse,datetime,hashlib,json,pathlib,subprocess,os
META={'build-source.json','build-commit.txt','build-files.json','build-inputs.json'}
def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(o):return (json.dumps(o,sort_keys=True,indent=2)+'\n').encode()
def inventory(root,source=False):
 result={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'.git','.github','node_modules','.next','out','__pycache__'} for x in rel.parts):continue
  if not p.is_file() or rel.name in META or rel.name.endswith(('.tsbuildinfo','.log')) or rel.name in {'next-env.d.ts','next.config.compiled.js'}:continue
  if source and rel.parts[0]=='public' and rel.name in META:continue
  result[rel.as_posix()]=digest(p.read_bytes())
 return result
def publication_mode(root):
 mode=json.loads((root/'build-source.json').read_text()).get('provenance_mode')
 if mode not in {'postbuild_source_and_export_inventory','retrospective_existing_export'}:raise SystemExit('Unknown export provenance mode')
 return mode
def generate(root,source,release,mode):
 if not isinstance(release,str)or not release.strip():raise SystemExit('Release required')
 if mode not in {'postbuild_source_and_export_inventory','retrospective_existing_export'}:raise SystemExit('Unknown provenance mode')
 files=inventory(root);inputs=inventory(source,True)
 if not files or 'app/aprobaciones/index.html'not in files:raise SystemExit('Not an Ads Scores export')
 try:base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True,stderr=subprocess.DEVNULL).strip()
 except subprocess.CalledProcessError:base=None
 fm=encoded(files);sm=encoded(inputs)
 meta={'schema_version':2,'release':release,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'provenance_mode':mode,'source':{'base_commit':base,'tree_manifest':'build-inputs.json','tree_sha256':digest(sm),'commit_is_base_only':True},'export':{'manifest':'build-files.json','manifest_sha256':digest(fm),'file_count':len(files),'scope':'all published files except provenance, .git and .github; includes retained static chunks'},'backend':{'included':False,'reason':'Gateway deploys independently; no backend identity inferred from a frontend build'}}
 for name,data in [('build-files.json',fm),('build-inputs.json',sm),('build-source.json',encoded(meta)),('build-commit.txt',('source-tree-sha256:'+digest(sm)+'\n').encode())]:(root/name).write_bytes(data)
 verify(root)
def verify(root,source=None):
 j=json.loads((root/'build-source.json').read_text());fm=(root/'build-files.json').read_bytes();sm=(root/'build-inputs.json').read_bytes()
 publication_mode(root)
 if j.get('schema_version')!=2 or digest(fm)!=j['export']['manifest_sha256']or digest(sm)!=j['source']['tree_sha256']:raise SystemExit('Provenance manifest mismatch')
 if source is not None and json.loads(sm)!=inventory(source,True):raise SystemExit('Source tree differs from build provenance')
 expected=json.loads(fm);actual=inventory(root)
 if actual!=expected:raise SystemExit('Export differs from generated provenance')
 if j['export']['file_count']!=len(expected):raise SystemExit('Export count mismatch')
 if (root/'build-commit.txt').read_text()!='source-tree-sha256:'+digest(sm)+'\n':raise SystemExit('Source pointer mismatch')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['generate','verify']);p.add_argument('root',type=pathlib.Path);p.add_argument('--source',type=pathlib.Path);p.add_argument('--release');p.add_argument('--release-env');p.add_argument('--provenance-mode',choices=['postbuild_source_and_export_inventory','retrospective_existing_export'],default='postbuild_source_and_export_inventory');a=p.parse_args()
 if a.mode=='generate':
  if a.release and a.release_env:p.error('choose --release or --release-env')
  release=os.environ.get(a.release_env)if a.release_env else a.release
  if not a.source or not release or not release.strip():p.error('generate requires source and a nonempty release (value or named environment variable)')
  generate(a.root,a.source,release,a.provenance_mode)
 else:verify(a.root)
 print('Per-export provenance verified')
