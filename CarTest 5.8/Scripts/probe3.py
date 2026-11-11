import unreal, re, inspect
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe3.txt"
L = []
base = set(dir(unreal.Object))
for n in ["BlueprintGraphEditor","EdGraph","EdGraphNode","K2Node","EdGraphPin","BlueprintGraphPinLibrary","BlueprintEditorLibrary"]:
    c = getattr(unreal, n, None)
    if c is None: L.append("## %s missing" % n); continue
    L.append("## %s: %s" % (n, " ".join(x for x in dir(c) if not x.startswith("_") and x not in base)))
for fn in ["try_create_connection","set_pin_value","get_pin_value"]:
    L.append(fn + ": " + (getattr(unreal.BlueprintGraphPinLibrary, fn).__doc__ or "")[:800])
for fn in ["find_event_graph","list_all_pins","find_graph","add_function_graph","list_graphs"]:
    L.append(fn + ": " + (getattr(unreal.BlueprintEditorLibrary, fn).__doc__ or "")[:600])
c = getattr(unreal, "BlueprintGraphEditor", None)
if c:
    for x in dir(c):
        if not x.startswith("_") and x not in base:
            L.append("BGE." + x + ": " + (getattr(c, x).__doc__ or "")[:700])
others = [n for n in dir(unreal) if re.search(r"(Spawn.*Node|NodeSpawn|GraphEdit|BlueprintNode|Node.*Library|Graph.*Library|Blueprint.*Library)", n)]
L.append("others: " + " ".join(others))
with open(OUT, "w") as f: f.write("\n".join(L))
