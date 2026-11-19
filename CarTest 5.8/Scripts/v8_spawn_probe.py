# Reports the open level's spawn setup: game mode, player starts (and what they overlap), the track pieces, and the
# project's default game mode / maps. Read-only.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v8_spawn_probe.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    w = UES.get_editor_world()
    log("level", w.get_path_name())
    ws = w.get_world_settings()
    gm = ws.get_editor_property("default_game_mode")
    log("gm override", gm.get_name() if gm else None, "gravity", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"))
    gms = unreal.get_default_object(unreal.GameMapsSettings)
    for k in ("global_default_game_mode", "game_default_map", "editor_startup_map"):
        try: log("project", k, gms.get_editor_property(k))
        except Exception as e: log("project", k, "ERR", e)
    acts = EAS.get_all_level_actors()
    for a in acts:
        cls = a.get_class().get_name()
        o, e = a.get_actor_bounds(False)
        if cls in ("PlayerStart",) or "Pawn" in cls or "Car" in cls:
            log("SPAWN", a.get_actor_label(), cls, "loc", a.get_actor_location(), "rot", a.get_actor_rotation())
            p = a.get_actor_location()
            for d in (unreal.Vector(0, 0, -5000), unreal.Vector(0, 0, 5000)):
                r = unreal.SystemLibrary.line_trace_single(w, p, p + d, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [a], unreal.DrawDebugTrace.NONE, True)
                if isinstance(r, tuple): r = r[0] if isinstance(r[0], unreal.HitResult) else r[-1]
                t = r.to_tuple() if r else None
                log("   trace", "down" if d.z < 0 else "up", "hit" if t and t[0] else "none", (t[4], t[9].get_name() if t[9] else None) if t and t[0] else "")
            ov = unreal.SystemLibrary.sphere_overlap_actors(w, p, 120.0, [], None, [a])
            if isinstance(ov, tuple): ov = ov[-1]
            log("   overlapping within 1.2 m:", [x.get_actor_label() for x in (ov or [])])
    for a in acts:
        if isinstance(a, unreal.StaticMeshActor):
            sm = a.static_mesh_component.get_editor_property("static_mesh")
            nm = sm.get_name() if sm else None
            if nm and ("Track" in nm or "track" in nm):
                o, e = a.get_actor_bounds(False)
                bs = sm.get_editor_property("body_setup")
                log("TRACK", a.get_actor_label(), nm, "center (%.0f,%.0f,%.0f) ext (%.0f,%.0f,%.0f)" % (o.x, o.y, o.z, e.x, e.y, e.z),
                    "collision", a.static_mesh_component.get_collision_profile_name(), a.static_mesh_component.get_collision_enabled(),
                    "trace flag", bs.get_editor_property("collision_trace_flag") if bs else None)
    log("actor count", len(acts), sorted(set(a.get_class().get_name() for a in acts)))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
