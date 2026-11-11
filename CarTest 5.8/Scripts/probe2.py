import unreal, re
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe2.txt"
L = []
names = [n for n in dir(unreal) if re.search(r"(Graph|Pin|K2|Node|AnimBlueprint|AnimGraph|StateMachine|Blendspace|BlendSpace|Montage)", n)]
L.append(" ".join(names))
for n in names:
    if re.search(r"(Library|Subsystem|Utils|Utilities|Helpers)$", n):
        c = getattr(unreal, n)
        L.append("## " + n + ": " + " ".join(x for x in dir(c) if not x.startswith("_") and x not in dir(unreal.Object)))
with open(OUT, "w") as f: f.write("\n".join(L))
