import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()

section = r"""<section id="meni" style="background: #ffffff; padding: 0 20px clamp(64px, 8vw, 96px)">
<div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 28px">
<h2 style="margin: 0; max-width: 860px; text-align: center; font-size: clamp(30px, 3.6vw, 44px); line-height: 1.12; letter-spacing: -0.025em; font-weight: 700; color: #123c32">112+ novih jela svake&nbsp;nedelje. <span style="color: #5e8f3d">Ovako izgleda tvoja&nbsp;nedelja.</span></h2>
<p style="margin: -10px 0 0; text-align: center; font-size: 16px; color: #3d4a41; text-wrap: balance">Primeri jela iz jelovnika. Jelovnik se menja svake&nbsp;nedelje.</p>
<div role="group" aria-label="Filter po tipu ishrane" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px">
<sc-for list="{{ filters }}" as="f" hint-placeholder-count="7">
<button type="button" class="pick" aria-pressed="{{ f.on }}" onClick="{{ f.pick }}" style="min-height: 44px; padding: 9px 18px; border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; {{ f.style }}">{{ f.label }}</button>
</sc-for>
</div>
<div style="width: 100%; display: flex; flex-direction: column; gap: 10px">
<div class="slider" style="width: 100%; display: flex; gap: 20px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 6px 2px 12px; box-sizing: border-box">
<sc-for list="{{ meals }}" as="m" hint-placeholder-count="5">
<article style="flex: 0 0 250px; min-width: 250px; scroll-snap-align: start; display: flex; flex-direction: column; gap: 10px">
<div style="position: relative; width: 100%; aspect-ratio: 1 / 1; border-radius: 20px; overflow: hidden; background: #e4efdc">
<img src="{{ m.img }}" alt="{{ m.alt }}" loading="lazy" width="480" height="600" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">
<span style="position: absolute; top: 12px; left: 12px; padding: 5px 10px; border-radius: 99px; background: #ffffff; font-size: 13px; font-weight: 700; color: #123c32">{{ m.kcal }}</span>
<sc-if value="{{ m.posno }}" hint-placeholder-val="{{ false }}"><span style="position: absolute; top: 12px; right: 12px; padding: 5px 10px; border-radius: 99px; background: #123c32; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: #accb7d">POSNO</span></sc-if>
</div>
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.06em; color: #4d7a31">{{ m.tag }}</span>
<h3 style="margin: -4px 0 0; font-size: 18px; line-height: 1.25; font-weight: 700; color: #123c32">{{ m.name }}</h3>
<span style="font-size: 13px; font-weight: 500; color: #4d7a31">{{ m.macros }}</span>
</article>
</sc-for>
</div>
<span style="align-self: flex-end; display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; color: #3d4a41">Prevuci za još&nbsp;jela<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg></span>
</div>
<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 14px 16px">
<a class="btn" href="https://www.nutribox.rs/order-form" style="display: inline-flex; align-items: center; gap: 10px; min-height: 58px; box-sizing: border-box; padding: 18px 30px; border-radius: 14px; background: #123c32; color: #ffffff; font-size: 18px; font-weight: 700; text-decoration: none">Izaberi svoj plan
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>
</a>
<a class="btn" href="#jelovnik" style="display: inline-flex; align-items: center; min-height: 58px; box-sizing: border-box; padding: 16px 26px; border-radius: 14px; border: 2px solid #123c32; background: #ffffff; color: #123c32; font-size: 18px; font-weight: 700; text-decoration: none">Pogledaj meni za&nbsp;danas</a>
</div>
</div>
</section>"""

a = s.index('<section id="meni"')
b = s.index("</section>", a) + len("</section>")
s = s[:a] + section + s[b:]

js = r"""    // Jelovnik (Nutribox jelovnik.json): primeri jela za slajder, makroi za paket od 2.000 kcal
    if (!this._jel) this._jel = this.jelovnik();
    const J = this._jel;
    const MENUS = ['Balance', 'Fish', 'Vegetarijanski', 'Vegan', 'Bez glutena'];
    const MEALS = ['DORUČAK', 'UŽINA', 'RUČAK', 'VEČERA'];
    const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const diet = st.diet || 'sve';
    const dietDefs = [['sve', 'Sve'], ['0', 'Balance'], ['1', 'Fish'], ['2', 'Vegetarijanski'], ['3', 'Vegan'], ['posno', 'Posno'], ['4', 'Bez glutena']];
    const filters = dietDefs.map(([id, label]) => {
      const on = id === diet;
      return {
        label,
        on: on ? 'true' : 'false',
        style: on ? 'background: #123c32; color: #ffffff; border: 1.5px solid #123c32' : 'background: #ffffff; color: #123c32; border: 1.5px solid #accb7d',
        pick: () => this.setState({ diet: id })
      };
    });
    const inFilter = r => diet === 'sve' ? r[1] < 7 : diet === 'posno' ? /posn/i.test(r[3]) : (r[0] === +diet && r[1] < 7);
    const ordered = J.rows.slice().sort((a, b) => a[1] - b[1] || a[2] - b[2] || a[0] - b[0]);
    const seen = {};
    const meals = [];
    for (const r of ordered) {
      if (meals.length >= 18) break;
      if (!inFilter(r) || seen[r[3]]) continue;
      seen[r[3]] = 1;
      const k = Math.min(2, r[5].length / 4 - 1) * 4;
      meals.push({
        img: 'meni/' + J.imgs[r[4]] + '.webp',
        alt: r[3],
        tag: MENUS[r[0]].toUpperCase() + ' · ' + MEALS[r[2]],
        name: nb(r[3]),
        posno: /posn/i.test(r[3]),
        kcal: fmt(r[5][k]) + ' kcal',
        macros: r[5][k + 1] + 'g proteina · ' + r[5][k + 2] + 'g UH · ' + r[5][k + 3] + 'g masti'
      });
    }
"""
ja = s.index("    // Jelovnik 9.11. do 29.11.2026")
jb_marker = "    const posnoCount = posnoCards.length;\n"
jb = s.index(jb_marker) + len(jb_marker)
s = s[:ja] + js + s[jb:]

old_ret_start = s.index("    return { sec, goToday,")
old_ret_end = s.index("\n", old_ret_start)
s = s[:old_ret_start] + "    return { sec, filters, meals, plans, selLabel, faqs, dayAcc, dayGen };" + s[old_ret_end:]

open(p, "w", encoding="utf-8").write(s)
print("ok")
