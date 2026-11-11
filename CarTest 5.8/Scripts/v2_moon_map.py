# Opens the Moon map in the editor and reports its settings, actors, and which wheel classes each car uses.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_map.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
try:
    for nm in ("BP_CarPawn", "BP_CarPawn_Moon"):
        bp = unreal.load_asset("/Game/Car/Blueprints/" + nm)
        for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
            o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
            if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
                log(nm, "wheels", [w.get_editor_property("wheel_class").get_name() for w in o.get_editor_property("wheel_setups")])
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log("load", les.load_level("/Game/Car/Maps/CarTestMoonGrav"))
    w = unreal.EditorLevelLibrary.get_editor_world(); ws = w.get_world_settings()
    log("world", w.get_path_name(), "gravity override", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"),
        "gm", ws.get_editor_property("default_game_mode").get_name())
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        loc = a.get_actor_location(); o, e = a.get_actor_bounds(False)
        log("actor", a.get_actor_label(), a.get_class().get_name(), "loc (%.0f,%.0f,%.0f)" % (loc.x, loc.y, loc.z), "ext (%.0f,%.0f,%.0f)" % (e.x, e.y, e.z),
            "rot", a.get_actor_rotation())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_MOON_MAP_DONE")
