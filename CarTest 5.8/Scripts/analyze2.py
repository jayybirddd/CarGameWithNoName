import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_analyze2.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
def v(x): return "(%.1f,%.1f,%.1f)" % (x.x, x.y, x.z)
def r(q):
    rr = q.rotator(); return "(p%.1f,y%.1f,r%.1f)" % (rr.pitch, rr.yaw, rr.roll)
APE = unreal.AnimPoseExtensions
try:
    m = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    try:
        mod = unreal.SkeletonModifier()
        mod.set_skeletal_mesh(m)
        for n in mod.get_all_bone_names():
            p("parent", n, "<-", mod.get_parent_name(n))
    except Exception as e:
        p("modifier err", e)
    ref = APE.get_reference_pose(m.skeleton)
    names = APE.get_bone_names(ref)
    opts = unreal.AnimPoseEvaluationOptions()
    A = {"Default":"SK_CarCAR_ArmatureAction","Idle":"SK_CarCAR_ArmatureAction_002","Accel":"SK_CarCAR_ArmatureAction_003",
         "Decel":"SK_CarCAR_ArmatureAction_004","Left":"SK_CarCAR_ArmatureAction_005","Right":"SK_CarCAR_ArmatureAction_006"}
    for k, an in A.items():
        a = unreal.load_asset("/Game/Car/Mesh/"+an)
        T = a.get_play_length()
        for tm in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.5, T]:
            if tm > T: continue
            pose = APE.get_anim_pose_at_time(a, tm, opts)
            out = []
            for n in names:
                t = APE.get_bone_pose(pose, n, unreal.AnimPoseSpaces.LOCAL)
                t0 = APE.get_bone_pose(ref, n, unreal.AnimPoseSpaces.LOCAL)
                dt = (t.translation - t0.translation).length()
                r1 = t.rotation.rotator(); r0 = t0.rotation.rotator()
                dr = max(abs(((r1.pitch-r0.pitch+180)%360)-180), abs(((r1.yaw-r0.yaw+180)%360)-180), abs(((r1.roll-r0.roll+180)%360)-180))
                if dt > 0.3 or dr > 0.5:
                    out.append("%s dT%s R%s" % (n, v(t.translation - t0.translation), r(t.rotation)))
            p(k, "t%.2f" % tm, " | ".join(out))
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_ANALYZE2_DONE")
