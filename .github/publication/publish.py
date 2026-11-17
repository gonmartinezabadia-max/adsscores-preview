#!/usr/bin/env python3
"""Publish an already-reviewed static export without losing required resources.
Run from the gh-pages checkout. No build or provider operation is performed.
Requires an explicit expected remote HEAD and refuses dirty/concurrent checkouts.
"""
import argparse, pathlib, subprocess, shutil
import sys
sys.dont_write_bytecode = True
from required_assets import prepare, verify
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--export', required=True, type=pathlib.Path)
p.add_argument('--expected-head', required=True)
p.add_argument('--message', required=True)
p.add_argument('--push', action='store_true')
a=p.parse_args()
repo=pathlib.Path.cwd(); src=a.export.resolve()
def git(*args):
    return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
if git('status','--porcelain'): raise SystemExit('Dirty checkout: refusing publication')
if git('branch','--show-current')!='gh-pages': raise SystemExit('Expected gh-pages branch')
if git('rev-parse','HEAD')!=a.expected_head: raise SystemExit('Local HEAD changed')
def remote_unchanged():
    if git('ls-remote','origin','refs/heads/gh-pages').split()[0]!=a.expected_head:
        raise SystemExit('Remote HEAD changed: reconcile before publishing')
remote_unchanged()
if not (src/'index.html').is_file() or not (src/'app/aprobaciones/index.html').is_file():
    raise SystemExit('Not an Ads Scores static export')
# Preserve fixture bytes in the export before any destructive sync.
prepare(src)
subprocess.run(['rsync','-a','--delete','--exclude=.git','--exclude=.github','--exclude=.nojekyll','--exclude=_next/static',str(src)+'/',str(repo)+'/'],check=True)
subprocess.run(['rsync','-a',str(src/'_next/static')+'/',str(repo/'_next/static')+'/'],check=True)
verify(repo)
remote_unchanged()
if a.push:
    subprocess.run(['git','add','-A'],check=True)
    subprocess.run(['git','commit','-m',a.message],check=True)
    subprocess.run(['git','push','origin','HEAD:gh-pages'],check=True)
else:
    print('Prepared and verified, not committed or pushed. Inspect git diff before proceeding.')
