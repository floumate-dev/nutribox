import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()

start = '<div style="grid-row: span 2; position: relative; border-radius: 22px; background: #30563f;'
end = '<span style="position: relative; font-size: 13px; color: #accb7d">Executive Chef</span>\n</div>'
assert s.count(start) == 1 and s.count(end) == 1
a = s.index(start)
b = s.index(end) + len(end)


def cell(src, w, h, pos, name, role, extra=""):
    return f'''<div style="{extra}position: relative; border-radius: 22px; background: #30563f; overflow: hidden">
<img src="{src}" alt="{name}, {role}" width="{w}" height="{h}" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: {pos}; display: block">
<div style="position: absolute; left: 12px; right: 12px; bottom: 12px; padding: 10px 14px; border-radius: 14px; background: rgba(18, 60, 50, 0.88); display: flex; flex-direction: column; gap: 2px">
<span style="font-size: 16px; font-weight: 700; color: #ffffff">{name}</span>
<span style="font-size: 13px; color: #accb7d">{role}</span>
</div>
</div>'''


new = "\n".join([
    cell("/_blob/ec797353543bd116e39ec0f77dc993c2", 640, 640, "64% 30%", "Vuksan Vasić", "Osnivač Nutriboxa", "grid-row: span 2; "),
    cell("/_blob/7dfdeaeb68b1f16eed6a786daa5dbd41", 800, 1200, "50% 22%", "Miloš Simić", "Vodi kuhinju"),
    cell("/_blob/0a4fee7dafd76b0cccf8bf05276d4464", 864, 1080, "62% 14%", "Amer Hamza", "Executive Chef"),
])
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
