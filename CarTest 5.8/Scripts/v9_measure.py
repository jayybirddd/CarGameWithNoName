# Walks each track in the open level and reports lap length and road width (at the actor's scale and per unit scale).
import unreal, traceback, sys, importlib, time
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gtrack; importlib.reload(gtrack)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_measure.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    w = UES.get_editor_world()
    for lb in ("TestTrack", "NewBigTrack_Flat", "TestTrack_2"):
        a = [x for x in EAS.get_all_level_actors() if x.get_actor_label() == lb][0]
        t0 = time.time()
        p, hx, hy = gtrack.find_start(w, a)
        pts, length = gtrack.walk(w, a, p, hx, hy, log=log)
        ws = sorted(pt[5] for pt in pts)
        sc = a.get_actor_scale3d().x
        med = ws[len(ws) // 2] if ws else 0
        closed = pts and abs(pts[-1][0] - p.x) + abs(pts[-1][1] - p.y) < gtrack.STEP * 3
        log(lb, "scale %.3f" % sc, "steps", len(pts), "lap %.0f m" % (length / 100), "closed" if closed else "NOT CLOSED",
            "width median %.0f cm (p10 %.0f, p90 %.0f)" % (med, ws[len(ws) // 10], ws[len(ws) * 9 // 10]) if ws else "", "-> per unit scale %.0f cm" % (med / sc),
            "took %.0fs" % (time.time() - t0))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
