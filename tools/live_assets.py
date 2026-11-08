import re
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def between(start_marker, end_marker, new, include_end=True):
    """Replace from start_marker up to (and incl.) end_marker; both must be unique."""
    global s
    assert s.count(start_marker) == 1, ("start", start_marker[:60], s.count(start_marker))
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    if include_end:
        b += len(end_marker)
    s = s[:a] + new + s[b:]


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:70], s.count(old))
    s = s.replace(old, new)


# 1) hero avatars: 3 real photos from the live site
avatars = [
    "/_blob/08ea69fadd37f12a07d0be72d7104b61",
    "/_blob/5716f8d174ebfb590231784a5d5e22b8",
    "/_blob/4464db9535ed3f41e4690b23a8407f37",
]
av_html = '<div style="display: flex; align-items: center" aria-hidden="true">\n'
for i, src in enumerate(avatars):
    ml = "" if i == 0 else " margin-left: -10px;"
    av_html += (f'<img src="{src}" alt="" width="125" height="126" style="width: 38px; height: 38px;{ml} '
                f'border-radius: 99px; border: 2px solid #ffffff; object-fit: cover; display: block; background: #ffffff">\n')
av_html += '</div>\n<span style="font-size: 15px; font-weight: 600; color: #123c32">2.500+ korisnika</span>'
between('<div style="display: flex; align-items: center" aria-hidden="true">\n<span style="width: 36px; height: 36px;',
        '<span style="font-size: 15px; font-weight: 600; color: #123c32">2.500+ korisnika</span>', av_html)

# 2) hero visual: VSL out, food collage from the live site in
hero_visual = '''<div style="flex: 1 1 500px; min-width: 0; position: relative; padding: 10px 0 28px">
<img src="/_blob/c33f489fdbb36b4384e2f4e9889ea628" alt="Nutribox obroci spakovani za ceo dan" width="959" height="532" style="display: block; width: 100%; height: auto">
<div style="position: absolute; left: 2%; bottom: 0; width: 124px; height: 124px; border-radius: 999px; background: #accb7d; color: #123c32; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; text-align: center; transform: rotate(-10deg); box-shadow: 0 12px 28px rgba(18, 60, 50, 0.22)">
<span style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em">SVAKO JUTRO</span>
<span style="font-size: 27px; line-height: 1.05; font-weight: 800; letter-spacing: -0.02em">do&nbsp;9:30</span>
</div>
</div>
</div>
</section>'''
between('<div style="flex: 1 1 420px; min-width: 0; display: flex; flex-direction: column; gap: 14px">\n<div style="position: relative; width: 100%; aspect-ratio: 516 / 340;',
        '</div>\n</div>\n</section>', hero_visual)
rep('<div style="flex: 1 1 540px; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">',
    '<div style="flex: 1 1 520px; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 24px">')

# 3) video testimonials: all 8 from the live site, as a swipe slider
people = [
    ("Miloš Ludus", "/_blob/ec1226f597c7dec757e4c995fe12450b"),
    ("Tamara", "/_blob/48dd7e9204b80dbb912c5dc9f125a63b"),
    ("Tibor Čubrilo", "/_blob/dd0cf92261036a266fe626f3dfb2d53d"),
    ("Miloš Bubaja", "/_blob/f0dad957612601a0a103f55ea9f4ba9c"),
    ("Dušan Kocić", "/_blob/4ef02203b38c984aec205f4b38bb712a"),
    ("Zoran", "/_blob/f7f0842e439dafcbb5430078f75d7386"),
    ("", "/_blob/54901ea1b99eebd5263437b70dfe53c1"),
    ("Sava", "/_blob/f560b51e0a765f5432501a85626fb5c2"),
]
cards = []
for name, src in people:
    label = name or "korisnik"
    band = (f'<span style="position: absolute; left: 12px; right: 12px; bottom: 12px; padding: 10px 14px; border-radius: 14px; '
            f'background: rgba(18, 60, 50, 0.86); font-size: 15px; font-weight: 700; color: #ffffff">{name}</span>\n') if name else ""
    cards.append(f'''<div style="flex: 0 0 250px; scroll-snap-align: start; position: relative; aspect-ratio: 9 / 16; border-radius: 22px; overflow: hidden; background: #123c32">
<img src="{src}" alt="Video utisak: {label}" width="318" height="568" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">
<span style="position: absolute; top: 14px; left: 14px; padding: 5px 10px; border-radius: 99px; background: rgba(18, 60, 50, 0.82); font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #accb7d">VIDEO UTISAK</span>
<button type="button" aria-label="Pusti video utisak: {label}" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 60px; height: 60px; border-radius: 999px; border: 0; background: #ffffff; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25)"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="#123c32"></path></svg></button>
{band}</div>''')
slider = ('<div style="width: 100%; display: flex; flex-direction: column; gap: 14px">\n'
          '<div class="slider" style="width: 100%; display: flex; gap: 20px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 10px">\n'
          + "\n".join(cards) +
          '\n</div>\n'
          '<span style="align-self: flex-end; display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; color: #3d4a41">Prevuci za još&nbsp;utisaka'
          '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg></span>\n'
          '</div>\n'
          '<div style="max-width: 680px; width: 100%; box-sizing: border-box; border-radius: 24px; background: #f0f6ec;')
between('<div class="slider" style="width: 100%; display: flex; gap: 24px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 8px">',
        '<div style="max-width: 680px; width: 100%; box-sizing: border-box; border-radius: 24px; background: #f0f6ec;', slider)

# 4) message screenshots: all 9 from the live site, masonry on desktop, swipe row on phone
shots = [
    ("/_blob/b1b4e6e1cd0ef54976785d35770e1c7d", 469, 563),
    ("/_blob/2d84f2d819ced9430341e6ef3f4045b1", 468, 167),
    ("/_blob/943985ac3e62784b716c1bba1122bd8e", 469, 464),
    ("/_blob/6939c0e1fb3abccbe8d2cffeb41f3bcf", 469, 133),
    ("/_blob/4d884f145ff01de41a1995ad53e8d315", 468, 368),
    ("/_blob/5e4e66659da7f24ab802fa2ded5ba6f8", 469, 277),
    ("/_blob/28f4114881093ab6bc0b621bb3d365b8", 469, 179),
    ("/_blob/0581996be5ea55f522657e0e8d859593", 468, 284),
    ("/_blob/fcb7ef5c674e13aa0c03b0d790bc548c", 469, 117),
]
wall = '<div class="wall" style="width: 100%">\n'
for i, (src, w, h) in enumerate(shots, 1):
    wall += (f'<img src="{src}" alt="Poruka zadovoljnog korisnika {i}" width="{w}" height="{h}" '
             f'style="display: block; width: 100%; height: auto; margin: 0 0 16px; box-sizing: border-box; border: 1px solid #e3e8e2; border-radius: 16px; background: #ffffff; break-inside: avoid">\n')
wall += '</div>\n</div>\n</section>'
between('<div style="width: 100%; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(44%, 260px), 1fr)); gap: 16px">\n<sc-for list="{{ shots }}"',
        '</sc-for>\n</div>\n</div>\n</section>', wall)

# helmet css for the wall
rep('.slider{scrollbar-width:thin}',
    '.slider{scrollbar-width:thin}\n.wall{columns:3 260px;column-gap:16px}\n@media (max-width:640px){.wall{columns:auto;display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;align-items:flex-start;padding-bottom:10px}.wall img{flex:0 0 270px;width:270px !important;margin:0 !important;scroll-snap-align:start}}')

# 5) script: shots placeholder data no longer needed
rep("    const shots = [1, 2, 3, 4, 5, 6, 7, 8].map(n => ({ n }));\n", "")
rep("faqs, shots, dayAcc", "faqs, dayAcc")

open(p, "w", encoding="utf-8").write(s)
print("ok", len(s))
