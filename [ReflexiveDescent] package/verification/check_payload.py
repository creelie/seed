from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'PACKAGE-MANIFEST.json').read_text(encoding='utf8'))
for item in manifest:
    p=(ROOT/item['path']).resolve();assert p.is_relative_to(ROOT.resolve())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path']
formal=json.loads((ROOT/'formal/verification.json').read_text(encoding='utf8'))
for item in formal['modules']:
    p=ROOT/'formal'/(item['module']+'.lean')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['source_sha256'],item['module']
assert formal['all_positive_modules_compiled']
assert not formal['scope']['full_manuscript_formalized'] and not formal['scope']['exact_D4_proved']
print('PASS:',len(manifest),'payload hashes;',formal['named_source_theorems'],'named source theorems; scope flags preserved')
