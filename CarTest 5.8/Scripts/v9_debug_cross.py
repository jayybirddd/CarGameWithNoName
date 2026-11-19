# Debug: road heights straight across each track at its start point, every 40 cm out to 25 m each side.
import unreal, traceback, sys, importlib, math
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gtrack; importlib.reload(gtrack)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_debug_cross.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    w = UES.get_editor_world()
    for lb in ("TestTrack", "NewBigTrack_Flat", "TestTrack_2"):
        a = [x for x in EAS.get_all_level_actors() if x.get_actor_label() == lb][0]
        p, hx, hy = gtrack.find_start(w, a)
        log(lb, "start", "(%.0f,%.0f,%.0f)" % (p.x, p.y, p.z), "heading %.2f %.2f" % (hx, hy))
        rx, ry = -hy, hx
        row = []
        for s in range(-60, 61, 2):
            d = s * 40
            zs = gtrack._hits(w, a, p.x + rx * d, p.y + ry * d, p.z + 3000, p.z - 3000)
            row.append("%d:%s" % (d, ",".join("%.0f" % (z - p.z) for z in zs) if zs else "-"))
        log("   across:", " ".join(row))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
