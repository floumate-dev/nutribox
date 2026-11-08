import re
import sys

path = sys.argv[1]
src = open(path, encoding="utf-8").read()

start = src.index("</helmet>") + len("</helmet>")
end = src.index("</x-dc>")
markup = src[start:end]

count = 0


def fix(m):
    global count
    text = m.group(1)
    # skip whitespace-only, holes, and short fragments
    if "{{" in text or "}}" in text:
        return m.group(0)
    stripped = text.strip()
    if len(stripped.split()) < 3 or "&nbsp;" in stripped[-20:]:
        return m.group(0)
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    new = re.sub(r" (\S+)$", r"&nbsp;\1", stripped)
    if new != stripped:
        count += 1
    return ">" + lead + new + trail + "<"


markup = re.sub(r">([^<>]+)<", fix, markup)
open(path, "w", encoding="utf-8").write(src[:start] + markup + src[end:])
print("text blocks fixed:", count)
