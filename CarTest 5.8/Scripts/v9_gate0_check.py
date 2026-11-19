# Lists every surface (all heights) at and around each level's START / FINISH gate, along the gate's heading.
import unreal, traceback, math
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_gate0_check.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    for lv in ("L_Track1", "L_Track2", "L_Track3"):
        LES.load_level("/Game/Levels/" + lv); w = UES.get_editor_world()
        g0 = [a for a in EAS.get_all_level_actors() if a.get_actor_label() == "Gate_00"][0]
        ps = [a for a in EAS.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"][0]
        p = g0.get_actor_location(); f = g0.get_actor_forward_vector()
        log(lv, "gate0 (%.0f,%.0f,%.0f) yaw %.0f   player start (%.0f,%.0f,%.0f) yaw %.0f" % (p.x, p.y, p.z, g0.get_actor_rotation().yaw, *ps.get_actor_location().to_tuple(), ps.get_actor_rotation().yaw))
        for d in (-2500, -1500, -600, 0, 600, 1500):
            x, y = p.x + f.x * d, p.y + f.y * d
            r = unreal.SystemLibrary.line_trace_multi(w, unreal.Vector(x, y, p.z + 5000), unreal.Vector(x, y, p.z - 5000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            if isinstance(r, tuple): r = r[-1] if isinstance(r[-1], list) else r[0]
            log("   %+5d m along: surfaces z" % (d / 100), [round(h.to_tuple()[4].z) for h in (r or [])])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
