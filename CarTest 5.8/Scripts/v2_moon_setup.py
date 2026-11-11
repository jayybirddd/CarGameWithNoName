# Moon setup, kept in one place so it can be applied to any map (the planned boost-pickup scene included).
# What "Moon" means for a map:
#   - World Settings: gravity override on, GlobalGravityZ = -162 (1/6 of Earth's -980)
#   - World Settings: GameMode override = BP_CarGameMode_Moon  (spawns BP_CarPawn_Moon, uses BP_CarHUD)
#   - BP_CarPawn_Moon: AirStabilize = 0.6, so a released key in the air bleeds off the pitch spin (long Moon jumps
#     otherwise keep rotating). The regular BP_CarPawn keeps 0 = off; set it per car in Class Defaults to toggle.
# BP_CarPawn_Moon is a child of BP_CarPawn, so all car logic (boost, gears, air pitch, antenna) is inherited;
# it only swaps in BP_Wheel_*_Moon (spring rate 45 / preload 9 instead of 250 / 50) and its own movement
# component copy, which is why the transmission/engine must be re-synced whenever BP_CarPawn's gears change.
#
# Usage from the editor console (CHECK only reports; APPLY changes and saves the map):
#   py exec(open('D:/PersonalGameFiles/CarTest 5.8/Scripts/v2_moon_setup.py').read())
# with MODE / MAPS set below. A new scene can be made by duplicating an existing map with NEW_SCENE (off by default).
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_setup.txt"
MODE = "CHECK"            # "CHECK" or "APPLY"
MAPS = ["/Game/Levels/L_MoonTestTrack", "/Game/Levels/L_EarthTestTrack"]
NEW_SCENE = None          # e.g. ("/Game/Levels/L_MoonTestTrack", "/Game/Levels/L_MoonBoostPickups") to duplicate first
MOON_GRAVITY_Z = -162.0
MOON_GM = "/Game/Car/Blueprints/BP_CarGameMode_Moon"
MOON_AIR_STABILIZE = 0.6
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
EAL = unreal.EditorAssetLibrary
L = []
def log(*a): L.append(" ".join(str(x) for x in a))

def movement(bp):
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent): return o

def check_car_sync(fix):
    base = movement(unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn"))
    moon_bp = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn_Moon"); moon = movement(moon_bp)
    ok = True
    for p in ("transmission_setup", "engine_setup"):
        same = base.get_editor_property(p).export_text() == moon.get_editor_property(p).export_text()
        log("moon car", p, "matches base" if same else "DIFFERS from base")
        if not same:
            ok = False
            if fix: moon.set_editor_property(p, base.get_editor_property(p))
    for nm in ("BP_CarPawn", "BP_CarPawn_Moon"):
        log(nm, "AirStabilize", unreal.get_default_object(unreal.load_asset("/Game/Car/Blueprints/" + nm).generated_class()).get_editor_property("AirStabilize"))
    cdo = unreal.get_default_object(moon_bp.generated_class())
    if abs(cdo.get_editor_property("AirStabilize") - MOON_AIR_STABILIZE) > 0.001:
        ok = False
        if fix:
            cdo.modify(); cdo.set_editor_property("AirStabilize", MOON_AIR_STABILIZE)
            log("moon car AirStabilize ->", MOON_AIR_STABILIZE)
    if fix and not ok:
        unreal.BlueprintEditorLibrary.compile_blueprint(moon_bp)
        log("saved moon car", EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn_Moon", only_if_is_dirty=False))

def moon_map(path, fix):
    w = unreal.load_asset(path)
    if w is None: log("missing map", path); return
    ws = w.get_world_settings()
    gm = ws.get_editor_property("default_game_mode")
    is_moon = ws.get_editor_property("global_gravity_set") and abs(ws.get_editor_property("global_gravity_z") - MOON_GRAVITY_Z) < 0.01 and gm is not None and gm.get_name() == "BP_CarGameMode_Moon_C"
    log(path, "gravity override", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"),
        "gm", gm.get_name() if gm else None, "=> moon" if is_moon else "=> not moon")
    if fix and not is_moon:
        ws.modify()
        ws.set_editor_property("global_gravity_set", True)
        ws.set_editor_property("global_gravity_z", MOON_GRAVITY_Z)
        ws.set_editor_property("default_game_mode", unreal.load_asset(MOON_GM).generated_class())
        log("saved", path, EAL.save_loaded_asset(w, False))

try:
    log("mode", MODE)
    maps = list(MAPS)
    if NEW_SCENE and MODE == "APPLY":
        src, dst = NEW_SCENE
        if EAL.does_asset_exist(dst): log("new scene already exists, not overwriting", dst)
        else: log("duplicated", src, "->", dst, EAL.duplicate_asset(src, dst) is not None)
        maps.append(dst)
    check_car_sync(MODE == "APPLY")
    for m in maps:
        moon_map(m, MODE == "APPLY" and m != "/Game/Levels/L_EarthTestTrack")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_MOON_SETUP_DONE")
