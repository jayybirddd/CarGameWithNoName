# Lists the separated car physics asset's constraints (which bone pairs are joined).
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v7_probe_pa.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
try:
    pa = unreal.load_asset("/Game/Car/SeparatedCar/CAR_separated_PhysicsAsset")
    log("pa methods", [m for m in dir(pa) if not m.startswith("_")])
    for args in ((True,), (False,), ()):
        try:
            cs = pa.get_constraints(*args); log("get_constraints", args, len(cs))
            for c in cs:
                log("  ", c, [m for m in dir(c) if not m.startswith("_")][:30] if c is cs[0] else "")
            break
        except Exception as e: log("get_constraints", args, "ERR", e)
    bones = ["DEF-BODY", "DEF-BASE-ANTENNAE", "DEF-ANTENAE0-001", "DEF-ANTENAE0-002", "DEF-ANTENAE0-003", "DEF-ANTENAE0-004",
             "DEF-FRONT-WHEEL_L", "DEF-FRONT-WHEEL_R", "DEF-BACK-WHEEL_L", "DEF-BACK-WHEEL_R", "MASTER-ROTATION", "ROOT", "Armature_001"]
    for a in bones:
        for b in bones:
            if a < b:
                try:
                    c = pa.get_constraint_by_bone_names(a, b)
                    if c: log("constraint", a, "-", b, c)
                except Exception as e: pass
    log("export", pa.export_text()[:3000] if hasattr(pa, "export_text") else "")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
