import re
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:70], s.count(old))
    s = s.replace(old, new)


# 1) move the menu block (sec.s6 wrapper) right before the system block (sec.s4 wrapper)
m_start = s.index('<sc-if value="{{ sec.s6 }}"')
m_end = s.index('<sc-if value="{{ sec.s7 }}"')
block = s[m_start:m_end]
s = s[:m_start] + s[m_end:]
t = s.index('<sc-if value="{{ sec.s4 }}"')
s = s[:t] + block + s[t:]

# menu now follows the comparison table (white on white): no top padding, like the system section had
rep('<section id="meni" style="background: #ffffff; padding: clamp(64px, 8vw, 96px) 20px">',
    '<section id="meni" style="background: #ffffff; padding: 0 20px clamp(64px, 8vw, 96px)">')

# 2) renumber section wrappers in document order
counter = iter(range(100))
s = re.sub(r'\{\{ sec\.s\d+ \}\}', lambda m: '{{ sec.s%d }}' % next(counter), s)

# 3) hero: secondary CTA next to the primary one
hero_btn_end = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>\n</a>\n'
                '<div style="display: flex; flex-direction: column; gap: 4px; font-size: 14px; line-height: 1.35; color: #3d4a41">\n<span>Prijava traje 2&nbsp;minuta</span>')
rep(hero_btn_end,
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>\n</a>\n'
    '<a class="btn" href="#meni" onClick="{{ goToday }}" style="display: inline-flex; align-items: center; min-height: 58px; box-sizing: border-box; padding: 16px 26px; border-radius: 14px; border: 2px solid #123c32; background: #ffffff; color: #123c32; font-size: 18px; font-weight: 700; text-decoration: none">Pogledaj meni za&nbsp;danas</a>\n'
    '<div style="display: flex; flex-direction: column; gap: 4px; font-size: 14px; line-height: 1.35; color: #3d4a41">\n<span>Prijava traje 2&nbsp;minuta</span>')

# 4) menu opens on today's day (or the first day of the menu that is not in the past)
rep("    const wk = st.wk || 0;\n    const dy = st.dy || 0;\n",
    "    if (this._todayIdx === undefined) {\n"
    "      const t = new Date(); t.setHours(0, 0, 0, 0);\n"
    "      const dateOf = d => { const x = d[1].split('.'); return new Date(2026, +x[1] - 1, +x[0]); };\n"
    "      let ix = J.days.findIndex(d => dateOf(d) >= t);\n"
    "      if (ix < 0) ix = J.days.length - 1;\n"
    "      this._todayIdx = ix;\n"
    "      this._todayExact = dateOf(J.days[ix]).getTime() === t.getTime();\n"
    "    }\n"
    "    const wk = st.wk === undefined ? Math.floor(this._todayIdx / 7) : st.wk;\n"
    "    const dy = st.dy === undefined ? this._todayIdx % 7 : st.dy;\n"
    "    const goToday = () => this.setState({ wk: Math.floor(this._todayIdx / 7), dy: this._todayIdx % 7 });\n")
rep("    const dayTitle = J.days[dayIdx][2];\n",
    "    const dayTitle = (this._todayExact && dayIdx === this._todayIdx ? 'Danas \\u00b7 ' : '') + J.days[dayIdx][2];\n")
rep("    return { sec, menuTabs,", "    return { sec, goToday, menuTabs,")

open(p, "w", encoding="utf-8").write(s)
print("ok")
