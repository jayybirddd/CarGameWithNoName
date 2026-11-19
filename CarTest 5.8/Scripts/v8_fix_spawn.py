# Fixes the car not spawning on L_EarthTestTrack after new tracks were added:
#  1. NewBigTrack_Flat / TestTrack_2 had only an auto-generated convex hull as collision (one shell around the whole
#     track), so the player start sat inside solid collision and the spawn was refused. They now use the road mesh
#     itself as collision ("Use Complex Collision As Simple"), like TestTrack.
#  2. The player start wasn't above any road; it moves to the nearest road point on NewBigTrack_Flat, pointed along it.
import unreal, traceback, math
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v8_fix_spawn.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
TRACKS = ["/Game/Environment/Track/NewBigTrack_Flat", "/Game/Environment/Track/TestTrack_2"]
START_TRACK = "NewBigTrack_Flat"
def road_hit(w, x, y, actor, ztop, zbot):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, ztop), unreal.Vector(x, y, zbot), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[0] if isinstance(r[0], unreal.HitResult) else r[-1]
    if r is None: return None
    t = r.to_tuple()
    return t[4] if t[0] and t[9] == actor else None
try:
    for path in TRACKS:
        sm = unreal.load_asset(path)
        bs = sm.get_editor_property("body_setup")
        bs.modify()
        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        sm.modify()
        log(path, "trace flag now", bs.get_editor_property("collision_trace_flag"), "saved", unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False))
    w = UES.get_editor_world()
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.get_actor_label() in ("NewBigTrack_Flat", "TestTrack_2"):
            c = a.static_mesh_component; c.recreate_physics_state() if hasattr(c, "recreate_physics_state") else None
            a.set_actor_location(a.get_actor_location(), False, False)   # re-register so the new collision applies in the editor
    trk = [a for a in EAS.get_all_level_actors() if a.get_actor_label() == START_TRACK][0]
    ps = [a for a in EAS.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"][0]
    p = ps.get_actor_location(); o, e = trk.get_actor_bounds(False)
    zt, zb = o.z + e.z + 500, o.z - e.z - 500
    best = None
    for r_ in range(0, 6000, 150):                 # spiral out from the chosen spot until the road is found
        for k in range(max(1, int(2 * math.pi * r_ / 150))):
            ang = 2 * math.pi * k / max(1, int(2 * math.pi * r_ / 150))
            h = road_hit(w, p.x + math.cos(ang) * r_, p.y + math.sin(ang) * r_, trk, zt, zb)
            if h is not None: best = h; break
        if best is not None: break
    if best is None:
        log("!! no road on", START_TRACK, "within 60 m of the player start; left it where it is")
    else:
        # point along the road: the heading with the longest run of road ahead
        runs = []
        for k in range(36):
            ang = math.radians(k * 10); n = 0
            for s in range(1, 10):
                if road_hit(w, best.x + math.cos(ang) * s * 250, best.y + math.sin(ang) * s * 250, trk, best.z + 600, best.z - 600) is None: break
                n += 1
            runs.append((n, k * 10))
        yaw = max(runs)[1]
        old = (p.x, p.y, p.z)
        ps.set_actor_location_and_rotation(unreal.Vector(best.x, best.y, best.z + 100), unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(yaw)), False, True)
        log("player start moved from (%.0f,%.0f,%.0f) to (%.0f,%.0f,%.0f) yaw %d, road at z %.0f" % (old + (best.x, best.y, best.z + 100, yaw, best.z)))
        r = unreal.SystemLibrary.sphere_overlap_actors(w, ps.get_actor_location(), 60.0, [], None, [ps])
        if isinstance(r, tuple): r = r[-1]
        log("overlaps at new start (60 cm):", [x.get_actor_label() for x in (r or [])])
    log("saved level", LES.save_current_level())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
