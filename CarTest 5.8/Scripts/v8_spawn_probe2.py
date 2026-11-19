# Finds the road surface around the player start (tracing from high above) and how much simple collision each new
# track mesh has. Read-only.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v8_spawn_probe2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def hits(w, a, b):
    out = []
    r = unreal.SystemLibrary.line_trace_multi(w, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[-1] if isinstance(r[-1], list) else r[0]
    for h in (r or []):
        t = h.to_tuple(); out.append((round(t[4].z), t[9].get_name() if t[9] else None, t[0]))
    return out
try:
    w = UES.get_editor_world()
    ps = [a for a in EAS.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"][0]
    p = ps.get_actor_location()
    for dx, dy in ((0, 0), (300, 0), (-300, 0), (0, 300), (0, -300)):
        a = unreal.Vector(p.x + dx, p.y + dy, 20000); b = unreal.Vector(p.x + dx, p.y + dy, -2000)
        log("column", dx, dy, hits(w, a, b))
    for nm in ("NewBigTrack_Flat", "TestTrack_2", "TestTrack"):
        acts = [x for x in EAS.get_all_level_actors() if x.get_actor_label() == nm]
        if not acts: continue
        sm = acts[0].static_mesh_component.get_editor_property("static_mesh")
        bs = sm.get_editor_property("body_setup")
        ag = bs.get_editor_property("agg_geom") if bs else None
        counts = {k: len(ag.get_editor_property(k)) for k in ("box_elems", "sphere_elems", "sphyl_elems", "convex_elems")} if ag else None
        log(nm, sm.get_path_name(), "trace flag", bs.get_editor_property("collision_trace_flag") if bs else None, "simple shapes", counts,
            "tris", sm.get_num_triangles(0) if hasattr(sm, "get_num_triangles") else "?")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
