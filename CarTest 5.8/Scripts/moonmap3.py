import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_moonmap3.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
MOON = "/Game/Car/Maps/CarTestMoonGrav"
try:
    gmm = unreal.load_asset("/Game/Car/Blueprints/BP_CarGameMode_Moon")
    w = unreal.load_asset(MOON)
    log("loaded", w.get_path_name(), "editor world", unreal.EditorLevelLibrary.get_editor_world().get_path_name())
    ws = w.get_world_settings()
    ws.set_editor_property("global_gravity_set", True)
    ws.set_editor_property("global_gravity_z", -162.0)
    ws.set_editor_property("default_game_mode", gmm.generated_class())
    ws.modify()
    log("save", EAL.save_loaded_asset(w, False))
    log("moon", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), ws.get_editor_property("default_game_mode").get_name())
    ows = unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    log("orig", ows.get_editor_property("global_gravity_set"), ows.get_editor_property("global_gravity_z"), ows.get_editor_property("default_game_mode").get_name())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
