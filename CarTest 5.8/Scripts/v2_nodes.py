import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_nodes.txt"
L = []
try:
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    ed = unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(car))
    L.append(str(ed.list_available_nodes.__doc__))
    res = None
    for args in ((), ("",), ([],)):
        try: res = ed.list_available_nodes(*args); break
        except Exception as e: L.append("try %s: %s" % (args, e))
    if res is not None:
        res = [str(x) for x in res]
        L.append("count %d" % len(res))
        for x in res:
            lx = x.lower()
            if any(k in lx for k in ("dynamicmaterial", "blendable", "scalarparameter", "drawrect", "drawtext", "owningpawn", "receivedrawhud", "drawhud")):
                L.append(x)
except Exception:
    L.append(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
