import json
import sys

p, lists_path = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
lists = json.load(open(lists_path, encoding="utf-8"))

ids = ["5268c4efc91305d89927836ba6d7a1ca", "a6755f9077c34c78ac20363be64911e2", "ac0b5ff04f67981eb24a6ec096d56872",
       "962f6318639b2c60209dcd8d2dda2b52", "1a20fbb6c5bc534a6d209d1149c3acec", "be0e8408087d67f0aff97b2423547726",
       "201adcf31c849c484cf36d35fa1995f8"]


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:70], s.count(old))
    s = s.replace(old, new)


# 1) helmet css: one sheet of 18 dish photos per filter (6 x 3 tiles)
css = ".spr{background-size:600% 300%;background-repeat:no-repeat;background-color:#e4efdc}\n" + "".join(
    ".sp%d{background-image:url(/_blob/%s)}\n" % (i, x) for i, x in enumerate(ids))
rep(".slider{scrollbar-width:thin}\n", ".slider{scrollbar-width:thin}\n" + css)

# 2) card photo: tile from the sheet
rep('<img src="{{ m.img }}" alt="{{ m.alt }}" width="480" height="600" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">',
    '<div class="spr {{ m.sp }}" role="img" aria-label="{{ m.alt }}" style="position: absolute; inset: 0; background-position: {{ m.pos }}"></div>')

# 3) data method: only the dishes the slider shows
a = s.index("  jelovnik() {\n")
b = s.index("  renderVals() {", a)
data = "  jelovnik() {\n    // po filteru: [jelo, meni, obrok, kcal, P, UH, M] za paket od 2.000 kcal, redom kao na slici-mapi\n    return {\n"
data += ",\n".join("      %s: [\n%s\n      ]" % (json.dumps(k), ",\n".join("        " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in v)) for k, v in lists.items())
data += "\n    };\n  }\n"
s = s[:a] + data + s[b:]

# 4) slider items from the lists
a = s.index("    // Sve: svaki dan drugi meni")
b = s.index("      });\n    }\n\n    const planDefs", a) + len("      });\n    }\n")
new = r"""    const spIdx = { sve: 0, '0': 1, '1': 2, '2': 3, '3': 4, posno: 5, '4': 6 }[diet];
    const meals = (J[diet] || []).map((c, i) => ({
      sp: 'sp' + spIdx,
      pos: (i % 6) * 20 + '% ' + Math.floor(i / 6) * 50 + '%',
      alt: c[0],
      tag: MENUS[c[1]].toUpperCase() + ' · ' + MEALS[c[2]],
      name: nb(c[0]),
      posno: /posn/i.test(c[0]),
      kcal: fmt(c[3]) + ' kcal',
      macros: c[4] + 'g proteina · ' + c[5] + 'g UH · ' + c[6] + 'g masti'
    }));
"""
s = s[:a] + new + s[b:]
rep("    // Jelovnik (Nutribox jelovnik.json): primeri jela za slajder, makroi za paket od 2.000 kcal\n",
    "    // Jelovnik (Nutribox jelovnik.json): 18 primera jela po filteru, makroi za paket od 2.000 kcal\n")
open(p, "w", encoding="utf-8").write(s)
print("ok", round(len(s) / 1024), "KB")
