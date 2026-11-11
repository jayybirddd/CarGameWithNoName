# v3: places boost pads, land mines and a BP_LevelRules in the test maps, and builds the no-recharge scene.
# Re-runnable: removes the actors it placed before (labels BoostPad_*, LandMine_*, LevelRules) and places them again.
# The no-recharge levels (L_MoonBoostCharge, L_EarthBoostCharge) are copies of the matching test track made the first time; later runs just refresh them.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v3_levels.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = "/Game/Car/Placeholders/"
PAD = unreal.load_asset(P + "BP_BoostPad").generated_class()
MINE = unreal.load_asset(P + "BP_LandMine").generated_class()
RULES = unreal.load_asset(P + "BP_LevelRules").generated_class()
FINISH = unreal.load_asset(P + "BP_FinishLine").generated_class()
FINISH_AHEAD = 11000   # cm in front of the start, past the pads, mines and the first ramp
NEXT = {"L_EarthTestTrack": "L_MoonTestTrack", "L_MoonTestTrack": "L_EarthBoostCharge", "L_EarthBoostCharge": "L_MoonBoostCharge"}
TRACK, MOON, CHARGE = "/Game/Levels/L_EarthTestTrack", "/Game/Levels/L_MoonTestTrack", "/Game/Levels/L_MoonBoostCharge"
EARTH_CHARGE = "/Game/Levels/L_EarthBoostCharge"
MINE_EVERY_MAP = [(2400, 0), (2400, 450), (2400, -450), (5200, 700), (5200, -700)]   # (metres ahead x100, sideways) from the start
PADS_EVERY_MAP = [(1200, 0), (3000, 0), (1200, 1500), (1200, -1500)]

def actors(): return EAS.get_all_level_actors()

def setup(path, pads, mines, rules):
    log("== load", path, LES.load_level(path))
    for a in actors():
        lb = a.get_actor_label()
        if lb.startswith("BoostPad_") or lb.startswith("LandMine_") or lb in ("LevelRules", "FinishLine"): EAS.destroy_actor(a)
    start = [a for a in actors() if a.get_class().get_name() == "PlayerStart"][0]
    s0 = start.get_actor_location(); fwd = start.get_actor_forward_vector(); right = start.get_actor_right_vector()
    floor = [a for a in actors() if a.get_actor_label() == "Floor"]
    ztop = 0.0
    if floor:
        o, e = floor[0].get_actor_bounds(False); ztop = o.z + e.z
    blockers = []
    for a in actors():
        lb = a.get_actor_label()
        if lb.startswith("Ramp") or lb.startswith("Bump"):
            o, e = a.get_actor_bounds(False); blockers.append((lb, o, e))
    def free(p, pad=320.0):
        for lb, o, e in blockers:
            if abs(p.x - o.x) < e.x + pad and abs(p.y - o.y) < e.y + pad: return lb
        return None
    yaw = start.get_actor_rotation().yaw
    def place(cls, label, ahead, side):
        p = unreal.Vector(s0.x + fwd.x * ahead + right.x * side, s0.y + fwd.y * ahead + right.y * side, ztop)
        for _ in range(6):
            hit = free(p)
            if not hit: break
            p = unreal.Vector(p.x + right.x * 500, p.y + right.y * 500, p.z)
        a = EAS.spawn_actor_from_class(cls, p, unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        a.set_actor_label(label)
        log("placed", label, "(%.0f, %.0f, %.0f)" % (p.x, p.y, p.z), "moved off " + hit if hit else "")
        return a
    for i, (ah, sd) in enumerate(pads): place(PAD, "BoostPad_%d" % i, ah, sd)
    for i, (ah, sd) in enumerate(mines): place(MINE, "LandMine_%d" % i, ah, sd)
    place(FINISH, "FinishLine", FINISH_AHEAD, 0)
    rules = dict(rules, NextLevel=NEXT.get(path.split("/")[-1], "None"))
    r = EAS.spawn_actor_from_class(RULES, unreal.Vector(s0.x - fwd.x * 400, s0.y - fwd.y * 400, ztop), unreal.Rotator())
    r.set_actor_label("LevelRules")
    for k, v in rules.items(): r.set_editor_property(k, unreal.Name(v) if k == "NextLevel" else v)
    log("rules", {k: r.get_editor_property(k) for k in rules})
    log("saved", LES.save_current_level())
    return floor[0] if floor else None

try:
    setup(TRACK, PADS_EVERY_MAP, MINE_EVERY_MAP, {"BoostRegenEnabled": True, "PadsChargeMeter": False, "StartingLives": 3, "StartingBoost": 1.0})
    setup(MOON, PADS_EVERY_MAP, MINE_EVERY_MAP, {"BoostRegenEnabled": True, "PadsChargeMeter": False, "StartingLives": 3, "StartingBoost": 1.0})
    # no-recharge levels: pads refill the meter; more pads, bigger floor (the copied floor ends 300 m out).
    # Made with Save As from the matching test track the first time (duplicating a map asset from Python while
    # maps are loading leaves a stray world in memory and the editor aborts on the next map load).
    import os
    pads = PADS_EVERY_MAP + [(4800, 0), (6600, 0), (8400, 0), (2400, 3000), (2400, -3000), (6000, 3000), (6000, -3000), (9000, 1800), (9000, -1800)]
    UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    for path, source in ((CHARGE, MOON), (EARTH_CHARGE, TRACK)):
        if not os.path.exists("D:/PersonalGameFiles/CarTest 5.8/Content" + path[len("/Game"):] + ".umap"):
            log("== create", path, "from", source, LES.load_level(source), unreal.EditorLoadingAndSavingUtils.save_map(UES.get_editor_world(), path))
        floor = setup(path, pads, MINE_EVERY_MAP, {"BoostRegenEnabled": False, "PadsChargeMeter": True, "StartingLives": 3, "StartingBoost": 0.3})
        if floor:
            sc = floor.get_actor_scale3d(); fo, fe = floor.get_actor_bounds(False)
            if fe.x < 60000:   # copied floor is 600 m across; make this one 1.8 km
                floor.set_actor_scale3d(unreal.Vector(sc.x * 3, sc.y * 3, sc.z)); log("floor scaled", floor.get_actor_scale3d())
            log("saved", LES.save_current_level())
        ws = UES.get_editor_world().get_world_settings()
        log(path, "gravity", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), "gm", ws.get_editor_property("default_game_mode").get_name())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V3_LEVELS_DONE")
