# Fix: the v2 key mappings and the Moon HUD were only ever in memory, because save_asset skips
# assets that aren't flagged dirty. Re-adds them, then forces the saves.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_fix_input_save.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
IMC = "/Game/Car/Input/IMC_Car"
try:
    imc = unreal.load_asset(IMC)
    def mappings():
        return [(m.get_editor_property("action").get_name(), str(m.get_editor_property("key").get_editor_property("key_name")))
                for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")]
    log("before", mappings())
    have = set(mappings())
    def key(n): k = unreal.Key(); k.set_editor_property("key_name", n); return k
    want = [("IA_Boost", "LeftShift"), ("IA_Boost", "Gamepad_FaceButton_Left"),
            ("IA_ShiftUp", "E"), ("IA_ShiftUp", "Gamepad_RightShoulder"),
            ("IA_ShiftDown", "Q"), ("IA_ShiftDown", "Gamepad_LeftShoulder"),
            ("IA_ToggleTransmission", "T"), ("IA_ToggleTransmission", "Gamepad_DPad_Up")]
    imc.modify()
    for an, kn in want:
        if (an, kn) not in have:
            imc.map_key(unreal.load_asset("/Game/Car/Input/" + an), key(kn)); log("mapped", an, kn)
    log("saved imc", EAL.save_asset(IMC, only_if_is_dirty=False))
    log("after", mappings())

    gm = "/Game/Car/Blueprints/BP_CarGameMode_Moon"
    b = unreal.load_asset(gm)
    hud = unreal.load_asset("/Game/Car/Blueprints/BP_CarHUD")
    cdo = unreal.get_default_object(b.generated_class())
    cdo.modify()
    cdo.set_editor_property("hud_class", hud.generated_class())
    BEL.compile_blueprint(b)
    log("saved moon gm", EAL.save_asset(gm, only_if_is_dirty=False))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_FIX_INPUT_SAVE_DONE")
