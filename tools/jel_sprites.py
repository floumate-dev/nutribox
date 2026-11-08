"""Sprite sheets for the Jelovnik page: one per (menu, week), 4 meals x 7 days, square tiles."""
import json, os, sys
from PIL import Image

jdir, out = sys.argv[1], sys.argv[2]
T = 440
d = json.load(open(os.path.join(jdir, "jelovnik.json"), encoding="utf-8"))
MENUS = ["Balance", "Fish", "Vegetarijanski", "Vegan", "Bez glutena"]
MEALS = ["Doručak", "Užina", "Ručak", "Večera"]
dates = sorted(set(o["datum"] for o in d["obroci"]))
cell = {}
for o in d["obroci"]:
    cell[(MENUS.index(o["meni"]), dates.index(o["datum"]), MEALS.index(o["obrok"]))] = o["slika"]

def tile(path):
    im = Image.open(os.path.join(jdir, path)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    return im.resize((T, T), Image.LANCZOS)

for mi in range(5):
    for wk in range(3):
        sheet = Image.new("RGB", (4 * T, 7 * T), (228, 239, 220))
        for dy in range(7):
            for ml in range(4):
                sheet.paste(tile(cell[(mi, wk * 7 + dy, ml)]), (ml * T, dy * T))
        p = os.path.join(out, "jel-m%dw%d.webp" % (mi, wk))
        sheet.save(p, "WEBP", quality=72, method=6)
        print(p.split("/")[-1], round(os.path.getsize(p) / 1024), "KB")
