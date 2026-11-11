import unreal
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_bones2.txt"
L = []
APE = unreal.AnimPoseExtensions
m = unreal.load_asset("/Game/Car/Mesh/SK_Car")
ref = APE.get_reference_pose(m.skeleton)
for n in ["CAR", "ROOT", "MASTER-LOCATION", "MASTER-ROTATION", "DEF-BODY", "DEF-FRONT-WHEEL_L", "DEF-BACK-WHEEL_R"]:
    for sp in (unreal.AnimPoseSpaces.WORLD, unreal.AnimPoseSpaces.LOCAL):
        t = APE.get_bone_pose(ref, n, sp)
        r = t.rotation.rotator()
        L.append("%s %s loc(%.2f,%.2f,%.2f) rot(p%.2f,y%.2f,r%.2f) scale(%.3f,%.3f,%.3f)" % (n, "W" if sp == unreal.AnimPoseSpaces.WORLD else "L", t.translation.x, t.translation.y, t.translation.z, r.pitch, r.yaw, r.roll, t.scale3d.x, t.scale3d.y, t.scale3d.z))
with open(OUT, "w") as f: f.write("\n".join(L))
