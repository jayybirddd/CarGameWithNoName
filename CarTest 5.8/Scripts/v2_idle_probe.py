# Samples AS_Idle: which bones move, how far, and how fast the motion repeats.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_idle_probe.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
APE = unreal.AnimPoseExtensions
try:
    a = unreal.load_asset("/Game/Car/Animations/AS_Idle")
    m = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    T = a.get_play_length()
    log("length", T, "rate_scale", a.get_editor_property("rate_scale"))
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    for nd in ag.list_all_nodes():
        if "AS_Idle" in str(unreal.BlueprintEditorLibrary.get_node_title(nd)):
            log("player", nd.get_editor_property("node").export_text()[:300])
    opts = unreal.AnimPoseEvaluationOptions()
    ref = APE.get_reference_pose(m.skeleton)
    names = APE.get_bone_names(ref)
    N = 48
    poses = [APE.get_anim_pose_at_time(a, T * i / N, opts) for i in range(N + 1)]
    S = unreal.AnimPoseSpaces.WORLD
    for n in names:
        tr = [APE.get_bone_pose(p, n, S) for p in poses]
        xs = [t.translation.x for t in tr]; ys = [t.translation.y for t in tr]; zs = [t.translation.z for t in tr]
        ro = [t.rotation.rotator() for t in tr]
        ps = [r.pitch for r in ro]; yw = [r.yaw for r in ro]; rl = [r.roll for r in ro]
        rg = [max(v) - min(v) for v in (xs, ys, zs, ps, yw, rl)]
        if max(rg) > 0.02:
            log("%-28s rngT %.3f %.3f %.3f rngR %.3f %.3f %.3f" % (str(n), *rg))
    for n in names:
        if "ANTENAE0-001" in str(n) or "MASTER" in str(n) or "BODY" in str(n).upper():
            log("track", n)
            for i in range(0, N + 1, 2):
                t = APE.get_bone_pose(poses[i], n, S); r = t.rotation.rotator()
                log("  t%.3f loc %.3f %.3f %.3f rot p%.3f y%.3f r%.3f" % (T * i / N, t.translation.x, t.translation.y, t.translation.z, r.pitch, r.yaw, r.roll))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_IDLE_PROBE_DONE")
