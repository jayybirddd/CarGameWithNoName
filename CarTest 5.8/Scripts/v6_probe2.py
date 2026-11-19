# Dumps the car graph around the handbrake and steering inputs, and the full wheel settings.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_probe2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
def t(nd): return str(BEL.get_node_title(nd)).splitlines()[0]
try:
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(car))
    nodes = ed.list_all_nodes()
    for nd in nodes:
        tt = t(nd)
        if any(k in tt for k in ("IA_Handbrake", "IA_Steer", "SetHandbrakeInput", "SetSteeringInput", "IA_Reset", "IA_Throttle", "IA_Brake")):
            p = BEL.get_node_pos(nd)
            links = []
            for pin in BEL.list_all_pins(nd):
                for q in PL.list_connected_pins(pin):
                    owner = PL.get_owning_node(q) if hasattr(PL, "get_owning_node") else None
                    links.append("%s->%s" % (PL.get_pin_name(pin), t(owner) if owner else "?"))
            vals = {str(PL.get_pin_name(pin)): str(PL.get_pin_value(pin)) for pin in BEL.list_all_pins(nd) if hasattr(PL, "get_pin_value") and PL.get_pin_direction(pin) == unreal.EdGraphPinDirection.EGPD_INPUT}
            log("NODE", tt, "pos", p.x, p.y, "links", links, "vals", vals)
    log("PL methods", [m for m in dir(PL) if not m.startswith("_")])
    for w in ("BP_Wheel_Front", "BP_Wheel_Rear"):
        cdo = unreal.get_default_object(unreal.load_asset("/Game/Car/Blueprints/" + w).generated_class())
        log(w, cdo.export_text() if hasattr(cdo, "export_text") else "")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
