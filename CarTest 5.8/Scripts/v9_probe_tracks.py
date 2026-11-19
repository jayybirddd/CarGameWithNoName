# Reports each track actor's scale in the open level, its mesh bounds at scale 1, and the road width measured with
# traces across the road (in cm at the actor's current scale and per unit scale). Read-only.
import unreal, traceback, math
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_probe_tracks.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def hit_on(w, actor, x, y, z0, z1):
    r = unreal.SystemLibrary.line_trace_multi(w, unreal.Vector(x, y, z0), unreal.Vector(x, y, z1), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[-1] if isinstance(r[-1], list) else r[0]
    zs = [h.to_tuple()[4].z for h in (r or []) if h.to_tuple()[9] == actor]
    return zs
try:
    w = UES.get_editor_world(); log("level", w.get_path_name())
    for a in EAS.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        sm = a.static_mesh_component.get_editor_property("static_mesh")
        if not sm or "rack" not in sm.get_name(): continue
        o, e = a.get_actor_bounds(False); b = sm.get_bounds()
        sc = a.get_actor_scale3d()
        log("TRACK", a.get_actor_label(), sm.get_name(), "scale", "%.3f %.3f %.3f" % (sc.x, sc.y, sc.z), "loc", a.get_actor_location(), "rot", a.get_actor_rotation(),
            "mesh ext %.0f %.0f %.0f" % (b.box_extent.x, b.box_extent.y, b.box_extent.z), "world ext %.0f %.0f %.0f" % (e.x, e.y, e.z))
        # find road widths: along a grid of columns, find road hits; then for a few, scan across in x and y to measure the run
        widths = []
        for i in range(-6, 7):
            for j in range(-6, 7):
                x, y = o.x + e.x * i / 7, o.y + e.y * j / 7
                zs = hit_on(w, a, x, y, o.z + e.z + 500, o.z - e.z - 500)
                if not zs: continue
                z = max(zs)
                for dx, dy in ((1, 0), (0, 1)):
                    run = []
                    for s in range(-80, 81):
                        q = hit_on(w, a, x + dx * s * 50, y + dy * s * 50, z + 300, z - 300)
                        run.append(bool(q) and abs(max(q) - z) < 80)
                    # contiguous run through the centre
                    c = 80; l = c; r_ = c
                    while l > 0 and run[l - 1]: l -= 1
                    while r_ < 160 and run[r_ + 1]: r_ += 1
                    if run[c]: widths.append((r_ - l + 1) * 50)
        widths.sort()
        if widths:
            med = widths[len(widths) // 4]   # lower quartile: cross-cuts along the road read long, across it read the true width
            log("   road width samples", len(widths), "lower-quartile %d cm" % med, "min %d" % widths[0], "-> per unit scale %.0f cm" % (med / sc.x))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
