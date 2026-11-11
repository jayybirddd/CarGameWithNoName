import unreal, traceback
L = []
try:
    imc = unreal.load_asset("/Game/Car/Input/IMC_Car")
    L.append("mappings " + str([(m.get_editor_property("action").get_name(), str(m.get_editor_property("key").get_editor_property("key_name"))) for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings") if m.get_editor_property("action").get_name() in ("IA_Boost", "IA_ShiftUp", "IA_ShiftDown", "IA_ToggleTransmission")]))
    for gm in ("/Game/Car/Blueprints/BP_CarGameMode", "/Game/Car/Blueprints/BP_CarGameMode_Moon"):
        b = unreal.load_asset(gm)
        c = unreal.get_default_object(b.generated_class())
        L.append("%s parent %s hud %s" % (gm, b.generated_class().get_super_class().get_name() if hasattr(b.generated_class(), "get_super_class") else "?", c.get_editor_property("hud_class")))
except Exception:
    L.append(traceback.format_exc())
open("D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_verify_disk.txt", "w").write("\n".join(L))
