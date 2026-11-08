"""Build the static preview (preview/index.html, preview/jelovnik.html) from design/*.dc.html.

Run from the repo root:  python3 tools/build_preview.py
The pages render the canvas components with preview/dc-runtime.js and load images from ../assets/.
"""
import hashlib
import json
import re
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
out = repo / 'preview'
index = json.loads((repo / 'assets/index.json').read_text())
rt_ver = hashlib.sha1((out / 'dc-runtime.js').read_bytes()).hexdigest()[:8]


def blob(m):
    return '../assets/' + index[m.group(1)]['file']


def src(name):
    t = (repo / 'design' / f'{name}.dc.html').read_text()
    t = re.sub(r'/_blob/([0-9a-f]{32})', blob, t)
    t = t.replace('href="Jelovnik.dc.html"', 'href="jelovnik.html"').replace('href="Main.dc.html"', 'href="index.html"')
    t = t.replace('</script', '<\\/script')
    return f'<script type="text/plain" id="dc-src-{name}">{t}</script>\n'


def page(fname, title, root, comps, props):
    html = f'''<!doctype html>
<html lang="sr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
</head>
<body style="margin:0">
<div id="app"></div>
{''.join(src(c) for c in comps)}<script>window.DC_BLOBS = {json.dumps({k: v['file'] for k, v in index.items()})};</script>
<script src="dc-runtime.js?v={rt_ver}"></script>
<script>DCMount(document.getElementById('app'), {json.dumps(root)}, {json.dumps(props)});</script>
</body>
</html>
'''
    (out / fname).write_text(html)


page('index.html', 'Nutribox: prodajna stranica (preview)', 'Main', ['Main'], {'partFrom': 0, 'partTo': 16})
page('jelovnik.html', 'Nutribox: jelovnik (preview)', 'Jelovnik', ['Jelovnik', 'Main'], {})
print('preview built')
