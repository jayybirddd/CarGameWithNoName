import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_probe_abp.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
try:
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    for nd in ag.list_all_nodes():
        t = str(BEL.get_node_title(nd)).replace("\n", " | ")
        pins = []
        for p in BEL.list_all_pins(nd):
            nm = str(PL.get_pin_name(p))
            try: dv = PL.get_pin_value(p) if hasattr(PL, "get_pin_value") else ""
            except Exception: dv = "?"
            try: lk = [str(BEL.get_node_title(PL.get_owning_node(q))).split("\n")[0] for q in PL.list_connected_pins(p)]
            except Exception as e: lk = "err %s" % e
            pins.append("%s=%s->%s" % (nm, dv, lk))
        log(nd.get_class().get_name(), t, pins)
        if nd.get_class().get_name() == "AnimGraphNode_ModifyBone":
            log("   ", nd.get_editor_property("node").export_text()[:500])
    log("PL api", [x for x in dir(PL) if not x.startswith("_")])
    eg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "EventGraph")
    for nd in eg.list_all_nodes():
        t = str(BEL.get_node_title(nd)).split("\n")[0]
        if t.startswith("Set ") or "Event" in t:
            log("EG", t, BEL.get_node_pos(nd))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
