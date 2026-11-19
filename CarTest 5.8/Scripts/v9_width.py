# Road width per track: at many road points, the shortest crossing over all directions (a crossing ends where the
# surface stops or jumps by more than 60 cm between 40 cm samples, i.e. a wall or edge). Reports per-unit-scale widths
# and the scale each track needs to match TestTrack's road width at its scale in this level. Read-only.
import unreal, traceback, sys, importlib, math, random
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gtrack; importlib.reload(gtrack)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_width.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def run(w, a, x, y, z, ang, sgn):
    d, zp = 0.0, z
    while d < 6000:
        q = gtrack.road_z(w, a, x + math.cos(ang) * sgn * (d + 40), y + math.sin(ang) * sgn * (d + 40), zp, 150.0)
        if q is None or abs(q - zp) > 60: break
        d += 40; zp = q
    return d
try:
    w = UES.get_editor_world(); random.seed(3)
    res = {}
    for lb in ("TestTrack", "NewBigTrack_Flat", "TestTrack_2"):
        a = [x for x in EAS.get_all_level_actors() if x.get_actor_label() == lb][0]
        o, e = a.get_actor_bounds(False); sc = a.get_actor_scale3d().x
        widths = []; tries = 0
        while len(widths) < 30 and tries < 3000:
            tries += 1
            x, y = o.x + random.uniform(-e.x, e.x), o.y + random.uniform(-e.y, e.y)
            zs = gtrack._hits(w, a, x, y, o.z + e.z + 500, o.z - e.z - 500)
            if not zs: continue
            z = max(zs)
            best = min(run(w, a, x, y, z, math.radians(k * 10), 1) + run(w, a, x, y, z, math.radians(k * 10), -1) for k in range(18))
            if best >= 200: widths.append(best)     # skip wall tops / rims
        widths.sort()
        med = widths[len(widths) // 2]
        res[lb] = (med / sc, sc)
        log(lb, "scale %.3f" % sc, "samples", len(widths), "width median %.0f cm (p25 %.0f, p75 %.0f)" % (med, widths[len(widths) // 4], widths[len(widths) * 3 // 4]), "per unit scale %.0f cm" % (med / sc))
    target = res["TestTrack"][0] * res["TestTrack"][1]
    for lb, (wu, sc) in res.items():
        log("to match TestTrack's %.0f cm road:" % target, lb, "scale %.2f" % (target / wu))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
