"""Build the Webflow version of the landing page into webflow/landing/.

Run from the repo root:
    python3 tools/build_webflow.py build              # landing.css, landing.js, embeds
    python3 tools/build_webflow.py snippets <sha>     # head.html, footer.html for commit <sha>

Output (webflow/landing/):
    landing.css     page CSS (Webflow reset scoped to the page + the design's CSS)
    landing.js      runtime + page template; takes over the prerendered HTML
    embed-NN.html   prerendered HTML, one Webflow Embed element each (< 50,000 characters)
    head.html       paste into Page settings > Custom code > Inside <head> tag
    footer.html     paste into Page settings > Custom code > Before </body> tag

Images, CSS and JS are served by jsDelivr from this repo, pinned to a commit:
assets/ at the commit this build runs on (ASSET_SHA = HEAD), landing.css/js at the
commit that contains the build output (passed to `snippets`).
Prerendering uses headless Google Chrome.
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
out = repo / 'webflow' / 'landing'
CDN = 'https://cdn.jsdelivr.net/gh/floumate-dev/nutribox@{sha}/'
JELOVNIK_URL = '/jelovnik'     # Webflow URL of the menu page (not decided yet)
EMBED_LIMIT = 48000            # Webflow allows 50,000 characters per Embed element
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# Webflow's webflow.css restyles bare elements (h1-h6, p, img, figure, ...), sets
# body to 14px/20px Arial and box-sizing: border-box on everything. The design was
# made on browser defaults, so restore them inside the page. :where(.nbx-part) adds no
# specificity and :is(h1, ...) counts as one element, the same as webflow.css; this file
# loads later, so it wins there, while the design's classes and inline styles still win here.
WEBFLOW_RESET = """/* Webflow embeds that hold the page do not create boxes, so position: sticky
   (top bar) works against the whole page and sections stay full width. */
.w-embed:has(> .nbx-part), .nbx-part, .nbx-part > div { display: contents; }
.w-embed:has(> .nbx-part)::before, .w-embed:has(> .nbx-part)::after { content: none; }
.nbx-part { font-size: 16px; line-height: normal; }
:where(.nbx-part, .nbx-part *, .nbx-part *::before, .nbx-part *::after) { box-sizing: revert; }
:where(.nbx-part) :is(h1, h2, h3, h4, h5, h6, p, ul, ol, li, figure, figcaption, blockquote, label) {
  margin: revert; padding: revert; font-size: revert; line-height: revert; font-weight: revert;
  text-align: revert; display: revert;
}
:where(.nbx-part) img { max-width: none; vertical-align: baseline; display: inline; }
:where(.nbx-part) :is(button, input, select, textarea) { line-height: normal; }
"""


def git_head():
    return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def template(asset_base, index):
    t = (repo / 'design' / 'Main.dc.html').read_text()
    t = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: asset_base + index[m.group(1)]['file'], t)
    t = t.replace('href="Jelovnik.dc.html"', f'href="{JELOVNIK_URL}"')
    helmet = re.search(r'<helmet>(.*?)</helmet>', t, re.S).group(1)
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', helmet, re.S)).strip()
    fonts = re.findall(r'<link rel="stylesheet" href="([^"]+)">', helmet)
    t = t.replace(helmet, '')
    t, css = prefix_classes(t, css)
    return t, css, fonts


# The page lives in a Webflow site whose shared CSS has its own classes (e.g. .slider),
# and Webflow reserves w-*. Prefix every class the design defines with nbx-.
PREFIX = 'nbx-'
# Class names built in the component's JS; each must match exactly once.
JS_CLASSES = [
    ("cls: open ? 'faq-item faq-open' : 'faq-item',", "cls: open ? 'nbx-faq-item nbx-faq-open' : 'nbx-faq-item',"),
    ("? 'w-hide' : ''", "? 'nbx-w-hide' : ''"),
    ("sp: 'sp' + spIdx,", "sp: 'nbx-sp' + spIdx,"),
]


def prefix_classes(t, css):
    plain = re.sub(r'url\([^)]*\)', '', re.sub(r'/\*.*?\*/', '', css, flags=re.S))
    names = set(re.findall(r'\.(-?[_a-zA-Z][\w-]*)', plain))
    sel = re.compile(r'(?<![\w-])\.(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')(?![\w-])')
    # only outside url(...) in the CSS
    css = re.sub(r'(url\([^)]*\))|' + sel.pattern, lambda m: m.group(1) or '.' + PREFIX + m.group(2), css)

    def attr(m):
        toks = [PREFIX + x if x in names else x for x in m.group(1).split(' ')]
        return 'class="' + ' '.join(toks) + '"'
    head, sep, script = t.partition('<script type="text/x-dc"')
    head = re.sub(r'class="([^"]*)"', attr, head)
    for a, b in JS_CLASSES:
        if script.count(a) != 1:
            raise SystemExit(f'build_webflow: expected one {a!r} in Main.dc.html, update JS_CLASSES')
        script = script.replace(a, b)
    return head + sep + script, css


def prerender(js_path, css_path, ranges):
    """Render each range of sections in headless Chrome and return the HTML of each mount."""
    parts = ''.join(f'<div class="w-embed"><div class="nbx-part" data-dc-part="{a}-{b}"></div></div>\n' for a, b in ranges)
    page = f'''<!doctype html><html lang="sr"><head><meta charset="utf-8">
<link rel="stylesheet" href="{css_path.as_uri()}"></head><body>
{parts}<textarea id="nbx-out"></textarea>
<script src="{js_path.as_uri()}"></script>
<script>document.getElementById('nbx-out').textContent = JSON.stringify(
  [...document.querySelectorAll('.nbx-part')].map(p => p.innerHTML));</script>
</body></html>'''
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'prerender.html'
        f.write_text(page)
        dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--allow-file-access-from-files',
                              '--virtual-time-budget=3000', '--dump-dom', f.as_uri()],
                             capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<textarea id="nbx-out">(.*?)</textarea>', dom, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit('prerender failed: no output from Chrome')
    return json.loads(html.unescape(m.group(1)))


def embed_html(a, b, inner):
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    return f'<div class="nbx-part" data-dc-part="{a}-{b}">{inner}</div>\n'


def build():
    index = json.loads((repo / 'assets/index.json').read_text())
    asset_sha = git_head()
    asset_base = CDN.format(sha=asset_sha) + 'assets/'
    tpl, css, fonts = template(asset_base, index)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('embed-*.html'):
        old.unlink()

    (out / 'landing.css').write_text(
        f'/* Nutribox landing for Webflow. Built by tools/build_webflow.py from design/Main.dc.html. */\n'
        f'{WEBFLOW_RESET}\n/* Design CSS (design/Main.dc.html <helmet>) */\n{css}\n')
    runtime = (repo / 'preview' / 'dc-runtime.js').read_text()
    blobs = {k: v['file'] for k, v in index.items()}
    (out / 'landing.js').write_text(
        '/* Nutribox landing for Webflow. Built by tools/build_webflow.py from design/Main.dc.html. */\n'
        f'window.DC_SOURCES = {{ Main: {json.dumps(tpl, ensure_ascii=False)} }};\n'
        f'window.DC_BLOBS = {json.dumps(blobs)};\n'
        f'window.DC_ASSET_BASE = {json.dumps(asset_base)};\n'
        'window.DC_NO_HELMET = true;\n'
        f'{runtime}\n'
        'DCMountParts("Main", ".nbx-part[data-dc-part]");\n')
    (out / 'fonts.json').write_text(json.dumps(fonts))

    # Pass 1: size of every section on its own; pass 2: render the final groups.
    singles = prerender(out / 'landing.js', out / 'landing.css', [(i, i) for i in range(17)])
    sizes = [len(embed_html(i, i, h)) for i, h in enumerate(singles)]
    groups, cur = [], None
    for i, s in enumerate(sizes):
        if s > EMBED_LIMIT:
            raise SystemExit(f'section {i} alone is {s} characters, over the Embed limit')
        if cur and cur[2] + s <= EMBED_LIMIT:
            cur = (cur[0], i, cur[2] + s)
        else:
            if cur:
                groups.append(cur)
            cur = (i, i, s)
    groups.append(cur)
    rendered = prerender(out / 'landing.js', out / 'landing.css', [(a, b) for a, b, _ in groups])
    for n, ((a, b, _), inner) in enumerate(zip(groups, rendered), 1):
        h = embed_html(a, b, inner)
        if len(h) > 50000:
            raise SystemExit(f'embed {n} is {len(h)} characters')
        (out / f'embed-{n:02d}.html').write_text(h)
        print(f'embed-{n:02d}.html  sections {a}-{b}  {len(h):,} characters')
    print('section sizes:', sizes)
    print('assets pinned to', asset_sha)


def snippets(code_sha):
    base = CDN.format(sha=code_sha) + 'webflow/landing/'
    fonts = json.loads((out / 'fonts.json').read_text())
    font_links = ''.join(f'<link rel="stylesheet" href="{html.escape(f)}">\n' for f in fonts)
    (out / 'head.html').write_text(
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
        f'{font_links}<link rel="stylesheet" href="{base}landing.css">\n')
    (out / 'footer.html').write_text(f'<script src="{base}landing.js" defer></script>\n')
    print((out / 'head.html').read_text() + (out / 'footer.html').read_text())


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'build':
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == 'snippets':
        snippets(sys.argv[2])
    else:
        raise SystemExit(__doc__)
