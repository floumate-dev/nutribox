"""Check that a translated copy of design/Main.dc.html only differs in human-visible text.

    python3 tools/check_translation.py design/Main.en.dc.html
    python3 tools/check_translation.py design/Jelovnik.ru.dc.html

Compares design/X.<lang>.dc.html against design/X.dc.html:
  - the markup skeleton: every tag and every attribute except alt/aria-label/title/href/lang
    (text nodes are ignored), so classes, styles, {{ }} bindings and handlers must match;
  - the set of {{ }} expressions;
  - the component script parses as JavaScript (node) and exposes the same renderVals keys;
  - no em dash; words with Serbian letters are listed so leftovers can be spotted.
Prints problems and exits 1 if there are any.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
TEXT_ATTRS = {'alt', 'aria-label', 'title', 'href', 'lang'}


class Skeleton(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, tuple((k, '' if k in TEXT_ATTRS else v) for k, v in attrs)))

    def handle_endtag(self, tag):
        self.items.append(('/' + tag, ()))


def split(t):
    i = t.index('<script type="text/x-dc"')
    return t[:i], t[i:]


def skeleton(markup):
    p = Skeleton()
    p.feed(markup)
    return p.items


def main(path):
    orig = re.sub(r'\.[a-z]{2}\.dc\.html$', '.dc.html', Path(path).name)
    src = (repo / 'design' / orig).read_text()
    dst = Path(path).read_text()
    problems = []
    (ms, ss), (md, sd) = split(src), split(dst)
    a, b = skeleton(ms), skeleton(md)
    if len(a) != len(b):
        problems.append(f'markup: {len(a)} tags in the original, {len(b)} in the translation')
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            problems.append(f'markup tag #{i} differs:\n  original:    {x}\n  translation: {y}')
            break
    ea, eb = set(re.findall(r'\{\{[^}]*\}\}', ms)), set(re.findall(r'\{\{[^}]*\}\}', md))
    if ea != eb:
        problems.append(f'{{{{ }}}} expressions differ: missing {sorted(ea - eb)}, extra {sorted(eb - ea)}')
    js = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', sd, re.S).group(1)
    js_src = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', ss, re.S).group(1)
    node = r"""
const vm = require('vm');
const code = require('fs').readFileSync(0, 'utf8');
class DCLogic { constructor(p) { this.props = p || {}; this.state = {}; } setState() {} }
const C = new Function('DCLogic', code + '\n;return Component;')(DCLogic);
for (const part of [0, 16]) {
  const c = new C({ partFrom: 0, partTo: 16 });
  const v = c.renderVals();
  process.stdout.write(Object.keys(v).sort().join(',') + '\n');
}
"""
    keys = []
    for code in (js_src, js):
        r = subprocess.run(['node', '-e', node], input=code, capture_output=True, text=True)
        if r.returncode:
            problems.append('script does not run: ' + r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'script failed')
            keys.append(None)
        else:
            keys.append(r.stdout.split('\n')[0])
    if keys[0] and keys[1] and keys[0] != keys[1]:
        problems.append(f'renderVals keys differ:\n  original:    {keys[0]}\n  translation: {keys[1]}')
    if '—' in dst:
        problems.append('em dash (—) found; use a comma, colon or period instead')
    visible = re.sub(r'<style>.*?</style>|<!--.*?-->|^\s*//[^\n]*', '', dst, flags=re.S | re.M)
    left = sorted(set(re.findall(r'[^\s<>"\']*[čćžšđČĆŽŠĐ][^\s<>"\']*', visible)))
    if left:
        # not an error: names (Vuksan Vasić) may keep them in English
        print(f'note: words with Serbian letters ({len(left)}), check they are names: ' + ', '.join(left[:60]))
    if problems:
        print('\n'.join(problems))
        sys.exit(1)
    print('OK: markup, bindings and script match the original')


if __name__ == '__main__':
    main(sys.argv[1])
