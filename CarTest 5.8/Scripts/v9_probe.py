# Lists every surface along a line (editor world), for finding gaps or drops in a track. Globals: MAP, A, B (x,y), N.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_probe.txt"
L = []
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for i in range(N + 1):
        x = A[0] + (B[0] - A[0]) * i / N; y = A[1] + (B[1] - A[1]) * i / N
        r = unreal.SystemLibrary.line_trace_multi(w, unreal.Vector(x, y, 20000), unreal.Vector(x, y, -20000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
        if isinstance(r, tuple): r = r[-1] if isinstance(r[-1], list) else r[0]
        L.append("(%6.0f,%6.0f) z %s" % (x, y, [(round(h.to_tuple()[4].z), h.to_tuple()[9].get_actor_label() if h.to_tuple()[9] else "?") for h in (r or [])]))
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_class().get_name() in ("PlayerStart",) or a.get_actor_label() in ("Gate_00", "Gate_01", "Track"):
            L.append("%s %s yaw %.0f" % (a.get_actor_label(), a.get_actor_location(), a.get_actor_rotation().yaw))
except Exception:
    L.append(traceback.format_exc())
open(OUT, "w").write("\n".join(L))
