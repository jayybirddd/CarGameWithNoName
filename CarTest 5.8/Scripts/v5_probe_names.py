# Tries candidate node names in BP_MenuHUD's graph, logs which ones exist and their pins, then removes the test nodes.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v5_probe_names.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
try:
    bp = unreal.load_asset("/Game/Car/Blueprints/BP_MenuHUD")
    ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(bp))
    cands = ["AddEvent|EventHitBoxClicked", "AddEvent|HUD|EventHitBoxClicked", "AddEvent|HitBoxClicked", "AddEvent|EventReceiveHitBoxClick",
             "Utilities|String|Equal(String)", "Utilities|String|EqualExactly(String)", "Utilities|String|EqualEqual_StrStr", "Utilities|String|Equal",
             "Utilities|Name|Equal(Name)", "Math|Name|Equal(Name)", "Utilities|Operators|Equal(Name)", "Utilities|Name|EqualEqual_NameName",
             "Utilities|String|StringtoName", "Utilities|String|StringToName", "Utilities|Name|StringtoName", "Utilities|String|ToName(String)"]
    made = []
    for i, c in enumerate(cands):
        nd = ed.create_node_from_name(c, unreal.Vector2D(-3000, -3000 - i * 200), [])
        if nd:
            made.append(nd)
            log("OK", c, "|", str(BEL.get_node_title(nd)).splitlines()[0], [str(PL.get_pin_name(p)) for p in BEL.list_all_pins(nd)])
        else:
            log("--", c)
    ed.remove_nodes(made)
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
