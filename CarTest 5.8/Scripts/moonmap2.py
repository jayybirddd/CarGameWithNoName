import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_moonmap2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
BP = "/Game/Car/Blueprints/"
ORIG = "/Game/Car/Maps/CarTestTrack"; MOON = "/Game/Car/Maps/CarTestMoonGrav"
try:
    log("project", unreal.Paths.get_project_file_path())
    log("project gravity", unreal.get_default_object(unreal.PhysicsSettings).get_editor_property("default_gravity_z"))
    for p in ["BP_Wheel_Front", "BP_Wheel_Rear", "BP_Wheel_Front_Moon", "BP_Wheel_Rear_Moon"]:
        c = unreal.get_default_object(unreal.load_asset(BP + p).generated_class())
        log(p, c.get_editor_property("spring_rate"), c.get_editor_property("spring_preload"))
    for p in ["BP_CarPawn", "BP_CarPawn_Moon"]:
        for h in SDS.k2_gather_subobject_data_for_blueprint(unreal.load_asset(BP + p)):
            o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
            if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
                log(p, [w.get_editor_property("wheel_class").get_name() for w in o.get_editor_property("wheel_setups")])
    gmm = unreal.load_asset(BP + "BP_CarGameMode_Moon")
    log("moon gm pawn", unreal.get_default_object(gmm.generated_class()).get_editor_property("default_pawn_class").get_name())
    # copy the map via Save As (no second in-memory copy)
    if not EAL.does_asset_exist(MOON):
        if unreal.EditorLevelLibrary.get_editor_world().get_path_name().split(".")[0] != ORIG:
            les.load_level(ORIG)
        w = unreal.EditorLevelLibrary.get_editor_world()
        log("save as", unreal.EditorLoadingAndSavingUtils.save_map(w, MOON))
    w = unreal.EditorLevelLibrary.get_editor_world()
    log("current world", w.get_path_name())
    if w.get_path_name().split(".")[0] == MOON:
        ws = w.get_world_settings()
        ws.set_editor_property("global_gravity_set", True)
        ws.set_editor_property("global_gravity_z", -162.0)
        ws.set_editor_property("default_game_mode", gmm.generated_class())
        les.save_current_level()
        log("moon settings", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), ws.get_editor_property("default_game_mode").get_name())
    log("maps on disk", EAL.does_asset_exist(ORIG), EAL.does_asset_exist(MOON))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
