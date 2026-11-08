"""Writes project/Jelovnik.dc.html: the full weekly menu page.

argv: <jelovnik folder> <Main.dc.html> <out Jelovnik.dc.html>
"""
import datetime
import json
import os
import re
import sys

jdir, main_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(os.path.join(jdir, "jelovnik.json"), encoding="utf-8"))
ob = d["obroci"]
MENUS = ["Balance", "Fish", "Vegetarijanski", "Vegan", "Bez glutena"]
MEALS = ["Doručak", "Užina", "Ručak", "Večera"]
SIZES = ["XS", "S", "M", "L", "XL"]
WD_SHORT = ["Pon", "Uto", "Sre", "Čet", "Pet", "Sub", "Ned"]
WD_LONG = ["Ponedeljak", "Utorak", "Sreda", "Četvrtak", "Petak", "Subota", "Nedelja"]
MONTHS = ["januar", "februar", "mart", "april", "maj", "jun", "jul", "avgust", "septembar", "oktobar", "novembar", "decembar"]
dates = sorted(set(o["datum"] for o in ob))
assert len(dates) == 21

SHEETS = ["9bfd7de5b881a454c2b131ae78690cdb", "a492183b2f9351927719b61662517a44", "a82ec9ff0b8748f8bed0bb31e876da7f",
          "d22c9b9bdbb0f27ab324fa5ba9e4274d", "666d33ff00ea8aedf028b27382dcd344", "86a1892f0d404c8e88b581667d6d4846",
          "832c9b607fccb2308f8cb0bd95fb47dd", "64cc2fa15a96f07b8f7d7be80c97fe2f", "2734c42493f0d9d0298c522bba681836",
          "862388e8ea635615ba806695de7007b4", "ad4802db6ef64d93944957edaf55ac6f", "c256211f25a17362dd0037b04db8726a",
          "5959b1fe3e4698ee4011aefdbb9b277d", "4b98bf81c79d7d13fca603c77ee7a1a5", "c812ac9c10786518c107a2c1707a677b"]
POSNO_SHEET = "be0e8408087d67f0aff97b2423547726"


def mac(o):
    r = []
    for s in SIZES:
        if s in o["makroi"]:
            m = o["makroi"][s]
            r += [m["kcal"], m["p"], m["uh"], m["m"]]
    return r


grid = [[[None] * 4 for _ in range(21)] for _ in range(5)]
for o in ob:
    grid[MENUS.index(o["meni"])][dates.index(o["datum"])][MEALS.index(o["obrok"])] = [o["jelo"], mac(o)]

days = []
for ds in dates:
    dt = datetime.date.fromisoformat(ds)
    days.append([WD_SHORT[dt.weekday()], "%d.%d." % (dt.day, dt.month), "%s, %d. %s" % (WD_LONG[dt.weekday()], dt.day, MONTHS[dt.month - 1])])

# posno: same order as the posno sheet used on the sales page
s = open(main_path, encoding="utf-8").read()
a = s.index('"posno": [')
b = s.index("]\n      ]", a)
prow = [json.loads(x) for x in re.findall(r"^\s+(\[.*\])", s[a:b + 2], re.M)]
assert len(prow) == 18
posno = []
for name, mi, ml, *_ in prow:
    o = next(o for o in ob if o["jelo"] == name and o["meni"] == MENUS[mi] and o["obrok"] == MEALS[ml])
    posno.append([name, mi, ml, mac(o)])


def jd(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))


data = "  jelovnik() {\n    // Nutribox jelovnik 9.11. do 29.11.2026: m[meni][dan][obrok] = [jelo, kcal/P/UH/M za XS, S, M, L, XL]\n    return {\n"
data += "      days: " + jd(days) + ",\n"
data += "      m: [\n" + ",\n".join(
    "        [\n" + ",\n".join("          " + jd(grid[mi][dy]) for dy in range(21)) + "\n        ]" for mi in range(5)) + "\n      ],\n"
data += "      posno: [\n" + ",\n".join("        " + jd(p) for p in posno) + "\n      ]\n"
data += "    };\n  }\n"

sheet_css = "".join(".jl-s%d{background-image:url(/_blob/%s)}\n" % (i, x) for i, x in enumerate(SHEETS))

ARROW = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>'
BACK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5"></path><path d="M11 6l-6 6 6 6"></path></svg>'

card = r"""<article class="jl-card">
<div class="jl-img {{ c.cls }}" role="img" aria-label="{{ c.alt }}" style="background-position: {{ c.pos }}">
<sc-if value="{{ c.posno }}" hint-placeholder-val="{{ false }}"><span style="position: absolute; left: 10px; bottom: 10px; padding: 4px 9px; border-radius: 99px; background: #123c32; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #accb7d">POSNO</span></sc-if>
</div>
<div style="display: flex; flex-direction: column; gap: 6px; min-width: 0">
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.08em; color: #4d7a31">{{ c.tag }}</span>
<h3 class="jl-name" style="margin: 0; font-size: 17px; line-height: 1.3; font-weight: 700; color: #123c32; text-wrap: pretty">{{ c.name }}</h3>
<span style="font-size: 15px; font-weight: 700; color: #123c32">{{ c.kcal }}</span>
<span style="font-size: 13px; line-height: 1.4; font-weight: 500; color: #4d7a31">{{ c.macros }}</span>
</div>
</article>"""

html = r"""<!doctype html>
<html lang="sr">
<head>
<meta charset="utf-8">
<title>Nutribox jelovnik</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&amp;display=swap">
<style>
body{margin:0}
.jl-pick{transition:box-shadow .15s ease, border-color .15s ease}
.jl-pick:hover{box-shadow:0 0 0 3px #dfeccf}
.jl-pick:focus-visible,.jl-back:focus-visible{outline:3px solid #5e8f3d;outline-offset:2px}
.jl-back:hover{color:#123c32 !important}
.jl-row{display:grid;grid-template-columns:132px minmax(0,1fr);align-items:center;gap:12px 20px}
.jl-opts{display:flex;flex-wrap:wrap;gap:8px}
.jl-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px}
.jl-card{display:flex;flex-direction:column;gap:14px;min-width:0}
.jl-img{position:relative;width:100%;aspect-ratio:1/1;border-radius:20px;overflow:hidden;background-color:#e4efdc;background-repeat:no-repeat}
.jl-wk{background-size:400% 700%}
.jl-po{background-size:600% 300%;background-image:url(/_blob/""" + POSNO_SHEET + r""")}
""" + sheet_css + r"""@media (max-width:960px){.jl-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){
.jl-row{grid-template-columns:1fr;gap:10px}
.jl-h1b{display:block}
.jl-grid{grid-template-columns:1fr;gap:14px}
.jl-card{flex-direction:row;align-items:center;gap:14px}
.jl-img{width:112px;flex:none;border-radius:16px}
.jl-name{font-size:16px !important}
.jl-panel{padding:16px !important;border-radius:18px !important}
}
</style>
</helmet>
<div style="width: 100%; background: #ffffff; color: #123c32; font-family: 'Outfit', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; -webkit-font-smoothing: antialiased">
<dc-import name="Main" part-from="0" part-to="0" hint-size="100%,127px"></dc-import>

<!-- Uvod i izbor -->
<section style="background: #f0f6ec; padding: clamp(28px, 4vw, 48px) 20px clamp(32px, 4vw, 48px)">
<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 22px">
<a class="jl-back" href="Main.dc.html" style="align-self: flex-start; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-size: 15px; font-weight: 600; color: #4d7a31; text-decoration: none">""" + BACK + r"""Nazad na početnu</a>
<div style="display: flex; flex-direction: column; gap: 14px; margin-top: -8px">
<h1 style="margin: 0; font-size: clamp(28px, 4.4vw, 52px); line-height: 1.1; letter-spacing: -0.03em; font-weight: 700; color: #123c32">{{ titleA }} <span class="jl-h1b" style="color: #5e8f3d">{{ titleB }}</span></h1>
<p style="margin: 0; max-width: 760px; font-size: 18px; line-height: 1.55; color: #3d4a41; text-wrap: pretty">Izaberi meni i veličinu paketa. Svakog dana stižu četiri obroka, na tvoja&nbsp;vrata.</p>
</div>
<div class="jl-panel" style="display: flex; flex-direction: column; gap: 18px; box-sizing: border-box; padding: 24px 28px; border-radius: 22px; background: #ffffff; border: 1px solid #dfeccf">
<div class="jl-row">
<span style="font-size: 14px; font-weight: 700; letter-spacing: 0.06em; color: #3d4a41">MENI</span>
<div class="jl-opts" role="group" aria-label="Meni">
<sc-for list="{{ menuTabs }}" as="f" hint-placeholder-count="6">
<button type="button" class="jl-pick" aria-pressed="{{ f.on }}" onClick="{{ f.pick }}" style="min-height: 44px; padding: 9px 18px; border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; white-space: nowrap; {{ f.style }}">{{ f.label }}</button>
</sc-for>
</div>
</div>
<div style="height: 1px; background: #e3e8e2"></div>
<div class="jl-row">
<span style="font-size: 14px; font-weight: 700; letter-spacing: 0.06em; color: #3d4a41">PAKET</span>
<div style="display: flex; flex-direction: column; gap: 10px; min-width: 0">
<div class="jl-opts" role="group" aria-label="Veličina paketa">
<sc-for list="{{ sizeOpts }}" as="o" hint-placeholder-count="5">
<button type="button" class="jl-pick" aria-pressed="{{ o.on }}" onClick="{{ o.pick }}" style="min-height: 44px; padding: 9px 16px; border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; white-space: nowrap; {{ o.style }}">{{ o.label }}</button>
</sc-for>
</div>
<span style="font-size: 14px; line-height: 1.45; color: #3d4a41; text-wrap: pretty">{{ sizeNote }}</span>
</div>
</div>
<sc-if value="{{ notPosno }}" hint-placeholder-val="{{ true }}">
<div style="height: 1px; background: #e3e8e2"></div>
<div class="jl-row">
<span style="font-size: 14px; font-weight: 700; letter-spacing: 0.06em; color: #3d4a41">NEDELJA</span>
<div class="jl-opts" role="group" aria-label="Nedelja">
<sc-for list="{{ weekTabs }}" as="w" hint-placeholder-count="3">
<button type="button" class="jl-pick" aria-pressed="{{ w.on }}" onClick="{{ w.pick }}" style="min-height: 44px; padding: 9px 16px; border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; white-space: nowrap; {{ w.style }}">{{ w.label }}</button>
</sc-for>
</div>
</div>
</sc-if>
</div>
</div>
</section>

<!-- Nedelja po danima -->
<sc-if value="{{ notPosno }}" hint-placeholder-val="{{ true }}">
<section style="background: #ffffff; padding: clamp(36px, 5vw, 56px) 20px 8px">
<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: clamp(40px, 5vw, 56px)">
<sc-for list="{{ days }}" as="d" hint-placeholder-count="7">
<div style="display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 20px; padding-bottom: 14px; border-bottom: 1px solid #e3e8e2">
<div style="display: flex; align-items: center; gap: 10px">
<h2 style="margin: 0; font-size: clamp(20px, 2vw, 24px); line-height: 1.2; letter-spacing: -0.015em; font-weight: 700; color: #123c32">{{ d.title }}</h2>
<sc-if value="{{ d.today }}" hint-placeholder-val="{{ false }}"><span style="padding: 3px 9px; border-radius: 99px; background: #accb7d; font-size: 12px; font-weight: 700; letter-spacing: 0.06em; color: #123c32">DANAS</span></sc-if>
</div>
<span style="font-size: 15px; font-weight: 600; color: #4d7a31">{{ d.total }}</span>
</div>
<div class="jl-grid">
<sc-for list="{{ d.meals }}" as="c" hint-placeholder-count="4">
""" + card + r"""
</sc-for>
</div>
</div>
</sc-for>
</div>
</section>
</sc-if>

<!-- Posna jela -->
<sc-if value="{{ isPosno }}" hint-placeholder-val="{{ false }}">
<section style="background: #ffffff; padding: clamp(36px, 5vw, 56px) 20px 8px">
<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 18px">
<div style="padding-bottom: 14px; border-bottom: 1px solid #e3e8e2">
<h2 style="margin: 0; font-size: clamp(20px, 2vw, 24px); line-height: 1.2; letter-spacing: -0.015em; font-weight: 700; color: #123c32">{{ posnoTitle }}</h2>
</div>
<div class="jl-grid">
<sc-for list="{{ posnoCards }}" as="c" hint-placeholder-count="8">
""" + card + r"""
</sc-for>
</div>
</div>
</section>
</sc-if>

<dc-import name="Main" part-from="15" part-to="16" hint-size="100%,1020px"></dc-import>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1440,"height":5430}}'>
class Component extends DCLogic {
""" + data + r"""  renderVals() {
    const st = this.state || {};
    if (!this._jel) this._jel = this.jelovnik();
    const J = this._jel;
    const NB = ' ';
    // Bez usamljene reci u poslednjem redu: poslednje dve reci uvek zajedno
    const nb = s => String(s).replace(/ (\S+)$/, NB + '$1');
    const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const MENUS = ['Balance', 'Fish', 'Vegetarijanski', 'Vegan', 'Bez glutena', 'Posno'];
    const MEALS = ['DORUČAK', 'UŽINA', 'RUČAK', 'VEČERA'];
    const KCAL = [1300, 1600, 2000, 2600, 3000];
    const PACK = ['NutriSlim za žene', 'NutriSlim za muškarce i NutriBalance za žene', 'NutriBalance za muškarce i NutriPump za žene', 'NutriPump za muškarce', 'NutriMax za muškarce'];

    // Naredna nedelja: nedelja koja počinje prvog ponedeljka posle danas (jelovnik kreće u ponedeljak 9.11.2026)
    const start = new Date(2026, 10, 9);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const since = Math.round((today - start) / 86400000);
    const nextWk = Math.max(0, Math.min(2, since < 0 ? 0 : Math.floor(since / 7) + 1));

    const mi = st.mi === undefined ? 0 : st.mi;
    const isPosno = mi === 5;
    const maxSz = mi === 3 ? 2 : 4;
    const sz = Math.min(st.sz === undefined ? 2 : st.sz, maxSz);
    const wk = st.wk === undefined ? nextWk : st.wk;
    const on = 'background: #123c32; color: #ffffff; border: 1.5px solid #123c32';
    const off = 'background: #ffffff; color: #123c32; border: 1.5px solid #accb7d';

    const menuTabs = MENUS.map((label, i) => ({ label, on: i === mi ? 'true' : 'false', style: i === mi ? on : off, pick: () => this.setState({ mi: i }) }));
    const sizeOpts = KCAL.slice(0, maxSz + 1).map((k, i) => ({ label: fmt(k) + NB + 'kcal', on: i === sz ? 'true' : 'false', style: i === sz ? on : off, pick: () => this.setState({ sz: i }) }));
    const sizeNote = nb(fmt(KCAL[sz]) + ' kcal dnevno: ' + PACK[sz] + '.' + (mi === 3 ? ' Vegan meni je dostupan do 2.000 kcal.' : ''));
    const dayNum = i => J.days[i][1].split('.')[0];
    const weekTabs = [0, 1, 2].map(w => ({
      label: dayNum(w * 7) + '.–' + dayNum(w * 7 + 6) + '. nov' + (w === nextWk ? ' · naredna' : ''),
      on: w === wk ? 'true' : 'false', style: w === wk ? on : off, pick: () => this.setState({ wk: w })
    }));

    const macFor = (mac, s) => { const k = Math.min(s, mac.length / 4 - 1) * 4; return { kcal: mac[k], p: mac[k + 1], uh: mac[k + 2], m: mac[k + 3] }; };
    const card = (name, mac, tag, cls, pos) => {
      const m = macFor(mac, sz);
      return { cls, pos, alt: name, tag, name: nb(name), posno: /posn/i.test(name), kcal: fmt(m.kcal) + ' kcal', macros: m.p + 'g proteina · ' + m.uh + 'g UH · ' + m.m + 'g masti' };
    };

    let days = [], posnoCards = [];
    if (isPosno) {
      posnoCards = J.posno.map((r, i) => card(r[0], r[3], MENUS[r[1]].toUpperCase() + ' · ' + MEALS[r[2]], 'jl-po', (i % 6) * 20 + '% ' + Math.floor(i / 6) * 50 + '%'));
    } else {
      const cls = 'jl-wk jl-s' + (mi * 3 + wk);
      for (let dy = 0; dy < 7; dy++) {
        const di = wk * 7 + dy;
        const meals = J.m[mi][di].map((r, ml) => card(r[0], r[1], MEALS[ml], cls, (ml * 100 / 3).toFixed(4) + '% ' + (dy * 100 / 6).toFixed(4) + '%'));
        const t = J.m[mi][di].reduce((a, r) => { const m = macFor(r[1], sz); return [a[0] + m.kcal, a[1] + m.p]; }, [0, 0]);
        days.push({ title: J.days[di][2], today: di === since, total: 'Ukupno ' + fmt(t[0]) + ' kcal · ' + t[1] + 'g proteina', meals });
      }
    }

    const titleA = isPosno ? 'Posna jela' : (wk === nextWk && since < 21 ? 'Meni za narednu nedelju' : 'Meni za nedelju');
    const titleB = isPosno ? 'od 9. do 29. novembra' : 'od ' + dayNum(wk * 7) + '. do ' + dayNum(wk * 7 + 6) + '. novembra';
    return {
      titleA, titleB: nb(titleB), menuTabs, sizeOpts, sizeNote, weekTabs, days, posnoCards,
      posnoTitle: nb(J.posno.length + ' posnih jela iz svih menija'),
      isPosno, notPosno: !isPosno
    };
  }
}
</script>
</body>
</html>
"""
open(out, "w", encoding="utf-8").write(html)
print("ok", round(len(html) / 1024), "KB")
