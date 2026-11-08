"""Build the Webflow version of the landing page (Serbian, English, Russian) into webflow/landing/.

Run from the repo root:
    python3 tools/build_webflow.py build              # CSS, JS and embeds for every locale
    python3 tools/build_webflow.py snippets <sha>     # head.html, footer.html for commit <sha>

Sources: design/Main.dc.html (sr), design/Main.en.dc.html (en), design/Main.ru.dc.html (ru).

Output (webflow/landing/):
    landing.css          page CSS (Webflow reset scoped to the page + the design's CSS), all locales
    landing.<lang>.js    runtime + that locale's template; takes over the prerendered HTML
    embed-<lang>-NN.html prerendered HTML, one Webflow Embed element each (< 50,000 characters)
    head.html            Page settings > Custom code > Inside <head> tag
    footer.html          Page settings > Custom code > Before </body> tag (loads the JS for the
                         page's <html lang>)

Images, CSS and JS are served by jsDelivr from this repo, pinned to a commit:
assets/ at the commit this build runs on (HEAD), landing.* at the commit that contains
the build output (passed to `snippets`). Prerendering uses headless Google Chrome.
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
LOCALES = {
    # lang: (template, URL of the menu page on Webflow; not decided yet)
    'sr': ('Main.dc.html', '/jelovnik'),
    'en': ('Main.en.dc.html', '/en/jelovnik'),
    'ru': ('Main.ru.dc.html', '/ru/jelovnik'),
}
EMBED_LIMIT = 48000            # Webflow allows 50,000 characters per Embed element
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# Outfit has no Cyrillic; Onest fills in Cyrillic glyphs (browsers only download it
# when a page actually uses them).
FONTS = ['https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800'
         '&family=Onest:wght@300;400;500;600;700;800&display=swap']

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

/* Locales: when the page has embeds for its own language, hide the other languages'
   embeds (in case Webflow locale visibility was not set on them). */
html[lang^="sr"]:has(.nbx-part[data-dc-lang="sr"]) .nbx-part[data-dc-lang]:not([data-dc-lang="sr"]),
html[lang^="en"]:has(.nbx-part[data-dc-lang="en"]) .nbx-part[data-dc-lang]:not([data-dc-lang="en"]),
html[lang^="ru"]:has(.nbx-part[data-dc-lang="ru"]) .nbx-part[data-dc-lang]:not([data-dc-lang="ru"]) { display: none; }

/* Language switcher: the site-wide script builds .nb-jezik in a box floating over the
   top of the page; landing.js puts a copy in the header (wide screens) or next to the
   hero badge (narrow screens) and hides the floating one. */
.nbx-lang-hdr, .nbx-lang-hero { display: none; }
.nbx-lang-hdr:not(:empty) { display: flex; }
.nbx-lang-hero { position: absolute; top: 2px; right: 0; }
@media (max-width: 899px) {
  .nbx-lang-hdr:not(:empty) { display: none; }
  .nbx-lang-hero:not(:empty) { display: flex; }
}
.nbx-lang-hdr .nb-jezik, .nbx-lang-hero .nb-jezik { font-family: inherit; }
"""

# Slots for the language switcher, inserted into every locale's template after the
# classes are prefixed. The anchors are markup that translations keep unchanged
# (check_translation.py enforces that).
SLOTS = [
    ('<a class="nbx-hide-sm" href="tel:0800001007"',
     '<div class="nbx-lang-hdr" data-dc-keep="lang"></div>\n<a class="nbx-hide-sm" href="tel:0800001007"'),
    ('<div class="nbx-hero-txt" style="position: relative; z-index: 2; flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">',
     '<div class="nbx-hero-txt" style="position: relative; z-index: 2; flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">\n<div class="nbx-lang-hero" data-dc-keep="lang"></div>'),
]

LANG_JS = r"""
(function () {
  // Copy the site's language switcher (.nb-jezik, built by the site-wide script) into
  // the page's slots and hide the floating original.
  function place() {
    var nav = document.querySelector('.nb-jezik-red .nb-jezik');
    if (!nav) return false;
    document.querySelectorAll('[data-dc-keep="lang"]').forEach(function (slot) {
      if (!slot.firstChild) slot.appendChild(nav.cloneNode(true));
    });
    nav.closest('.nb-jezik-red').style.display = 'none';
    return true;
  }
  if (!place()) {
    var mo = new MutationObserver(function () { if (place()) mo.disconnect(); });
    mo.observe(document.body, { childList: true });
    setTimeout(function () { mo.disconnect(); }, 10000);
  }
})();
"""


# Webflow's webflow.js takes over clicks on same-page #links and animates the scroll
# itself with window.scroll() on every frame; with html { scroll-behavior: smooth } from
# the design each of those calls starts a new smooth scroll, so the jump crawls and
# lags, and it ignores the sticky top bar. Handle the page's own #links first (capture
# phase, before Webflow's delegated handler) with a native scroll that respects
# scroll-margin-top and reduced motion.
ANCHOR_JS = r"""
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('.nbx-part a[href^="#"]');
  if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  var id = decodeURIComponent(a.getAttribute('href').slice(1));
  var el = id && document.getElementById(id);
  if (!el) return;
  e.preventDefault();
  e.stopPropagation();
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  if (history.pushState && location.hash !== '#' + id) history.pushState(null, '', '#' + id);
}, true);
"""


def git_head():
    return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def template(lang, asset_base, index):
    name, jelovnik_url = LOCALES[lang]
    t = (repo / 'design' / name).read_text()
    t = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: asset_base + index[m.group(1)]['file'], t)
    t = t.replace('href="Jelovnik.dc.html"', f'href="{jelovnik_url}"')
    t = t.replace("font-family: 'Outfit', ui-sans-serif", "font-family: 'Outfit', 'Onest', ui-sans-serif")
    helmet = re.search(r'<helmet>(.*?)</helmet>', t, re.S).group(1)
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', helmet, re.S)).strip()
    t = t.replace(helmet, '')
    t, css = prefix_classes(t, css)
    for a, b in SLOTS:
        if t.count(a) != 1:
            raise SystemExit(f'build_webflow: {name}: switcher slot anchor not found: {a[:60]!r}')
        t = t.replace(a, b)
    return t, css


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
            raise SystemExit(f'build_webflow: expected one {a!r} in the template, update JS_CLASSES')
        script = script.replace(a, b)
    return head + sep + script, css


def prerender(js_path, css_path, lang, ranges):
    """Render each range of sections in headless Chrome and return the HTML of each mount."""
    parts = ''.join(f'<div class="w-embed"><div class="nbx-part" data-dc-part="{a}-{b}" data-dc-lang="{lang}"></div></div>\n' for a, b in ranges)
    page = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
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


def embed_html(a, b, lang, inner):
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    return f'<div class="nbx-part" data-dc-part="{a}-{b}" data-dc-lang="{lang}">{inner}</div>\n'


def build():
    index = json.loads((repo / 'assets/index.json').read_text())
    asset_sha = git_head()
    asset_base = CDN.format(sha=asset_sha) + 'assets/'
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob('embed-*.html')) + list(out.glob('landing*.js')):
        old.unlink()
    runtime = (repo / 'preview' / 'dc-runtime.js').read_text()
    blobs = {k: v['file'] for k, v in index.items()}
    css_out = None
    for lang in LOCALES:
        tpl, css = template(lang, asset_base, index)
        if css_out is None:
            css_out = css
            (out / 'landing.css').write_text(
                f'/* Nutribox landing for Webflow. Built by tools/build_webflow.py from design/Main*.dc.html. */\n'
                f'{WEBFLOW_RESET}\n/* Design CSS (design/Main.dc.html <helmet>) */\n{css}\n')
        elif css != css_out:
            raise SystemExit(f'build_webflow: the CSS in {LOCALES[lang][0]} differs from Main.dc.html')
        js = out / f'landing.{lang}.js'
        js.write_text(
            f'/* Nutribox landing ({lang}) for Webflow. Built by tools/build_webflow.py from design/{LOCALES[lang][0]}. */\n'
            f'window.DC_SOURCES = {{ Main: {json.dumps(tpl, ensure_ascii=False)} }};\n'
            f'window.DC_BLOBS = {json.dumps(blobs)};\n'
            f'window.DC_ASSET_BASE = {json.dumps(asset_base)};\n'
            'window.DC_NO_HELMET = true;\n'
            f'{runtime}\n'
            '(function () {\n'
            f'  // this locale\'s embeds; if the page only has another locale\'s embeds, take those over\n'
            f'  var own = document.querySelector(\'.nbx-part[data-dc-lang="{lang}"]\');\n'
            f'  DCMountParts("Main", own ? \'.nbx-part[data-dc-lang="{lang}"]\' : ".nbx-part[data-dc-part]");\n'
            '})();\n'
            f'{LANG_JS}{ANCHOR_JS}')

        # Pass 1: size of every section on its own; pass 2: render the final groups.
        singles = prerender(js, out / 'landing.css', lang, [(i, i) for i in range(17)])
        sizes = [len(embed_html(i, i, lang, h)) for i, h in enumerate(singles)]
        groups, cur = [], None
        for i, s in enumerate(sizes):
            if s > EMBED_LIMIT:
                raise SystemExit(f'{lang}: section {i} alone is {s} characters, over the Embed limit')
            if cur and cur[2] + s <= EMBED_LIMIT:
                cur = (cur[0], i, cur[2] + s)
            else:
                if cur:
                    groups.append(cur)
                cur = (i, i, s)
        groups.append(cur)
        rendered = prerender(js, out / 'landing.css', lang, [(a, b) for a, b, _ in groups])
        for n, ((a, b, _), inner) in enumerate(zip(groups, rendered), 1):
            h = embed_html(a, b, lang, inner)
            if len(h) > 50000:
                raise SystemExit(f'{lang}: embed {n} is {len(h)} characters')
            (out / f'embed-{lang}-{n:02d}.html').write_text(h)
            print(f'embed-{lang}-{n:02d}.html  sections {a}-{b}  {len(h):,} characters')
    (out / 'fonts.json').write_text(json.dumps(FONTS))
    print('assets pinned to', asset_sha)


def snippets(code_sha):
    base = CDN.format(sha=code_sha) + 'webflow/landing/'
    fonts = json.loads((out / 'fonts.json').read_text())
    font_links = ''.join(f'<link rel="stylesheet" href="{html.escape(html.unescape(f))}">\n' for f in fonts)
    (out / 'head.html').write_text(
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="preconnect" href="https://cdn.jsdelivr.net">\n'
        f'{font_links}<link rel="stylesheet" href="{base}landing.css">\n')
    langs = '|'.join(l for l in LOCALES if l != 'sr')
    (out / 'footer.html').write_text(
        '<script>\n'
        '(function () {\n'
        "  var l = (document.documentElement.lang || 'sr').slice(0, 2).toLowerCase();\n"
        f"  if (!/^({langs})$/.test(l)) l = 'sr';\n"
        "  var s = document.createElement('script');\n"
        f"  s.src = '{base}landing.' + l + '.js';\n"
        '  document.body.appendChild(s);\n'
        '})();\n'
        '</script>\n')
    print((out / 'head.html').read_text() + (out / 'footer.html').read_text())


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'build':
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == 'snippets':
        snippets(sys.argv[2])
    else:
        raise SystemExit(__doc__)
