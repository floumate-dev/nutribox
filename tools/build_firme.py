"""Business page (firme/): Danilo's two Webflow Embeds with our changes on top.

    python3 tools/build_firme.py
    python3 tools/build_embed_preview.py firme "Nutribox za firme"

Sources: firme/src/embed-01.html (fonts + CSS) and firme/src/embed-02.html (markup + JS),
copied unchanged from the published Webflow page "Firma". Output: firme/embed-01.html and
firme/embed-02.html, the code to paste into the two Embeds. Edit this script, not the output.

Changes:
- hero: the landing's food visual (#nbx-hero-food) instead of the lead form; the
  "Zakaži razgovor" button, until now phone-only, shows on every screen
- final CTA: no form; heading, text, checks, button and phone centred in one column
"""
import re
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
src = repo / 'firme' / 'src'
out = repo / 'firme'
CTA = 'https://app.iclosed.io/e/nutribox/besplatan-poziv-za-firme'
ARROW = '<svg class="arr" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>'


def one(text, old, new):
    assert text.count(old) == 1, (text.count(old), old[:80])
    return text.replace(old, new)


def block(text, start, tag):
    """The element that starts at `start` (an opening <tag ...>), through its matching close."""
    i = text.index(start)
    depth = 0
    for m in re.finditer(rf'<{tag}\b|</{tag}>', text[i:]):
        depth += 1 if m.group(0) != f'</{tag}>' else -1
        if depth == 0:
            return text[i:i + m.end()]
    raise ValueError(start)


def hero_food():
    """The landing hero's food collage, same images (pinned jsDelivr URLs) as the landing."""
    land = (repo / 'webflow' / 'landing' / 'embed-sr-01.html').read_text()
    food = block(land, '<div id="nbx-hero-food"', 'div')
    assert food.count('<img ') == 5
    return food


CSS = '''<style>
/* firme: hero visual from the landing (instead of the form) */
.nbl .hero{overflow-x:clip}
.nbl .bh.nbf-bh{grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.nbl .nbf-vis{min-width:0}
.nbl #nbx-hero-food{position:relative;width:100%;aspect-ratio:590/516}
.nbl #nbx-hero-food img{position:absolute;height:auto;max-width:none;filter:drop-shadow(8px 16px 18px rgba(18,60,50,.22));animation:nbxFadeInRight 1s ease both}
.nbl #nbx-hero-food .nbx-k{left:52.85%;top:0;width:47.15%;z-index:1;transform:rotate(3deg);animation-delay:.3s}
.nbl #nbx-hero-food .nbx-r{left:0;top:45.29%;width:64.63%;z-index:4;transform:rotate(-3deg);animation-delay:.8s}
.nbl #nbx-hero-food .nbx-v{left:47.15%;top:45.29%;width:38.01%;z-index:5;transform:rotate(-5deg);animation-delay:1.3s}
.nbl #nbx-hero-food .nbx-u{left:58.54%;top:71.65%;width:41.06%;z-index:6;transform:rotate(-4deg);animation-delay:1.8s}
.nbl #nbx-hero-food .nbx-d{left:5.69%;top:6.88%;width:50.2%;z-index:3;transform:rotate(4deg);animation-delay:2.3s}
@keyframes nbxFadeInRight{from{opacity:0;translate:100% 0}to{opacity:1;translate:0 0}}
@media (min-width:768px){.nbl .bh .bh-cta{align-items:flex-start}.nbl .bh .bh-cta p{text-align:left}}
@media (max-width:991px){.nbl .bh.nbf-bh{grid-template-columns:1fr}.nbl #nbx-hero-food{max-width:520px;margin:0 auto}}
@media (max-width:767px){.nbl .nbf-vis{margin-top:28px}}
@media (prefers-reduced-motion:reduce){.nbl #nbx-hero-food img{animation:none}}
/* firme: final CTA without the form, everything centred */
.nbl .fs-g.nbf-fin{grid-template-columns:1fr;max-width:760px;margin:0 auto;justify-items:center}
.nbl .nbf-fin .fs-t{align-items:center;text-align:center}
.nbl .nbf-chks{display:flex;flex-wrap:wrap;justify-content:center;gap:12px 28px}
.nbl .nbf-fin .fs-ph{text-align:center!important}
@media (max-width:767px){.nbl .nbf-chks{flex-direction:column;align-items:center}}
</style>'''


def build_css(s):
    return s + CSS


def build_markup(s):
    # hero: form -> landing visual, CTA button on every screen
    form = block(s, '<form class="lf desk"', 'form')
    s = one(s, form, f'<div class="nbf-vis">{hero_food()}</div>')
    s = one(s, '<div class="bh">', '<div class="bh nbf-bh">')
    s = one(s, '<div class="bh-cta mob">', '<div class="bh-cta">')

    # final CTA: one centred column, button instead of the form
    fin = block(s, '<section class="sec bg-dk fsec">', 'section')
    new = one(fin, '<div class="fs-g">', '<div class="fs-g nbf-fin">')
    new = new.replace(block(new, '<form class="lf" id="ponuda"', 'form'), '')
    new = one(new, '<p>Ostavi kontakt, a mi ti za 24h šaljemo ponudu',
              '<p>Zakaži kratak razgovor, a mi ti za 24h šaljemo ponudu')
    checks = re.findall(r'\s*<p class="chk">.*?</p>', new)
    assert len(checks) == 3
    for c in checks:
        new = new.replace(c, '', 1)
    chks = '<div class="nbf-chks">' + ''.join(c.strip() for c in checks) + '</div>'
    button = f'<a class="btn lime" data-cta href="{CTA}">Zakaži razgovor {ARROW}</a>'
    new = one(new, '\n      <p class="fs-ph">', f'\n      {chks}\n      {button}\n      <p class="fs-ph">')
    return s.replace(fin, new)


def main():
    for name, fn in [('embed-01.html', build_css), ('embed-02.html', build_markup)]:
        text = fn((src / name).read_text())
        assert len(text) < 50000, (name, len(text))   # Webflow Embed limit
        (out / name).write_text(text)
        print(f'firme/{name} {len(text):,} characters')


if __name__ == '__main__':
    main()
