#!/usr/bin/env python3
"""Required preview resources: prepare an export or verify a publication.
The bytes are historical fixtures from 7083c43e, not current deployment metadata.
"""
import argparse, hashlib, json, pathlib, shutil, subprocess
ROOT = pathlib.Path(__file__).resolve().parent
FIXTURES = ROOT / 'required-assets'
MANIFEST = json.loads((FIXTURES / 'sha256.json').read_text())
def verify(root):
    for name, expected in MANIFEST.items():
        p = root / name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise SystemExit('Required asset absent or changed: ' + name)
def prepare(root):
    verify(FIXTURES)
    root.mkdir(parents=True, exist_ok=True)
    for name in MANIFEST:
        shutil.copyfile(FIXTURES / name, root / name)
    verify(root)
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'verify'])
    p.add_argument('directory', type=pathlib.Path)
    a = p.parse_args()
    (prepare if a.mode == 'prepare' else verify)(a.directory)
    print('Required preview assets verified: ' + ', '.join(MANIFEST))
