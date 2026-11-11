# Dumps what the car's own overlap/hit events are wired to, plus the pad trigger's collision responses.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v3_probe_overlap.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
def t(nd): return str(BEL.get_node_title(nd)).splitlines()[0]
try:
    for path in ("/Game/Car/Blueprints/BP_CarPawn", "/Game/Car/Blueprints/BP_CarPawn_Moon"):
        bp = unreal.load_asset(path)
        ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(bp))
        for nd in ed.list_all_nodes():
            tt = t(nd)
            if "Overlap" in tt or "Hit" in tt:
                outs = []
                for p in BEL.list_all_pins(nd):
                    for q in PL.list_connected_pins(p):
                        outs.append("%s->%s" % (PL.get_pin_name(p), t(PL.get_owning_node(q)) if hasattr(PL, "get_owning_node") else "?"))
                log(path.split("/")[-1], "node", tt, "links", outs)
    cdo = unreal.get_default_object(unreal.load_asset("/Game/Car/Placeholders/BP_BoostPad").generated_class())
    log("car mesh object type", unreal.get_default_object(unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn").generated_class()).get_editor_property("Mesh").get_collision_object_type())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
