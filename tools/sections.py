import re
import sys

main_path, footer_path = sys.argv[1], sys.argv[2]
src = open(main_path, encoding="utf-8").read()
footer = open(footer_path, encoding="utf-8").read().rstrip("\n")

# 1) replace old footer (from marker up to the m-pad div, inclusive)
start = src.index("<!-- Footer -->")
mpad = '<div class="m-pad" style="height: 84px; background: #123c32"></div>'
end = src.index(mpad) + len(mpad)
src = src[:start] + footer + src[end:]

# 2) wrap every section group in <sc-if> so the page can be shown in parts
markers = [
    ("<!-- S0 Top bar -->", 0),
    ("<!-- S1 Hero -->", 1),
    ("<!-- S2 Prepoznaješ li svoj dan -->", 2),
    ("<!-- S3 Poređenje -->", 3),
    ("<!-- S4 Mehanizam -->", 4),
    ("<!-- S5 Ko kuva -->", 5),
    ("<!-- S6 Meni -->", 6),
    ("<!-- S7 Benefiti -->", 7),
    ("<!-- S8 Socijalni dokaz -->", 8),
    ("<!-- S9 Kako funkcioniše -->", 9),
    ("<!-- S10 Ponuda -->", 10),
    ("<!-- S11 Garancija -->", 11),
    ("<!-- S12 Zamerke -->", 12),
    ("<!-- S13 Zašto sada -->", 13),
    ("<!-- S15 FAQ -->", 14),
    ("<!-- S16 Završni CTA -->", 15),
    ("<!-- Footer -->", 16),
]
positions = [(src.index(m), i, m) for m, i in markers]
root_end = src.index("</div>\n</x-dc>")
out = []
cursor = 0
for k, (pos, i, m) in enumerate(positions):
    out.append(src[cursor:pos])
    nxt = positions[k + 1][0] if k + 1 < len(positions) else root_end
    block = src[pos:nxt].rstrip("\n")
    out.append(f'<sc-if value="{{{{ sec.s{i} }}}}" hint-placeholder-val="{{{{ true }}}}">\n{block}\n</sc-if>\n\n')
    cursor = nxt
out.append(src[cursor:])
src = "".join(out)

open(main_path, "w", encoding="utf-8").write(src)
print("ok", src.count("<sc-if value=\"{{ sec.s"))
