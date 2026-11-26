import json, sys, os, re
root, comp = sys.argv[1], sys.argv[2]
t = json.load(open(os.path.join(root, "tokens.json"), encoding="utf-8"))
first = t["color"]["themes"][0]["id"]
v = []
for k in t["color"]["tokens"]:
    val = k["value"] if isinstance(k["value"], str) else k["value"].get(first)
    v.append(f"--{k['name']}:{val}")
for fam in ("spacing", "radius", "shadow"):
    for k in t[fam]["tokens"]:
        v.append(f"--{k['name']}:{k['value']}")
for key, stack in t["type"]["families"].items():
    v.append(f"--font-{key}:{stack}")
b = open(os.path.join(root, "components/bundle.css"), encoding="utf-8").read()
k = b.index("\n")
css = b[:k + 1] + ":root{" + ";".join(v) + "}\n" + b[k + 1:]
html = open(os.path.join(root, f"components/{comp}/preview.html"), encoding="utf-8").read()
html = html.replace("<head>", f"<head><style>{css}</style>", 1)
out = os.path.join(os.path.dirname(root), f"test_{comp}.html")
open(out, "w", encoding="utf-8").write(html)
print(out)
