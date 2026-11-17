"""Build the family page (porodice/) for Webflow.

    python3 tools/build_porodice.py

Content follows the Figma mobile design ("Nutribox za porodice i parove – Mobile 390",
file jEzLRaAeM3oA3NhAEYPBDu, node 143:369): what is not on the mobile design is not on
the page at any width. Sections that also exist on the landing page reuse the landing's
own markup (taken from webflow/landing/embed-sr-*.html) and are styled by the pinned
landing.css, so they look exactly like the landing; the rest is built in the same style.

Output: porodice/embed-NN.html (Webflow Embeds, each under 48,000 characters) and
porodice/index.html (preview). The texts are in the constants below.
"""
import html
import json
import re
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
out = repo / 'porodice'
LIMIT = 48000
LANDING_CSS = 'https://cdn.jsdelivr.net/gh/floumate-dev/nutribox@85508c1caae585168981cfb3f672861edf30fc65/webflow/landing/landing.css'
ASSETS = 'https://cdn.jsdelivr.net/gh/floumate-dev/nutribox@117e74093543da6c7d40e235bee5ada4216f4da1/assets/'
CTA = 'https://app.iclosed.io/e/nutribox/besplatan-poziv-za-porodice'
CTA_LABEL = 'Izaberite plan za&nbsp;vas'
G = '#5e8f3d'      # green accent in headings
LIME = '#accb7d'

# ---------------------------------------------------------------- texts (Figma mobile)
TOPBAR = 'Za parove i porodice · <span style="color: #accb7d">−10% za&nbsp;dvoje</span>'
HERO = {
    'pill': '👫 Za parove i porodice · <span class="nbp-desk">Beograd i Novi Sad</span><span class="nbp-mob">BG i NS</span>',
    'h1': 'Niko u kući više ne kuva. <span style="color: #5e8f3d">Svako jede po svom&nbsp;planu.</span>',
    'p': 'Stres oko gužve u kuhinji, kuvanja, pranja sudova i nabavke zamenjuješ zdravim obrocima koje spremaju vrhunski kuvari, a pritom vratiš preko 15 sati vremena sa&nbsp;porodicom.',
    'photo': '[Foto: par ujutru otvara Nutribox kutije]',
    'anchor': 'na oba paketa kad poručujete u&nbsp;dvoje',
    'micro': 'Prijava 2 minuta · Prva dostava već&nbsp;prekosutra',
    'checks': ['Svako svoj nalog i plan u&nbsp;aplikaciji', 'Pauza za jednog ili celo&nbsp;domaćinstvo', 'Jedan plaća, poeni se skupljaju&nbsp;zajedno'],
    'rating': '4,7 Google (144) · 2.500+&nbsp;korisnika',
}
PAINS_H2 = f'Prepoznajete li <span style="color: {G}">ovo&nbsp;veče?</span>'
PAINS = [
    ('<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>', '18h, oboje umorni, a „šta ćemo za večeru?“ vam padne&nbsp;preteško.'),
    ('<path d="M4 11h16v3.5a5.5 5.5 0 0 1-5.5 5.5h-5A5.5 5.5 0 0 1 4 14.5V11z"></path><path d="M2 11h2M20 11h2"></path><path d="M9.5 7.5c0-1.2 1-1.6 1-2.8M13.5 7.5c0-1.2 1-1.6 1-2.8"></path>', 'Jedno je na dijeti, drugo trenira, a šporet je&nbsp;jedan.'),
    ('<path d="M3 4h2.5l2.3 11h10.4l2.1-8H6.4"></path><circle cx="9.5" cy="19.5" r="1.4"></circle><circle cx="16.5" cy="19.5" r="1.4"></circle>', 'Subota u supermarketu, nedelja u kuhinji, sreda opet&nbsp;Wolt.'),
    ('<rect x="3" y="6" width="18" height="13" rx="2.5"></rect><path d="M3 10h18"></path><path d="M15.5 14.5h2.5"></path>', 'Wolt za dvoje: 6.000–7.000 RSD za jedan&nbsp;obrok.'),
]
PAINS_BRIDGE = 'U svakoj kući postoji „onaj koji kuva“. I taj neko je&nbsp;umoran.'
HOUSE_H2 = f'Jedna kuća. <span style="color: {G}">Različiti ciljevi. Jedna&nbsp;dostava.</span>'
HOUSE = [('ONA', 'NutriSlim', 'Ž 1.300 kcal · bez glutena', 'Želi da skine par kilograma'),
         ('ON', 'NutriPump', 'M 2.600 kcal · Balance', 'Trenira 4 puta nedeljno')]
HOUSE_RESULT = '📦 1 dostava do 9:30 · 8 obroka · 0&nbsp;kuvanja'
STEPS_H2 = f'Kako funkcioniše <span style="color: {G}">za dvoje i&nbsp;više?</span>'
STEPS = [('Svako izabere svoj&nbsp;plan', 'Svako ima svoj nalog u&nbsp;aplikaciji.'),
         ('Jedan plaća za&nbsp;sve', '10% popusta za par, zajednički&nbsp;poeni.'),
         ('Jedna jutarnja&nbsp;dostava', 'Sve stiže zajedno do&nbsp;9:30.'),
         ('Pauza po&nbsp;meri', 'Za jednog člana ili celo&nbsp;domaćinstvo.')]
PRICES_H2 = f'U dvoje je <span style="color: {G}">10%&nbsp;povoljnije.</span>'
PRICES_LEAD = 'Na oba paketa, ista adresa, nedeljni i mesečni paketi. Paketi mogu biti&nbsp;različiti.'
# 28-day plan 78,400 RSD and 7-day plan 22,400 RSD (landing prices), 10% off for two
PRICES = [dict(featured=True, badge='NAJISPLATIVIJE', title='Mesečno za dvoje', old='156.800 RSD', new='141.120 RSD', per='2.520 RSD po osobi dnevno', save='Uštedite 15.680 RSD'),
          dict(featured=False, badge='', title='Nedeljno za dvoje', old='44.800 RSD', new='40.320 RSD', per='2.880 RSD po osobi dnevno', save='Uštedite 4.480 RSD')]
PRICES_VAL = 'Jedan Wolt obrok za dvoje: 6.000–7.000 RSD. Ceo dan Nutriboxa za dvoje: 5.040&nbsp;RSD.'
VIDEOS_H2 = f'Kuće u kojima se više ne pita <span style="color: {G}">„šta ćemo&nbsp;danas“.</span>'
OBJS_H2 = f'Ono što vas&nbsp;verovatno <span style="color: {G}">još koči.</span>'
OBJS = [('Različiti&nbsp;ukusi?', 'Svako svoj paket, tip ishrane i do 2&nbsp;isključenja.'),
        ('Jedno često&nbsp;putuje?', 'Pauzirate samo njegove dane, drugi&nbsp;nastavlja.'),
        ('Nije li to&nbsp;luksuz?', '15+ sati nedeljno koje vraćate porodici. A dan za dvoje je jeftiniji od jednog Wolt obroka za&nbsp;dvoje.'),
        ('Šta ako nam se ne&nbsp;dopadne?', 'Garancija na mesečni paket, ili krenite sa&nbsp;nedeljnim.')]
GUAR = ('Garancija za mesečni&nbsp;paket', 'Ako vam u prvih 7 dana ne odgovara, vraćamo novac za preostale 3&nbsp;nedelje.')
FAQ_H2 = f'Česta pitanja <span style="color: {G}">parova i&nbsp;porodica.</span>'
FAQ = [
    ('Kako dobijamo popust od&nbsp;10%?', 'Dvoje poručuje nedeljni ili mesečni paket na istu adresu. Paketi ne moraju biti&nbsp;isti.'),
    ('Da li moramo da imamo isti&nbsp;paket?', 'Ne. Svako bira svoj paket, tip ishrane i do dva isključenja. Sve stiže zajedno u jednoj jutarnjoj&nbsp;dostavi.'),
    ('Može li samo jedno da&nbsp;pauzira?', 'Da. Pauzirate samo njegove dane u aplikaciji, a drugi nastavlja normalno, bez&nbsp;penala.'),
    ('Ko plaća i kako se skupljaju&nbsp;poeni?', 'Jedan plaća za sve, a poeni se skupljaju&nbsp;zajedno.'),
    ('Kada stiže prva&nbsp;dostava?', 'Prva dostava stiže najranije prekosutra od dana porudžbine. Svi obroci za taj dan stižu u jednoj isporuci na vašu&nbsp;adresu.'),
    ('Da li postoji dečiji&nbsp;meni?', '[Odgovor - dopuniti]'),
    ('Dostavljate li i u Novi&nbsp;Sad?', 'Da, dostavljamo u Beogradu i Novom Sadu. U Beogradu zasad ne dostavljamo u Železnik, Borču, Kaluđericu i prigradske opštine. Za proveru vaše adrese pozovite 0800&nbsp;001&nbsp;007.'),
]
FIN_H2 = f'Od prekosutra <span style="display: block; color: {LIME}">niko u kući ne&nbsp;kuva.</span>'
FIN_RECAP = ['−10% za&nbsp;dvoje', 'svako svoj&nbsp;plan', 'dostava do&nbsp;9:30', 'pauza po&nbsp;članu', 'Beograd i Novi&nbsp;Sad']
FIN_NOTE = '📞 <a href="tel:0800001007" style="color: #ffffff; font-weight: 600; white-space: nowrap">0800 001 007</a> · WhatsApp'
STICKY = ('−10% za dvoje', 'od 2.520 RSD po osobi/dan', 'Izaberite plan')

# ---------------------------------------------------------------- landing markup
land = ''.join((repo / f'webflow/landing/embed-sr-0{i}.html').read_text() for i in (1, 2, 3))
secs = [m.group(0) for m in re.finditer(r'<(section|footer|header)\b[^>]*>.*?</\1>', land, re.S)]
SEC = {'header': 0, 'pains': 2, 'menu': 4, 'videos': 8, 'steps': 9, 'guar': 11, 'objs': 12, 'faq': 14, 'fin': 15, 'footer': 16}
ROOT = re.search(r'<div class="nbx-root"[^>]*>', land).group(0)


def one(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f'build_porodice: landing markup changed, not found once: {old[:70]!r}')
    return text.replace(old, new)


def sub_h2(sec, inner):
    return re.sub(r'(<h2\b[^>]*>).*?(</h2>)', lambda m: m.group(1) + inner + m.group(2), sec, count=1, flags=re.S)


def cta(sec, label=CTA_LABEL):
    sec = sec.replace('<a class="nbx-btn" href="https://www.nutribox.rs/order-form"', f'<a class="nbx-btn" data-cta href="{CTA}"')
    return re.sub(r'(<a class="nbx-btn" data-cta [^>]*>)[^<]*', lambda m: m.group(1) + label + '\n', sec)


def h2_style():
    return re.search(r'<h2 style="([^"]*)"', secs[SEC['pains']]).group(1)


H2 = h2_style()
BTN_DARK = 'display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 58px; box-sizing: border-box; padding: 18px 30px; border-radius: 14px; background: #123c32; color: #ffffff; font-size: 18px; font-weight: 700; text-decoration: none'
ARROW = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>'
STARS = '<span aria-hidden="true" style="color: #e8a33c; letter-spacing: 1px">★★★★★</span>'


def section(bg, inner, extra=''):
    return (f'<section style="background: {bg}; padding: clamp(56px, 8vw, 96px) 20px{extra}">\n'
            f'<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 40px">\n{inner}\n</div>\n</section>')


def h2(inner, color='#123c32'):
    return f'<h2 style="{H2.replace("color: #123c32", "color: " + color)}">{inner}</h2>'


def lead(text, color='#3d4a41'):
    return f'<p style="margin: -20px 0 0; max-width: 720px; text-align: center; font-size: 18px; line-height: 1.5; color: {color}; text-wrap: balance">{text}</p>'


def btn(label=CTA_LABEL):
    return f'<a class="nbx-btn" data-cta href="{CTA}" style="{BTN_DARK}">{label}\n{ARROW}\n</a>'


# ---------------------------------------------------------------- sections
def topbar_header():
    i = land.index('<header')
    bar = land[land.rfind('<div style="position: sticky', 0, i):i].strip()
    bar = re.sub(r'<span>Dostava u .*?</span>\n', f'<span>{TOPBAR}</span>\n', bar, count=1, flags=re.S)
    hdr = secs[SEC['header']]
    hdr = one(hdr, '<div class="nbx-lang-hdr" data-dc-keep="lang"></div>\n', '')
    hdr = one(hdr, 'style="display: flex; align-items: center; min-height: 44px">', 'style="display: flex; align-items: center; gap: 10px; min-height: 44px">')
    hdr = one(hdr, 'style="height: 34px; width: auto; display: block">\n</a>',
              'style="height: 34px; width: auto; display: block"><span class="nbp-tag" style="background: #123c32; color: #accb7d; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; padding: 5px 10px; border-radius: 8px; line-height: 1.26; white-space: nowrap">ZA PORODICE</span>\n</a>')
    # phone: the number on wide screens, "Pozovi" on phones (no plan button in the header)
    hdr = one(hdr, '<a class="nbx-hide-sm" href="tel:0800001007"', '<a href="tel:0800001007"')
    hdr = one(hdr, '0800 001&nbsp;007\n</a>', '<span class="nbp-desk">0800 001&nbsp;007</span><span class="nbp-mob">Pozovi</span>\n</a>')
    hdr = re.sub(r'\n<a class="nbx-btn" href="https://www.nutribox.rs/order-form"[^>]*>.*?</a>', '', hdr, count=1, flags=re.S)
    return bar + '\n' + hdr


def hero():
    checks = ''.join(f'<li style="display: flex; align-items: center; gap: 10px; font-size: 15px; line-height: 1.35; color: #3d4a41"><span style="width: 20px; height: 20px; flex: none; border-radius: 99px; background: #accb7d; display: flex; align-items: center; justify-content: center"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#123c32" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg></span>{c}</li>' for c in HERO['checks'])
    return f'''<section style="position: relative; overflow: hidden; padding: clamp(32px, 5vw, 64px) 20px clamp(48px, 6vw, 80px); background: #ffffff">
<div class="nbp-hero" style="max-width: 1200px; margin: 0 auto">
<div class="nbp-hero-copy">
<span class="nbp-o1" style="align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 99px; background: #f0f6ec; font-size: 15px; font-weight: 600; color: #123c32">{HERO['pill']}</span>
<h1 class="nbp-o2" style="margin: 0; font-size: clamp(34px, 4.6vw, 56px); line-height: 1.08; letter-spacing: -0.03em; font-weight: 700; color: #123c32">{HERO['h1']}</h1>
<p class="nbp-o3" style="margin: 0; max-width: 600px; font-size: clamp(16px, 1.4vw, 19px); line-height: 1.55; color: #3d4a41">{HERO['p']}</p>
<div class="nbp-o5" style="align-self: flex-start; display: flex; align-items: center; gap: 14px; padding: 12px 16px; border-radius: 16px; background: #f6f8f3; font-size: 15px; line-height: 1.35; font-weight: 500; color: #3d4a41"><b style="flex: none; padding: 6px 10px; border-radius: 10px; background: #123c32; color: #accb7d; font-size: 22px; font-weight: 800; line-height: 1.2">−10%</b><span>{HERO['anchor']}</span></div>
<div class="nbp-o6 nbp-ctarow" style="display: flex; flex-direction: column; align-items: flex-start; gap: 10px">{btn()}
<span style="font-size: 14px; line-height: 1.4; color: #3d4a41">{HERO['micro']}</span></div>
<ul class="nbp-o7" style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px">{checks}</ul>
<p class="nbp-o8" style="margin: 0; font-size: 14px; font-weight: 600; color: #123c32">{STARS} {HERO['rating']}</p>
</div>
<div class="nbp-o4 nbp-photo" style="border-radius: 28px; background: #bbe2ab; padding: 20px; display: flex; align-items: flex-end"><div style="width: 100%; background: #ffffff; border-radius: 14px; padding: 12px 14px; font-size: 13px; font-weight: 500; color: #123c32">{HERO['photo']}</div></div>
</div>
</section>'''


def pains():
    s = sub_h2(secs[SEC['pains']], PAINS_H2)
    cards = list(re.finditer(r'(<svg width="26" height="26"[^>]*>).*?(</svg></span>\n<span style="font-size: 18px; line-height: 1.4; font-weight: 500; color: #123c32">).*?(</span>)', s, re.S))
    assert len(cards) == 4
    for m, (icon, text) in reversed(list(zip(cards, PAINS))):
        s = s[:m.start()] + m.group(1) + icon + m.group(2) + text + m.group(3) + s[m.end():]
    s = re.sub(r'(<p style="margin: 0; max-width: 960px;[^>]*>).*?(</p>)', lambda m: m.group(1) + PAINS_BRIDGE + m.group(2), s, count=1, flags=re.S)
    return re.sub(r'\n<a href="#poredjenje".*?</a>', '', s, count=1, flags=re.S)


def house():
    cards = ''.join(f'''<div style="flex: 1 1 300px; min-width: 0; display: flex; align-items: center; gap: 12px">
<span style="flex: none; width: 54px; box-sizing: border-box; padding: 6px 0; text-align: center; border-radius: 99px; background: #123c32; color: #accb7d; font-size: 12px; font-weight: 800; letter-spacing: 0.08em">{tag}</span>
<div style="flex: 1 1 auto; min-width: 0; background: #ffffff; border: 1.5px solid #e3e8e2; border-radius: 18px; padding: 16px 18px; display: flex; flex-direction: column; gap: 4px">
<b style="font-size: 20px; font-weight: 700; color: #123c32">{pkg}</b><span style="font-size: 14px; font-weight: 600; color: #4d7a31">{kcal}</span><span style="font-size: 14px; color: #3d4a41">{who}</span>
</div></div>''' for tag, pkg, kcal, who in HOUSE)
    inner = (h2(HOUSE_H2) + '\n'
             + f'<div style="width: 100%; max-width: 900px; display: flex; flex-direction: column; gap: 14px">\n<div style="display: flex; flex-wrap: wrap; gap: 14px">{cards}</div>\n'
             + f'<div style="border-radius: 16px; background: #123c32; color: #ffffff; padding: 16px 20px; text-align: center; font-size: 16px; font-weight: 700">{HOUSE_RESULT}</div>\n</div>')
    return section('#ffffff', inner)


def steps():
    s = sub_h2(secs[SEC['steps']], STEPS_H2)
    lis = list(re.finditer(r'(<h3 [^>]*>).*?(</h3>\n<p [^>]*>).*?(</p>)', s, re.S))
    assert len(lis) == 4
    for m, (h, p) in reversed(list(zip(lis, STEPS))):
        s = s[:m.start()] + m.group(1) + h + m.group(2) + p + m.group(3) + s[m.end():]
    return re.sub(r'\n<a class="nbx-btn" href="https://www.nutribox.rs/order-form".*?</a>', '', s, count=1, flags=re.S)


def prices():
    def card(p):
        bg, fg, sub = ('#123c32', '#ffffff', '#accb7d') if p['featured'] else ('#f6f8f3', '#123c32', '#4d7a31')
        badge = f'<span style="align-self: flex-start; padding: 4px 10px; border-radius: 8px; background: #accb7d; color: #123c32; font-size: 11px; font-weight: 700; letter-spacing: 0.06em">{p["badge"]}</span>' if p['badge'] else ''
        save_bg = '#30563f' if p['featured'] else '#ffffff'
        return f'''<div style="flex: 1 1 320px; min-width: 0; border-radius: 24px; background: {bg}; color: {fg}; padding: clamp(22px, 3vw, 32px); display: flex; flex-direction: column; gap: 8px">
{badge}<b style="font-size: 20px; font-weight: 700; color: {fg}">{p["title"]}</b>
<s style="font-size: 14px; color: {'#8fae82' if p['featured'] else '#9aa39d'}">{p["old"]}</s>
<span style="font-size: clamp(32px, 3.4vw, 42px); font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; color: {fg}">{p["new"]}</span>
<span style="font-size: 15px; font-weight: 600; color: {sub}">{p["per"]}</span>
<span style="align-self: flex-start; padding: 5px 10px; border-radius: 8px; background: {save_bg}; color: {sub}; font-size: 13px; font-weight: 700">{p["save"]}</span>
</div>'''
    inner = (h2(PRICES_H2) + '\n' + lead(PRICES_LEAD) + '\n'
             + f'<div style="width: 100%; max-width: 1000px; display: flex; flex-wrap: wrap; gap: 16px">{"".join(card(p) for p in PRICES)}</div>\n'
             + f'<p style="margin: 0; max-width: 640px; text-align: center; font-size: 16px; line-height: 1.5; font-weight: 600; color: #4d7a31; text-wrap: balance">{PRICES_VAL}</p>\n' + btn())
    return section('#ffffff', inner)


def menu_data():
    """The landing's menu data: {diet: [[name, menu, meal, kcal, P, UH, M], ...]} from design/Main.dc.html."""
    src = (repo / 'design' / 'Main.dc.html').read_text()
    body = src[src.index('jelovnik() {'):]
    body = body[body.index('return {') + len('return '):body.index('};') + 1]
    return json.loads(body)


def menu():
    """The landing's menu slider section; the filters re-render the cards with the same markup (JS below)."""
    s = secs[SEC['menu']]
    s = one(s, '<section ', '<section data-nbp-menu ')
    for diet, label in [('sve', 'Sve'), ('0', 'Balance'), ('1', 'Fish'), ('2', 'Vegetarijanski'), ('3', 'Vegan'), ('posno', 'Posno'), ('4', 'Bez glutena')]:
        s = re.sub(r'(<button type="button" class="nbx-pick")( aria-pressed="(?:true|false)"[^>]*>' + re.escape(label) + '</button>)',
                   lambda m: m.group(1) + f' data-diet="{diet}"' + m.group(2), s, count=1)
    assert s.count('data-diet=') == 7
    s = one(s, '<div class="nbx-slider" style="width: 100%; display: flex; gap: 20px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 6px 2px 12px; box-sizing: border-box">',
            '<div class="nbx-slider nbp-mlist" style="width: 100%; display: flex; gap: 20px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 6px 2px 12px; box-sizing: border-box">')
    data = json.dumps(menu_data(), ensure_ascii=False).replace('</', '<\\/')
    s = s.replace('\n</section>', f'\n<script type="application/json" class="nbp-mdata">{data}</script>\n</section>', 1)
    return cta(s, 'Izaberite plan za&nbsp;vas')


def videos():
    """The landing's testimonial section (videos, quote, message wall), with the family heading."""
    return sub_h2(secs[SEC['videos']], VIDEOS_H2)


def objs():
    s = sub_h2(secs[SEC['objs']], OBJS_H2)
    items = list(re.finditer(r'<div style="background: #ffffff; border-radius: 22px; padding: 28px; display: flex; gap: 16px">.*?</p></div>\n</div>\n', s, re.S))
    tmpl = re.sub(r'(<h3 [^>]*>).*?(</h3><p [^>]*>).*?(</p>)', r'\1{H}\2{P}\3', items[0].group(0), count=1, flags=re.S)
    return s[:items[0].start()] + ''.join(tmpl.replace('{H}', h).replace('{P}', p) for h, p in OBJS) + s[items[-1].end():]


def guar():
    s = secs[SEC['guar']]
    s = one(s, '<section style="background: #ffffff; padding: 0 20px clamp(64px, 8vw, 96px)">', '<section style="background: #ffffff; padding: clamp(56px, 8vw, 96px) 20px">')
    s = sub_h2(s, GUAR[0])
    return re.sub(r'(<p style="margin: 0; font-size: 18px;[^>]*>).*?(</p>)', lambda m: m.group(1) + GUAR[1] + m.group(2), s, count=1, flags=re.S)


def faq():
    src = secs[SEC['faq']]
    head = sub_h2(src[:src.index('<div class="nbx-faq-item')], FAQ_H2)
    items = re.findall(r'<div class="nbx-faq-item[^"]*" style="[^"]*">.*?\n</div>\n</div>\n</div>\n', src, re.S)
    tail = src[src.rindex('</div>\n</div>\n</div>\n') + len('</div>\n</div>\n</div>\n'):]

    def item(n, q, a):
        t = items[0] if n == 1 else items[1]
        t = re.sub(r'(<span class="nbx-faq-t" style="width: 26px;[^>]*>)\d+(</span>)', lambda m: m.group(1) + f'{n:02d}' + m.group(2), t, count=1)
        t = re.sub(r'(<span class="nbx-faq-t" style="flex: 1 1 auto;[^>]*>).*?(</span>)', lambda m: m.group(1) + q + m.group(2), t, count=1, flags=re.S)
        t = re.sub(r'(<p class="nbx-faq-a"[^>]*>).*?(</p>)', lambda m: m.group(1) + a + m.group(2), t, count=1, flags=re.S)
        return re.sub(r'<div class="nbx-faq-a"[^>]*>\n<a .*?</a>\n</div>\n', '', t, flags=re.S)
    return head + ''.join(item(n, q, a) for n, (q, a) in enumerate(FAQ, 1)) + tail


def fin():
    s = sub_h2(secs[SEC['fin']], FIN_H2)
    chips = list(re.finditer(r'<span class="nbx-recap-i"[^>]*><svg .*?</svg>.*?</span>\n', s, re.S))
    chip = re.sub(r'(</svg>).*?(</span>\n)$', r'\1{T}\2', chips[0].group(0), flags=re.S)
    s = s[:chips[0].start()] + ''.join(chip.replace('{T}', t) for t in FIN_RECAP) + s[chips[-1].end():]
    s = cta(s)
    return re.sub(r'(<p style="margin: 0; font-size: 15px; line-height: 1.5; color: #accb7d">).*?(</p>)', lambda m: m.group(1) + FIN_NOTE + m.group(2), s, count=1, flags=re.S)


def sticky():
    return (f'<div class="nbp-stk" aria-hidden="true"><div style="flex: 1 1 auto; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
            f'<b style="font-size: 15px; font-weight: 700; color: #123c32; white-space: nowrap">{STICKY[0]}</b>'
            f'<small style="font-size: 12px; color: #3d4a41; white-space: nowrap">{STICKY[1]}</small></div>'
            f'<a class="nbx-btn" data-cta href="{CTA}" tabindex="-1" style="flex: none; display: inline-flex; align-items: center; min-height: 48px; box-sizing: border-box; padding: 12px 18px; border-radius: 12px; background: #123c32; color: #ffffff; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap">{STICKY[2]}</a></div>')


CSS = '''<style>
/* Nutribox za porodice. Built by tools/build_porodice.py; shared sections are styled by landing.css. */
.nbp-mob{display:none}
.nbp-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:56px;align-items:center}
.nbp-hero-copy{display:flex;flex-direction:column;gap:22px}
.nbp-photo{min-height:460px}
.nbp-stk{position:fixed;left:0;right:0;bottom:0;z-index:60;background:#fff;box-shadow:0 -4px 16px rgba(0,0,0,.12);padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));display:none;align-items:center;gap:12px;transform:translateY(110%);transition:transform .3s ease;font-family:'Outfit',ui-sans-serif,system-ui,sans-serif}
.nbp-stk.show{transform:none}
.nbp-drag{cursor:grab}.nbp-drag.dragging{cursor:grabbing;scroll-snap-type:none;user-select:none}
@media (max-width:899px){
.nbp-hero{display:flex;flex-direction:column;align-items:stretch;gap:20px}
.nbp-hero-copy{display:contents}
.nbp-o1{order:1}.nbp-o2{order:2}.nbp-o3{order:3}.nbp-o4{order:4}.nbp-o5{order:5}.nbp-o6{order:6}.nbp-o7{order:7}.nbp-o8{order:8}
.nbp-photo{min-height:230px;border-radius:20px!important}
.nbp-o5{align-self:stretch!important}
.nbp-ctarow{align-items:stretch!important;text-align:center}
}
@media (max-width:640px){
.nbp-desk{display:none}.nbp-mob{display:inline}
.nbp-stk{display:flex}
header .nbp-tag{font-size:9px!important;padding:4px 7px!important}
.nbp-ctarow .nbx-btn{width:100%}
}
@media (prefers-reduced-motion:reduce){.nbp-stk{transition:none}}
</style>'''

JS = r'''<script>(function () {
  var $$ = function (s) { return document.querySelectorAll(s); };
  // CTA links keep the page's query string (UTM parameters) for the call booking
  var qs = window.location.search.slice(1);
  if (qs) $$("a[data-cta]").forEach(function (a) { var h = a.getAttribute("href"); a.setAttribute("href", h + (h.indexOf("?") > -1 ? "&" : "?") + qs); });
  // FAQ: one open item, same colours as the landing
  var ON = { box: ["#123c32", "1px solid #123c32"], num: "#accb7d", q: "#ffffff", ico: "#accb7d" };
  var OFF = { box: ["#ffffff", "1px solid #e3e8e2"], num: "#5e8f3d", q: "#123c32", ico: "#f0f6ec" };
  var set = function (item, on) {
    var c = on ? ON : OFF, t = item.querySelectorAll(".nbx-faq-t");
    item.classList.toggle("nbx-faq-open", on);
    item.style.background = c.box[0]; item.style.border = c.box[1];
    t[0].style.color = c.num; t[1].style.color = c.q;
    item.querySelector(".nbx-faq-ico").style.background = c.ico;
    item.querySelector("button").setAttribute("aria-expanded", on ? "true" : "false");
    item.querySelector(".nbx-faq-panel").setAttribute("aria-hidden", on ? "false" : "true");
  };
  $$(".nbx-faq-item > button").forEach(function (b) {
    b.addEventListener("click", function () {
      var item = b.parentElement, on = !item.classList.contains("nbx-faq-open");
      $$(".nbx-faq-item.nbx-faq-open").forEach(function (o) { set(o, false); });
      if (on) set(item, true);
    });
  });
  // menu filters: same cards as the landing (markup copied from its card template)
  var MENUS = ["Balance", "Fish", "Vegetarijanski", "Vegan", "Bez glutena"], MEALS = ["DORUČAK", "UŽINA", "RUČAK", "VEČERA"];
  var SP = { sve: 0, "0": 1, "1": 2, "2": 3, "3": 4, posno: 5, "4": 6 }, NB = "\u00a0";
  var esc = function (s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); };
  var nb = function (s) { return String(s).replace(/ (\S+)$/, NB + "$1"); };
  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); };
  var card = function (c, i, sp) {
    var sejk = c[2] === 1 && [0, 1, 1, 1.5, 0][c[1]] > 0;
    return '<article style="flex: 0 0 250px; min-width: 250px; scroll-snap-align: start; display: flex; flex-direction: column; gap: 10px">' +
      '<div style="position: relative; width: 100%; aspect-ratio: 1 / 1; border-radius: 20px; overflow: hidden; background: #e4efdc">' +
      '<div class="nbx-spr nbx-sp' + sp + '" role="img" aria-label="' + esc(c[0]) + '" style="position: absolute; inset: 0; background-position: ' + (i % 6) * 20 + "% " + Math.floor(i / 6) * 50 + '%"></div>' +
      '<span style="position: absolute; top: 12px; left: 12px; padding: 5px 10px; border-radius: 99px; background: #ffffff; font-size: 13px; font-weight: 700; color: #123c32">' + fmt(c[3]) + NB + "kcal</span>" +
      (/posn/i.test(c[0]) ? '<span style="position: absolute; top: 12px; right: 12px; padding: 5px 10px; border-radius: 99px; background: #123c32; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #accb7d">POSNO</span>' : "") +
      "</div>" +
      '<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.06em; color: #4d7a31">' + MENUS[c[1]].toUpperCase() + " · " + MEALS[c[2]] + "</span>" +
      '<h3 style="margin: -4px 0 0; font-size: 18px; line-height: 1.25; font-weight: 700; color: #123c32">' + esc(nb(c[0])) + "</h3>" +
      (sejk ? '<span style="margin-top: -4px; font-size: 13px; font-weight: 600; color: #5e8f3d">' + (c[1] === 3 ? "+ biljni proteinski" : "+ proteinski") + NB + "šejk</span>" : "") +
      '<span style="font-size: 13px; font-weight: 500; color: #4d7a31">' + c[4] + "g proteina · " + c[5] + "g UH · " + c[6] + "g" + NB + "masti</span>" +
      "</article>";
  };
  $$("[data-nbp-menu]").forEach(function (sec) {
    var J = JSON.parse(sec.querySelector(".nbp-mdata").textContent), list = sec.querySelector(".nbp-mlist");
    sec.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-diet]");
      if (!b) return;
      var d = b.getAttribute("data-diet");
      list.innerHTML = (J[d] || []).map(function (c, i) { return card(c, i, SP[d]); }).join("");
      list.scrollLeft = 0;
      sec.querySelectorAll("button[data-diet]").forEach(function (x) {
        var on = x === b;
        x.setAttribute("aria-pressed", on ? "true" : "false");
        x.style.background = on ? "#123c32" : "#ffffff"; x.style.color = on ? "#ffffff" : "#123c32";
        x.style.border = "1.5px solid " + (on ? "#123c32" : "#accb7d");
      });
    });
  });
  // message wall: "Prikaži još utisaka" shows the rest (on phones the wall scrolls sideways instead)
  $$(".nbx-wall-more").forEach(function (b) {
    b.addEventListener("click", function () {
      var wall = b.parentElement.querySelector(".nbx-wall");
      if (wall) wall.querySelectorAll(".nbx-w-hide").forEach(function (img) { img.classList.remove("nbx-w-hide"); });
      b.hidden = true;
    });
  });
  // sliders can be dragged with the mouse
  $$(".nbp-drag").forEach(function (el) {
    var down = false, x0 = 0, s0 = 0;
    el.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0 || e.target.closest("iframe,a,button")) return;
      down = true; x0 = e.clientX; s0 = el.scrollLeft; el.classList.add("dragging"); el.setPointerCapture(e.pointerId); e.preventDefault();
    });
    el.addEventListener("pointermove", function (e) { if (down) el.scrollLeft = s0 - (e.clientX - x0); });
    var up = function () { down = false; el.classList.remove("dragging"); };
    el.addEventListener("pointerup", up); el.addEventListener("pointercancel", up);
  });
  // sticky bar on phones: after the hero, hidden over the footer
  var stk = document.querySelector(".nbp-stk"), hero = document.querySelector(".nbp-hero"), foot = document.querySelector("footer");
  if (stk) {
    var tick = false;
    var upd = function () {
      tick = false;
      var past = hero ? hero.getBoundingClientRect().bottom < 0 : window.scrollY > 700;
      var atFoot = foot ? foot.getBoundingClientRect().top < window.innerHeight : false;
      var show = past && !atFoot;
      stk.classList.toggle("show", show); stk.setAttribute("aria-hidden", show ? "false" : "true");
      stk.querySelector("a").setAttribute("tabindex", show ? "0" : "-1");
    };
    window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });
    window.addEventListener("resize", upd); upd();
  }
})();
</script>'''


def part(*blocks):
    return '<div class="nbx-part">' + ROOT + '\n' + '\n'.join(blocks) + '\n</div></div>\n'


def build():
    head = (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&amp;display=swap">'
            f'<link rel="stylesheet" href="{LANDING_CSS}">\n<style>.nb-jezik-red{{display:none!important}}</style>\n{CSS}\n')
    blocks = [head + part(topbar_header(), hero()), part(pains()), part(house()), part(steps()), part(prices()),
              part(menu()), part(videos()), part(objs(), guar()), part(faq()), part(fin(), secs[SEC['footer']]),
              sticky() + '\n' + JS]
    groups, cur = [], ''
    for b in blocks:
        if cur and len(cur) + len(b) > LIMIT:
            groups.append(cur)
            cur = ''
        cur += b
    groups.append(cur)
    for old in out.glob('embed-*.html'):
        old.unlink()
    for n, g in enumerate(groups, 1):
        if len(g) > LIMIT:
            raise SystemExit(f'embed {n} is {len(g)} characters')
        (out / f'embed-{n:02d}.html').write_text(g)
        print(f'porodice/embed-{n:02d}.html {len(g):,} characters')


if __name__ == '__main__':
    build()
