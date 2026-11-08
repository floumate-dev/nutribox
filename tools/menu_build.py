"""Builds the real menu (jelovnik) section into Main.dc.html.

argv: <Main.dc.html> <jelovnik folder> <images out dir (project/meni)>
"""
import datetime
import hashlib
import json
import os
import shutil
import sys

main_path, jdir, img_out = sys.argv[1], sys.argv[2], sys.argv[3]
src_img = "/tmp/claude-0/-home-claude/3329e8b3-6e27-5700-b2d8-fd4aa6abfcc3/scratchpad/meni-img"
os.makedirs(img_out, exist_ok=True)

d = json.load(open(os.path.join(jdir, "jelovnik.json"), encoding="utf-8"))
ob = d["obroci"]
MENUS = ["Balance", "Fish", "Vegetarijanski", "Vegan", "Bez glutena"]
MEALS = ["Doručak", "Užina", "Ručak", "Večera"]
SIZES = ["XS", "S", "M", "L", "XL"]
dates = sorted(set(o["datum"] for o in ob))
WD_SHORT = ["Pon", "Uto", "Sre", "Čet", "Pet", "Sub", "Ned"]
WD_LONG = ["Ponedeljak", "Utorak", "Sreda", "Četvrtak", "Petak", "Subota", "Nedelja"]
MONTHS = ["januar", "februar", "mart", "april", "maj", "jun", "jul", "avgust", "septembar", "oktobar", "novembar", "decembar"]
days = []
for ds in dates:
    dt = datetime.date.fromisoformat(ds)
    days.append([WD_SHORT[dt.weekday()], f"{dt.day}.{dt.month}.", f"{WD_LONG[dt.weekday()]}, {dt.day}. {MONTHS[dt.month - 1]}"])

imgs, img_idx, rows = [], {}, []
for o in ob:
    h = hashlib.md5(open(os.path.join(jdir, o["slika"]), "rb").read()).hexdigest()[:12]
    if h not in img_idx:
        img_idx[h] = len(imgs)
        imgs.append(h)
        shutil.copy(os.path.join(src_img, h + ".webp"), os.path.join(img_out, h + ".webp"))
    mac = []
    for s in SIZES:
        if s in o["makroi"]:
            m = o["makroi"][s]
            mac += [m["kcal"], m["p"], m["uh"], m["m"]]
    rows.append([MENUS.index(o["meni"]), dates.index(o["datum"]), MEALS.index(o["obrok"]), o["jelo"], img_idx[h], mac])

js_data = (
    "      days: " + json.dumps(days, ensure_ascii=False) + ",\n"
    "      imgs: " + json.dumps(imgs) + ",\n"
    "      rows: [\n" + ",\n".join("        " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n      ]\n"
)

script_block = r"""    const plan = st.plan || '28';
    const openFaq = st.faq === undefined ? 0 : st.faq;
    // Bez usamljene reci u poslednjem redu: poslednje dve reci uvek zajedno
    const nb = s => String(s).replace(/ (\S+)$/, ' $1');

    // Jelovnik 9.11. do 29.11.2026 (Nutribox jelovnik.json): meni, dan, obrok, jelo, slika, makroi XS..XL
    if (!this._jel) this._jel = this.jelovnik();
    const J = this._jel;
    const MENUS = ['Balance', 'Fish', 'Vegetarijanski', 'Vegan', 'Bez glutena', 'Posno'];
    const MEALS = ['DORUČAK', 'UŽINA', 'RUČAK', 'VEČERA'];
    const KCAL = [1300, 1600, 2000, 2600, 3000];
    const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const mi = st.mi === undefined ? 0 : st.mi;
    const isPosno = mi === 5;
    const maxSz = mi === 3 ? 2 : 4;
    const sz = Math.min(st.sz === undefined ? 2 : st.sz, maxSz);
    const wk = st.wk || 0;
    const dy = st.dy || 0;
    const dayIdx = wk * 7 + dy;
    const on = 'background: #123c32; color: #ffffff; border: 1.5px solid #123c32';
    const off = 'background: #ffffff; color: #123c32; border: 1.5px solid #accb7d';
    const menuTabs = MENUS.map((label, i) => ({ label, on: i === mi ? 'true' : 'false', style: i === mi ? on : off, pick: () => this.setState({ mi: i }) }));
    const sizeOpts = KCAL.slice(0, maxSz + 1).map((k, i) => ({ label: fmt(k) + ' kcal', on: i === sz ? 'true' : 'false', style: i === sz ? on : off, pick: () => this.setState({ sz: i }) }));
    const weekTabs = [0, 1, 2].map(w => {
      const a = J.days[w * 7], b = J.days[w * 7 + 6];
      return { label: a[1].split('.')[0] + '.–' + b[1].split('.')[0] + '. nov', on: w === wk ? 'true' : 'false', style: w === wk ? on : off, pick: () => this.setState({ wk: w, dy: 0 }) };
    });
    const dayBtns = [0, 1, 2, 3, 4, 5, 6].map(i => {
      const dd = J.days[wk * 7 + i];
      return { wd: dd[0], dt: dd[1], on: i === dy ? 'true' : 'false', style: i === dy ? on : off, pick: () => this.setState({ dy: i }) };
    });
    const macFor = (mac, s) => {
      const n = mac.length / 4; const k = Math.min(s, n - 1) * 4;
      return { kcal: mac[k], p: mac[k + 1], uh: mac[k + 2], m: mac[k + 3] };
    };
    const card = (r, withMenu) => {
      const m = macFor(r[5], sz);
      const posno = /posn/i.test(r[3]);
      return {
        img: 'meni/' + J.imgs[r[4]] + '.webp',
        alt: r[3],
        meal: withMenu ? MENUS[r[0]].toUpperCase() + ' · ' + MEALS[r[2]] : MEALS[r[2]],
        name: nb(r[3]),
        posno,
        kcal: fmt(m.kcal) + ' kcal',
        mac: 'P ' + m.p + ' g · UH ' + m.uh + ' g · M ' + m.m + ' g'
      };
    };
    let dayCards = [], posnoCards = [], dayTotal = '';
    if (isPosno) {
      const seen = {};
      J.rows.forEach(r => { if (/posn/i.test(r[3]) && !seen[r[3]]) { seen[r[3]] = 1; posnoCards.push(card(r, true)); } });
    } else {
      const rs = J.rows.filter(r => r[0] === mi && r[1] === dayIdx).sort((a, b) => a[2] - b[2]);
      dayCards = rs.map(r => card(r, false));
      dayTotal = fmt(rs.reduce((t, r) => t + macFor(r[5], sz).kcal, 0)) + ' kcal';
    }
    const dayTitle = J.days[dayIdx][2];
    const posnoCount = posnoCards.length;
"""

method_block = "  jelovnik() {\n    return {\n" + js_data + "    };\n  }\n"

section = r"""<!-- S6 Meni -->
<section id="meni" style="background: #ffffff; padding: clamp(64px, 8vw, 96px) 20px">
<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 26px">
<h2 style="margin: 0; max-width: 860px; text-align: center; font-size: clamp(30px, 3.6vw, 44px); line-height: 1.12; letter-spacing: -0.025em; font-weight: 700; color: #123c32">112+ novih jela svake&nbsp;nedelje. <span style="color: #5e8f3d">Ovako izgleda tvoja&nbsp;nedelja.</span></h2>
<p style="margin: -10px 0 0; text-align: center; font-size: 16px; color: #3d4a41; text-wrap: balance">Pravi jelovnik od 9. do 29. novembra. Izaberi meni, veličinu paketa i&nbsp;dan.</p>
<div role="group" aria-label="Meni" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px">
<sc-for list="{{ menuTabs }}" as="f" hint-placeholder-count="6">
<button type="button" class="pick" aria-pressed="{{ f.on }}" onClick="{{ f.pick }}" style="min-height: 44px; padding: 9px 18px; border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; {{ f.style }}">{{ f.label }}</button>
</sc-for>
</div>
<div class="mctrl">
<sc-if value="{{ notPosno }}" hint-placeholder-val="{{ true }}">
<div role="group" aria-label="Nedelja" style="display: flex; flex-wrap: wrap; gap: 8px">
<sc-for list="{{ weekTabs }}" as="w" hint-placeholder-count="3">
<button type="button" class="pick" aria-pressed="{{ w.on }}" onClick="{{ w.pick }}" style="min-height: 44px; padding: 8px 14px; border-radius: 12px; font-family: inherit; font-size: 14px; font-weight: 600; cursor: pointer; {{ w.style }}">{{ w.label }}</button>
</sc-for>
</div>
</sc-if>
<sc-if value="{{ isPosno }}" hint-placeholder-val="{{ false }}">
<span style="font-size: 15px; font-weight: 600; color: #123c32">{{ posnoCount }} posnih jela u&nbsp;jelovniku</span>
</sc-if>
<div role="group" aria-label="Veličina paketa" style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px">
<span style="font-size: 14px; font-weight: 600; color: #3d4a41; margin-right: 2px">Veličina&nbsp;paketa:</span>
<sc-for list="{{ sizeOpts }}" as="o" hint-placeholder-count="5">
<button type="button" class="pick" aria-pressed="{{ o.on }}" onClick="{{ o.pick }}" style="min-height: 44px; padding: 8px 12px; border-radius: 12px; font-family: inherit; font-size: 14px; font-weight: 600; cursor: pointer; {{ o.style }}">{{ o.label }}</button>
</sc-for>
</div>
</div>
<sc-if value="{{ notPosno }}" hint-placeholder-val="{{ true }}">
<div class="mdays" role="group" aria-label="Dan">
<sc-for list="{{ dayBtns }}" as="b" hint-placeholder-count="7">
<button type="button" class="pick" aria-pressed="{{ b.on }}" onClick="{{ b.pick }}" style="min-height: 56px; padding: 8px 4px; border-radius: 14px; font-family: inherit; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; {{ b.style }}"><span style="font-size: 12px; font-weight: 600; letter-spacing: 0.04em">{{ b.wd }}</span><span style="font-size: 15px; font-weight: 700">{{ b.dt }}</span></button>
</sc-for>
</div>
<div style="width: 100%; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 6px 20px; border-bottom: 1px solid #e3e8e2; padding-bottom: 14px">
<span style="font-size: 20px; font-weight: 700; color: #123c32">{{ dayTitle }}</span>
<span style="font-size: 15px; font-weight: 600; color: #4d7a31">Ukupno za dan: {{ dayTotal }}</span>
</div>
<div class="mgrid">
<sc-for list="{{ dayCards }}" as="c" hint-placeholder-count="4">
<article class="mcard">
<div class="mimg">
<img src="{{ c.img }}" alt="{{ c.alt }}" loading="lazy" width="480" height="600" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">
<span style="position: absolute; top: 10px; left: 10px; padding: 4px 9px; border-radius: 99px; background: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #123c32">{{ c.meal }}</span>
<sc-if value="{{ c.posno }}" hint-placeholder-val="{{ false }}"><span style="position: absolute; bottom: 10px; left: 10px; padding: 4px 9px; border-radius: 99px; background: #123c32; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #accb7d">POSNO</span></sc-if>
</div>
<div style="display: flex; flex-direction: column; gap: 6px; min-width: 0">
<h3 style="margin: 0; font-size: 16px; line-height: 1.3; font-weight: 700; color: #123c32">{{ c.name }}</h3>
<span style="font-size: 15px; font-weight: 700; color: #123c32">{{ c.kcal }}</span>
<span style="font-size: 13px; color: #4d7a31">{{ c.mac }}</span>
</div>
</article>
</sc-for>
</div>
</sc-if>
<sc-if value="{{ isPosno }}" hint-placeholder-val="{{ false }}">
<div class="mslider slider">
<sc-for list="{{ posnoCards }}" as="c" hint-placeholder-count="4">
<article class="mcard">
<div class="mimg">
<img src="{{ c.img }}" alt="{{ c.alt }}" loading="lazy" width="480" height="600" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">
<span style="position: absolute; top: 10px; left: 10px; padding: 4px 9px; border-radius: 99px; background: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #123c32">{{ c.meal }}</span>
</div>
<div style="display: flex; flex-direction: column; gap: 6px; min-width: 0">
<h3 style="margin: 0; font-size: 16px; line-height: 1.3; font-weight: 700; color: #123c32">{{ c.name }}</h3>
<span style="font-size: 15px; font-weight: 700; color: #123c32">{{ c.kcal }}</span>
<span style="font-size: 13px; color: #4d7a31">{{ c.mac }}</span>
</div>
</article>
</sc-for>
</div>
</sc-if>
<a class="btn" href="https://www.nutribox.rs/order-form" style="display: inline-flex; align-items: center; gap: 10px; min-height: 58px; box-sizing: border-box; padding: 18px 30px; border-radius: 14px; background: #123c32; color: #ffffff; font-size: 18px; font-weight: 700; text-decoration: none">Izaberi svoj plan
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>
</a>
</div>
</section>"""

css = (".mctrl{width:100%;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px 24px}\n"
       ".mdays{width:100%;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}\n"
       ".mgrid{width:100%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}\n"
       ".mcard{display:flex;flex-direction:column;gap:12px;min-width:0}\n"
       ".mimg{position:relative;width:100%;aspect-ratio:4/5;border-radius:18px;overflow:hidden;background:#e4efdc}\n"
       ".mslider{width:100%;display:flex;gap:20px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}\n"
       ".mslider .mcard{flex:0 0 250px;scroll-snap-align:start}\n"
       "@media (max-width:960px){.mgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}\n")
css_mobile = (".mdays{gap:5px}\n"
              ".mgrid{grid-template-columns:1fr;gap:12px}\n"
              ".mgrid .mcard{flex-direction:row;align-items:center;gap:14px}\n"
              ".mgrid .mimg{width:112px;flex:none;border-radius:14px}\n"
              ".mslider .mcard{flex-basis:220px}\n")

s = open(main_path, encoding="utf-8").read()


def must(cond, msg):
    if not cond:
        raise SystemExit(msg)


# section
a = s.index("<!-- S6 Meni -->")
b = s.index("</section>", a) + len("</section>")
s = s[:a] + section + s[b:]

# script: replace from 'const diet' through end of the old meals statement
sa = s.index("    const diet = st.diet || 'sve';\n")
mk = "    const meals = allMeals\n"
sb = s.index(mk, sa)
sb = s.index(";\n", sb) + 2
s = s[:sa] + script_block + s[sb:]

# method on the class, right before renderVals
anchor = "class Component extends DCLogic {\n"
must(s.count(anchor) == 1, "class anchor")
s = s.replace(anchor, anchor + method_block)

# return values
old_ret = "    return { sec, filters, meals, noMeals: meals.length === 0, plans, selLabel, faqs, dayAcc, dayGen };"
must(s.count(old_ret) == 1, "return")
s = s.replace(old_ret, "    return { sec, menuTabs, sizeOpts, weekTabs, dayBtns, dayCards, posnoCards, posnoCount, dayTotal, dayTitle, isPosno, notPosno: !isPosno, plans, selLabel, faqs, dayAcc, dayGen };")

# css
anc = ".slider{scrollbar-width:thin}\n"
must(s.count(anc) == 1, "css anchor")
s = s.replace(anc, anc + css)
anc2 = ".faq-a{padding-left:22px !important}\n"
must(s.count(anc2) == 1, "css mobile anchor")
s = s.replace(anc2, anc2 + css_mobile)

open(main_path, "w", encoding="utf-8").write(s)
print("ok", len(rows), "rows", len(imgs), "images", round(len(s) / 1024), "KB")
