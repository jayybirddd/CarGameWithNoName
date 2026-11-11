import unreal, traceback, math
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_analyze1.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
def v(x): return "(%.1f,%.1f,%.1f)" % (x.x, x.y, x.z)
def r(q):
    rr = q.rotator(); return "(p%.1f,y%.1f,r%.1f)" % (rr.pitch, rr.yaw, rr.roll)
APE = unreal.AnimPoseExtensions
try:
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in reg.get_assets_by_path("/Game/Car/Mesh", recursive=True):
        p("asset", ad.package_name, ad.asset_class_path.asset_name)
    m = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    b = m.get_bounds(); p("bounds", v(b.origin), v(b.box_extent))
    p("phys", m.physics_asset)
    sk = m.skeleton
    ref = APE.get_reference_pose(sk)
    names = APE.get_bone_names(ref)
    for n in ["CAR_002","ROOT","DEF-BODY","DEF-FRONT-WHEEL_L","DEF-FRONT-WHEEL_R","DEF-BACK-WHEEL_L","CTRL-STEERING"]:
        t = APE.get_bone_pose(ref, n, unreal.AnimPoseSpaces.WORLD)
        p("ref", n, v(t.translation), r(t.rotation))
    # hierarchy
    for n in names:
        try:
            p("parent", n, "<-", sk.get_editor_property("bone_tree") if False else "")
        except Exception: pass
    opts = unreal.AnimPoseEvaluationOptions()
    def sample(anim, bones, times):
        res = []
        for tm in times:
            pose = APE.get_anim_pose_at_time(anim, tm, opts)
            res.append([APE.get_bone_pose(pose, bn, unreal.AnimPoseSpaces.LOCAL) for bn in bones])
        return res
    cmp_bones = ["DEF-BODY","CTRL-BODY","CTRL-STEERING","MCH-STEER-FRONT-WHEEL_L","DEF-ANTENAE0-002","MASTER-LOCATION"]
    old = {}
    for nm in ["AS_Default","AS_Idle","AS_Acceleration","AS_Deceleration","AS_LeftTurn","AS_RightTurn"]:
        old[nm] = unreal.load_asset("/Game/Car_Rig_and_Anims/Animations/"+nm)
    new = {}
    for ad in reg.get_assets_by_path("/Game/Car/Mesh"):
        if str(ad.asset_class_path.asset_name) == "AnimSequence":
            new[str(ad.asset_name)] = unreal.load_asset(str(ad.package_name))
    for k,a in new.items():
        p("new", k, "len %.3f" % a.get_play_length())
    def dist(a1, a2):
        T = min(a1.get_play_length(), a2.get_play_length())
        times = [T*i/7.0 for i in range(8)]
        s1 = sample(a1, cmp_bones, times); s2 = sample(a2, cmp_bones, times)
        d = 0.0
        for f1,f2 in zip(s1,s2):
            for t1,t2 in zip(f1,f2):
                d += (t1.translation - t2.translation).length()
                q = t1.rotation.inversed() * t2.rotation if hasattr(t1.rotation,'inversed') else None
                r1 = t1.rotation.rotator(); r2 = t2.rotation.rotator()
                d += abs(r1.pitch-r2.pitch)+abs(((r1.yaw-r2.yaw+180)%360)-180)+abs(((r1.roll-r2.roll+180)%360)-180)
        return d + abs(a1.get_play_length()-a2.get_play_length())*100
    for on,oa in old.items():
        ds = sorted((dist(oa, na), nn) for nn,na in new.items())
        p("match", on, "->", ["%s:%.1f" % (nn, d) for d,nn in ds[:3]])
    # motion description of old anims (world space body, root motion check)
    for on,oa in old.items():
        T = oa.get_play_length()
        p("---", on, "len %.2f" % T)
        for i in range(8):
            tm = T*i/7.0
            pose = APE.get_anim_pose_at_time(oa, tm, opts)
            ml = APE.get_bone_pose(pose, "MASTER-LOCATION", unreal.AnimPoseSpaces.WORLD)
            bd = APE.get_bone_pose(pose, "DEF-BODY", unreal.AnimPoseSpaces.WORLD)
            st = APE.get_bone_pose(pose, "CTRL-STEERING", unreal.AnimPoseSpaces.LOCAL)
            fw = APE.get_bone_pose(pose, "DEF-FRONT-WHEEL_L", unreal.AnimPoseSpaces.WORLD)
            bw = APE.get_bone_pose(pose, "DEF-BACK-WHEEL_L", unreal.AnimPoseSpaces.WORLD)
            p(" t%.2f master%s body%s%s steerLocal%s%s fwL%s%s bwL%s" % (tm, v(ml.translation), v(bd.translation), r(bd.rotation), v(st.translation), r(st.rotation), v(fw.translation), r(fw.rotation), r(bw.rotation)))
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_ANALYZE_DONE")
