"""Build the Webflow versions of the pages (Serbian, English, Russian).

Run from the repo root:
    python3 tools/build_webflow.py build [page ...]          # CSS, JS and embeds (default: all pages)
    python3 tools/build_webflow.py snippets <sha> [page ...] # head.html, footer.html for commit <sha>

Pages:
    landing   design/Main[.en|.ru].dc.html                    -> webflow/landing/
    jelovnik  design/Jelovnik[.en|.ru].dc.html (+ Main parts) -> webflow/jelovnik/

Output per page directory:
    <page>.css           page CSS (Webflow reset scoped to the page + the design's CSS), all locales
    <page>.<lang>.js     runtime + that locale's templates; takes over the prerendered HTML
    embed-<lang>-NN.html prerendered HTML, one Webflow Embed element each (< 50,000 characters)
    head.html            Page settings > Custom code > Inside <head> tag
    footer.html          Page settings > Custom code > Before </body> tag (loads the JS for the
                         page's <html lang>)

Images, CSS and JS are served by jsDelivr from this repo, pinned to a commit:
assets/ at the commit this build runs on (HEAD), the page files at the commit that
contains the build output (passed to `snippets`). Prerendering uses headless Google Chrome.
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
CDN = 'https://cdn.jsdelivr.net/gh/floumate-dev/nutribox@{sha}/'
LANGS = ['sr', 'en', 'ru']
# Webflow URLs of the pages (the menu page URL is not decided yet)
LANDING_URL = {'sr': '/', 'en': '/en', 'ru': '/ru'}
JELOVNIK_URL = {'sr': '/jelovnik', 'en': '/en/jelovnik', 'ru': '/ru/jelovnik'}
EMBED_LIMIT = 48000            # Webflow allows 50,000 characters per Embed element
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# Outfit has no Cyrillic; Onest fills in Cyrillic glyphs (browsers only download it
# when a page actually uses them).
FONTS = ['https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800'
         '&family=Onest:wght@300;400;500;600;700;800&display=swap']

# Root wrapper of every component (Main, Jelovnik): it gets class nbx-root and no box.
ROOT_DIV = '<div style="width: 100%; background: #ffffff; color: #123c32; font-family: \'Outfit\', ui-sans-serif'

# Webflow's webflow.css restyles bare elements (h1-h6, p, img, figure, ...), sets
# body to 14px/20px Arial and box-sizing: border-box on everything. The design was
# made on browser defaults, so restore them inside the page. :where(.nbx-part) adds no
# specificity and :is(h1, ...) counts as one element, the same as webflow.css; this file
# loads later, so it wins there, while the design's classes and inline styles still win here.
WEBFLOW_RESET = """/* Webflow embeds that hold the page, and the components' root wrappers, do not
   create boxes, so position: sticky (top bar) works against the whole page and
   sections stay full width. */
.w-embed:has(> .nbx-part), .nbx-part, .nbx-part > div, .nbx-root { display: contents; }
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
   top of the page; the page JS puts a copy in the header (wide screens) or in a slot
   near the top of the content (narrow screens) and hides the floating one. */
.nbx-lang-hdr, .nbx-lang-hero { display: none; }
.nbx-lang-hdr:not(:empty) { display: flex; }
.nbx-lang-hero { position: absolute; top: 2px; right: 0; }
@media (max-width: 899px) {
  .nbx-lang-hdr:not(:empty) { display: none; }
  .nbx-lang-hero:not(:empty) { display: flex; }
}
.nbx-lang-hdr .nb-jezik, .nbx-lang-hero .nb-jezik { font-family: inherit; }
.nbx-jl-intro { position: relative; }
.nbx-jl-intro > .nbx-lang-hero { top: 7px; }
"""

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

# Per component: class names built in its JS (must match exactly once) and switcher
# slots inserted after the classes are prefixed. Anchors are markup that the
# translations keep unchanged (check_translation.py enforces that).
COMPONENTS = {
    'Main': {
        'js_classes': [
            ("cls: open ? 'faq-item faq-open' : 'faq-item',", "cls: open ? 'nbx-faq-item nbx-faq-open' : 'nbx-faq-item',"),
            ("? 'w-hide' : ''", "? 'nbx-w-hide' : ''"),
            ("sp: 'sp' + spIdx,", "sp: 'nbx-sp' + spIdx,"),
        ],
        'slots': [
            ('<a class="nbx-hide-sm" href="tel:0800001007"',
             '<div class="nbx-lang-hdr" data-dc-keep="lang"></div>\n<a class="nbx-hide-sm" href="tel:0800001007"'),
            ('<div class="nbx-hero-txt" style="position: relative; z-index: 2; flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">',
             '<div class="nbx-hero-txt" style="position: relative; z-index: 2; flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">\n<div class="nbx-lang-hero" data-dc-keep="lang"></div>'),
        ],
    },
    'Jelovnik': {
        'js_classes': [
            ("MEALS[r[2]], 'jl-po',", "MEALS[r[2]], 'nbx-jl-po',"),
            ("const cls = 'jl-wk jl-s' + (mi * 3 + wk);", "const cls = 'nbx-jl-wk nbx-jl-s' + (mi * 3 + wk);"),
        ],
        'slots': [
            ('<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 22px">\n<a class="nbx-jl-back"',
             '<div class="nbx-jl-intro" style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 22px">\n'
             '<div class="nbx-lang-hero" data-dc-keep="lang"></div>\n<a class="nbx-jl-back"'),
        ],
    },
}

PAGES = {
    'landing': {'root': 'Main', 'components': ['Main'], 'mode': 'parts', 'count': 17},
    'jelovnik': {'root': 'Jelovnik', 'components': ['Jelovnik', 'Main'], 'mode': 'slices', 'count': 12},
}


# Extra code always added to a page's head snippet (requested by the client).
HEAD_EXTRA = {
    'landing': '<style>\n  .nb-jezik-red { display: none !important; }\n</style>\n',
}


def git_head():
    return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def source(name, lang):
    return repo / 'design' / (f'{name}.dc.html' if lang == 'sr' else f'{name}.{lang}.dc.html')


def css_classes(css):
    plain = re.sub(r'url\([^)]*\)', '', re.sub(r'/\*.*?\*/', '', css, flags=re.S))
    return set(re.findall(r'\.(-?[_a-zA-Z][\w-]*)', plain))


PREFIX = 'nbx-'


def prefix_css(css, names):
    sel = r'(?<![\w-])\.(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')(?![\w-])'
    return re.sub(r'(url\([^)]*\))|' + sel, lambda m: m.group(1) or '.' + PREFIX + m.group(2), css)


def prefix_template(t, names, js_classes):
    def attr(m):
        toks = [PREFIX + x if x in names else x for x in m.group(1).split(' ')]
        return 'class="' + ' '.join(toks) + '"'
    head, sep, script = t.partition('<script type="text/x-dc"')
    head = re.sub(r'class="([^"]*)"', attr, head)
    for a, b in js_classes:
        if script.count(a) != 1:
            raise SystemExit(f'build_webflow: expected one {a!r} in the template, update COMPONENTS')
        script = script.replace(a, b)
    return head + sep + script


def load_component(name, lang, asset_base, index):
    """Template text (helmet removed) and its CSS, with assets, links and fonts set."""
    t = source(name, lang).read_text()
    t = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: asset_base + index[m.group(1)]['file'], t)
    t = t.replace('href="Jelovnik.dc.html"', f'href="{JELOVNIK_URL[lang]}"')
    t = t.replace('href="Main.dc.html"', f'href="{LANDING_URL[lang]}"')
    t = t.replace("font-family: 'Outfit', ui-sans-serif", "font-family: 'Outfit', 'Onest', ui-sans-serif")
    if t.count(ROOT_DIV.replace("'Outfit', ui", "'Outfit', 'Onest', ui")) != 1:
        raise SystemExit(f'build_webflow: root wrapper not found in {source(name, lang).name}')
    t = t.replace('<div style="width: 100%; background: #ffffff; color: #123c32; font-family:',
                  '<div class="nbx-root" style="width: 100%; background: #ffffff; color: #123c32; font-family:', 1)
    helmet = re.search(r'<helmet>(.*?)</helmet>', t, re.S).group(1)
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', helmet, re.S)).strip()
    return t.replace(helmet, ''), css


def page_sources(page, lang, asset_base, index):
    comps = {c: load_component(c, lang, asset_base, index) for c in PAGES[page]['components']}
    names = set().union(*(css_classes(css) for _, css in comps.values()))
    out = {}
    for c, (t, css) in comps.items():
        t = prefix_template(t, names, COMPONENTS[c]['js_classes'])
        for a, b in COMPONENTS[c]['slots']:
            if t.count(a) != 1:
                raise SystemExit(f'build_webflow: {c} ({lang}): switcher slot anchor not found: {a[:60]!r}')
            t = t.replace(a, b)
        out[c] = (t, prefix_css(css, names))
    return out


def prerender(js_path, css_path, lang, mode, ranges):
    """Render each range in headless Chrome; return (inner HTML, root child count) per mount."""
    attr = 'data-dc-part' if mode == 'parts' else 'data-dc-slice'
    mounts = ''.join(f'<div class="w-embed"><div class="nbx-part" {attr}="{a}-{b}" data-dc-lang="{lang}"></div></div>\n' for a, b in ranges)
    page = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<link rel="stylesheet" href="{css_path.as_uri()}"></head><body>
{mounts}<textarea id="nbx-out"></textarea>
<script src="{js_path.as_uri()}"></script>
<script>document.getElementById('nbx-out').textContent = JSON.stringify(
  [...document.querySelectorAll('.nbx-part')].map(p => [p.innerHTML, p.firstElementChild ? p.firstElementChild.childElementCount : 0]));</script>
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


def embed_html(mode, a, b, lang, inner):
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    attr = 'data-dc-part' if mode == 'parts' else 'data-dc-slice'
    return f'<div class="nbx-part" {attr}="{a}-{b}" data-dc-lang="{lang}">{inner}</div>\n'


def build_page(page, asset_base, blobs, runtime, index):
    cfg = PAGES[page]
    out = repo / 'webflow' / page
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob('embed-*.html')) + list(out.glob('*.js')) + list(out.glob('*.css')):
        old.unlink()
    css_out = None
    mount = 'DCMountParts' if cfg['mode'] == 'parts' else 'DCMountSlices'
    attr = 'data-dc-part' if cfg['mode'] == 'parts' else 'data-dc-slice'
    for lang in LANGS:
        srcs = page_sources(page, lang, asset_base, index)
        css = '\n'.join(c for _, c in srcs.values())
        if css_out is None:
            css_out = css
            (out / f'{page}.css').write_text(
                f'/* Nutribox {page} for Webflow. Built by tools/build_webflow.py. */\n'
                f'{WEBFLOW_RESET}\n/* Design CSS (<helmet> of {", ".join(cfg["components"])}) */\n{css}\n')
        elif css != css_out:
            raise SystemExit(f'build_webflow: {page}: the CSS of the {lang} templates differs from the Serbian ones')
        js = out / f'{page}.{lang}.js'
        sources_js = ', '.join(f'{c}: {json.dumps(t, ensure_ascii=False)}' for c, (t, _) in srcs.items())
        js.write_text(
            f'/* Nutribox {page} ({lang}) for Webflow. Built by tools/build_webflow.py. */\n'
            f'window.DC_SOURCES = {{ {sources_js} }};\n'
            f'window.DC_BLOBS = {json.dumps(blobs)};\n'
            f'window.DC_ASSET_BASE = {json.dumps(asset_base)};\n'
            'window.DC_NO_HELMET = true;\n'
            f'{runtime}\n'
            '(function () {\n'
            '  // this locale\'s embeds; if the page only has another locale\'s embeds, take those over\n'
            f'  var own = document.querySelector(\'.nbx-part[data-dc-lang="{lang}"]\');\n'
            f'  {mount}("{cfg["root"]}", own ? \'.nbx-part[data-dc-lang="{lang}"]\' : ".nbx-part[{attr}]");\n'
            '})();\n'
            f'{LANG_JS}{ANCHOR_JS}')

        # Pass 1: size of every unit (section or root child) on its own; pass 2: final groups.
        singles = prerender(js, out / f'{page}.css', lang, cfg['mode'], [(i, i) for i in range(cfg['count'])])
        if cfg['mode'] == 'slices':
            singles = [s for s in singles if s[1] > 0]   # slices past the last root child are empty
        sizes = [len(embed_html(cfg['mode'], i, i, lang, h)) for i, (h, _) in enumerate(singles)]
        groups, cur = [], None
        for i, s in enumerate(sizes):
            if s > EMBED_LIMIT:
                raise SystemExit(f'{page} {lang}: unit {i} alone is {s} characters, over the Embed limit')
            if cur and cur[2] + s <= EMBED_LIMIT:
                cur = (cur[0], i, cur[2] + s)
            else:
                if cur:
                    groups.append(cur)
                cur = (i, i, s)
        groups.append(cur)
        rendered = prerender(js, out / f'{page}.css', lang, cfg['mode'], [(a, b) for a, b, _ in groups])
        for k, ((a, b, _), (inner, _)) in enumerate(zip(groups, rendered), 1):
            h = embed_html(cfg['mode'], a, b, lang, inner)
            if len(h) > 50000:
                raise SystemExit(f'{page} {lang}: embed {k} is {len(h)} characters')
            (out / f'embed-{lang}-{k:02d}.html').write_text(h)
            print(f'{page}/embed-{lang}-{k:02d}.html  units {a}-{b}  {len(h):,} characters')
    (out / 'fonts.json').write_text(json.dumps(FONTS))


def build(pages):
    index = json.loads((repo / 'assets/index.json').read_text())
    asset_sha = git_head()
    asset_base = CDN.format(sha=asset_sha) + 'assets/'
    runtime = (repo / 'preview' / 'dc-runtime.js').read_text()
    blobs = {k: v['file'] for k, v in index.items()}
    for page in pages:
        build_page(page, asset_base, blobs, runtime, index)
    print('assets pinned to', asset_sha)


def snippets(code_sha, pages):
    for page in pages:
        out = repo / 'webflow' / page
        base = CDN.format(sha=code_sha) + f'webflow/{page}/'
        fonts = json.loads((out / 'fonts.json').read_text())
        font_links = ''.join(f'<link rel="stylesheet" href="{html.escape(html.unescape(f))}">\n' for f in fonts)
        (out / 'head.html').write_text(
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="preconnect" href="https://cdn.jsdelivr.net">\n'
            f'{font_links}<link rel="stylesheet" href="{base}{page}.css">\n'
            + (HEAD_EXTRA.get(page, '')))
        langs = '|'.join(l for l in LANGS if l != 'sr')
        (out / 'footer.html').write_text(
            '<script>\n'
            '(function () {\n'
            "  var l = (document.documentElement.lang || 'sr').slice(0, 2).toLowerCase();\n"
            f"  if (!/^({langs})$/.test(l)) l = 'sr';\n"
            "  var s = document.createElement('script');\n"
            f"  s.src = '{base}{page}.' + l + '.js';\n"
            '  document.body.appendChild(s);\n'
            '})();\n'
            '</script>\n')
        print(f'--- {page}\n' + (out / 'head.html').read_text() + (out / 'footer.html').read_text())


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'build':
        build(args[1:] or list(PAGES))
    elif len(args) >= 2 and args[0] == 'snippets':
        snippets(args[1], args[2:] or list(PAGES))
    else:
        raise SystemExit(__doc__)
