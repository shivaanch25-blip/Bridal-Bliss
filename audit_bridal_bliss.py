import os
import re
import glob

os.chdir(r'd:\experiment\Bridal-Bliss')
print('cwd', os.getcwd())
py_files = glob.glob('app/**/*.py', recursive=True) + ['run.py', 'config.py', 'seed.py']
refs = {}
pattern = re.compile(r'render_template\(\s*["\']([^"\']+)["\']')

for path in py_files:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print('ERR read', path, e)
        continue
    refs[path] = pattern.findall(text)

all_templates = set()
for root, dirs, files in os.walk('app/templates'):
    for f in files:
        if f.endswith('.html'):
            rel = os.path.join(root, f).replace('\\', '/')
            all_templates.add(rel[len('app/templates/'):])

missing = []
for path, templates in refs.items():
    for t in templates:
        if t not in all_templates:
            missing.append((path, t))

print('templates referenced:', sum(len(v) for v in refs.values()))
print('templates found:', len(all_templates))
print('missing templates:')
for m in missing:
    print(m)

try:
    import app
    from app import create_app
    appinst = create_app('config.Config')
    print('app imported ok')
    endpoints = sorted([rule.rule for rule in appinst.url_map.iter_rules()])
    print('route count', len(endpoints))
    for r in endpoints:
        print(r)
except Exception:
    import traceback
    traceback.print_exc()
