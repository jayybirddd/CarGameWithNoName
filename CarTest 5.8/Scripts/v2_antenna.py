# v2: antenna reacts to the car's motion.
# EventGraph: damped spring driven by the car's local acceleration (+ a little speed drag) -> AntRot0-3 / AntOff1-3.
# AnimGraph: one Transform(Modify)Bone per antenna segment (component space, additive rotation + offset).
# Re-runnable: removes event-graph nodes at y >= 1400 and all ModifyBone nodes first.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_antenna.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
PL = unreal.BlueprintGraphPinLibrary
ABP = "/Game/Car/Blueprints/ABP_CarBody"
SEGS = ["DEF-ANTENAE0-001", "DEF-ANTENAE0-002", "DEF-ANTENAE0-003", "DEF-ANTENAE0-004"]
# tuning (degrees of total tip bend)
GAIN = 0.0183     # per cm/s^2 of forward/back acceleration
GAIN_Y = 0.0317   # per cm/s^2 of sideways acceleration (stronger: the baked turn anims lean the antenna inward)
DRAG = 0.125      # per km/h of forward speed (sweeps back at speed)
MAXB = 60.0
K, C = 204.0, 7.0  # spring stiffness / damping  (~2.3 Hz, settles in about one wobble)
SIGN_P, SIGN_R = -1.0, 1.0
SEG = 14.78     # antenna segment length (cm)
ACC_SMOOTH = 9.0  # acceleration low-pass speed (higher = snappier, noisier)
BODY_BONE = "DEF-BODY"
IDLE_ROLL = 1.2  # degrees of tip bend per degree the body rocks away from its average (idle engine shake)
IDLE_BOUNCE = 0.6 # degrees of tip bend per cm the body bounces away from its average
IDLE_MAX = 8.0
IDLE_FADE = 30.0  # km/h at which the idle shake has fully faded (driving feel stays as tuned)
BODY_SMOOTH = 1.5 # how fast the "average" body pose follows (lower = only slow drift is ignored)
try:
    abp = unreal.load_asset(ABP)
    have = [str(x) for x in BEL.list_member_variable_names(abp)]
    vec = BEL.get_struct_type(unreal.Vector.static_struct())
    rot = BEL.get_struct_type(unreal.Rotator.static_struct())
    for nm, tp in (("AntBend", vec), ("AntBendVel", vec), ("PrevVel", vec), ("AccSmooth", vec), ("BodySmooth", vec), ("AntRot0", rot), ("AntRot1", rot), ("AntRot2", rot), ("AntRot3", rot), ("AntOff1", vec), ("AntOff2", vec), ("AntOff3", vec)):
        if nm not in have: BEL.add_member_variable(abp, nm, tp)
    BEL.compile_blueprint(abp)

    # ============ EventGraph
    ed = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "EventGraph")
    def pos(nd): p = BEL.get_node_pos(nd); return (p.x, p.y)
    def title(nd): return str(BEL.get_node_title(nd)).split("\n")[0]
    old = [nd for nd in ed.list_all_nodes() if pos(nd)[1] >= 1400]
    ed.remove_nodes(old); log("removed", len(old))
    g = gh.G(ed, log)
    def n(names, x, y, cls=None):
        if isinstance(names, str): names = [names]
        for nm in names:
            nd = ed.create_node_from_name(nm, unreal.Vector2D(x, y), [], cls) if cls else ed.create_node_from_name(nm, unreal.Vector2D(x, y), [])
            if nd is not None: return nd
        log("!! node failed", names); return None
    upd = ed.find_event_node("BlueprintUpdateAnimation")
    last = [nd for nd in ed.list_all_nodes() if title(nd) == "Set IsBraking"][0]
    y = 1500
    own = n("Animation|TryGetPawnOwner", 0, y + 200)
    vel = n(["Utilities|Transformation|GetVelocity", "Transformation|GetVelocity", "Physics|GetVelocity"], 200, y + 200)
    g.link(own, "ReturnValue", vel, "self")
    xf = n("Transformation|GetActorTransform", 200, y + 350); g.link(own, "ReturnValue", xf, "self")
    dtc = n("Math|Float|Clamp(Float)", 200, y + 500); g.link(upd, "DeltaTimeX", dtc, "Value"); g.val(dtc, "Min", "0.001"); g.val(dtc, "Max", "0.033")
    DT = (dtc, "ReturnValue")
    pv = g.var_get("PrevVel", 200, y + 650)
    dv = n("Utilities|Operators|Subtract", 450, y + 250); g.link(vel, "ReturnValue", dv, "A"); g.link(pv, "PrevVel", dv, "B")
    aw = n("Utilities|Operators|Divide", 600, y + 250); g.link(dv, "ReturnValue", aw, "A"); g.link(*DT, aw, "B")
    al = n("Math|Transform|InverseTransformDirection", 750, y + 300); g.link(xf, "ReturnValue", al, "T"); g.link(aw, "ReturnValue", al, "Direction")
    g.dump(al); g.dump(aw)
    # frame-to-frame acceleration is noisy (physics substeps vs frame time), so low-pass it first
    asg = g.var_get("AccSmooth", 750, y + 650)
    vi = n("Math|Interpolation|VInterpTo", 900, y + 550)
    g.link(asg, "AccSmooth", vi, "Current"); g.link(al, "ReturnValue", vi, "Target"); g.link(*DT, vi, "DeltaTime"); g.val(vi, "InterpSpeed", str(ACC_SMOOTH))
    s_acc = g.var_set("AccSmooth", 2300, y); g.exe(last, "then", s_acc); g.link(vi, "ReturnValue", s_acc, "AccSmooth")
    br = n("Math|Vector|BreakVector", 950, y + 300); g.link(s_acc, "Output_Get", br, "InVec")
    tx1 = n("Utilities|Operators|Multiply", 1150, y + 250); g.link(br, "X", tx1, "A"); g.val(tx1, "B", str(-GAIN))
    spd = g.var_get("Speed", 1000, y + 450)
    tx2 = n("Utilities|Operators|Multiply", 1150, y + 450); g.link(spd, "Speed", tx2, "A"); g.val(tx2, "B", str(-DRAG))
    tx = n("Utilities|Operators|Add", 1300, y + 300); g.link(tx1, "ReturnValue", tx, "A"); g.link(tx2, "ReturnValue", tx, "B")
    ty = n("Utilities|Operators|Multiply", 1150, y + 350); g.link(br, "Y", ty, "A"); g.val(ty, "B", str(-GAIN_Y))
    # idle shake: the body bone's bounce/rock away from its running average also pushes the spring.
    # Reading the real pose means it fades out on its own when the idle animation blends away.
    mesh = n(["Animation|GetOwningComponent", "Animation|Components|SkeletalMesh|GetOwningComponent", "Components|Animation|GetOwningComponent"], 0, y + 2700)
    sock = n(["Transformation|GetSocketTransform", "Utilities|Transformation|GetSocketTransform"], 200, y + 2700, unreal.SceneComponent)
    g.dump(sock)
    g.link(mesh, "ReturnValue", sock, "self"); g.val(sock, "InSocketName", BODY_BONE); g.val(sock, "TransformSpace", "RTS_Component")
    bt = n("Math|Transform|BreakTransform", 450, y + 2700); g.link(sock, "ReturnValue", bt, "InTransform"); g.dump(bt)
    brl = n("Math|Vector|BreakVector", 650, y + 2700); g.link(bt, "Location", brl, "InVec")
    brr = n("Math|Rotator|BreakRotator", 650, y + 2850); g.link(bt, "Rotation", brr, "InRot")
    posed = n("Math|Float|Clamp(Float)", 750, y + 2850); g.link(brl, "Z", posed, "Value"); g.val(posed, "Min", "0.0"); g.val(posed, "Max", "1.0")
    raw = n("Math|Vector|MakeVector", 850, y + 2750); g.link(brl, "Z", raw, "X"); g.link(brr, "Pitch", raw, "Y"); g.link(posed, "ReturnValue", raw, "Z")
    # BodySmooth.Z stays 0 until the bone has a real pose (its Z is 0 on the first frames), which makes
    # the interp speed huge so the average snaps to that pose instead of kicking the antenna on spawn.
    bsg = g.var_get("BodySmooth", 850, y + 2950)
    bsb = n("Math|Vector|BreakVector", 1050, y + 2950); g.link(bsg, "BodySmooth", bsb, "InVec")
    sp1 = n("Utilities|Operators|Subtract", 1200, y + 2950); g.link(bsb, "Z", sp1, "A"); g.val(sp1, "B", "1.0")
    sp2 = n("Utilities|Operators|Multiply", 1350, y + 2950); g.link(sp1, "ReturnValue", sp2, "A"); g.val(sp2, "B", "-1000.0")
    sp3 = n("Utilities|Operators|Add", 1500, y + 2950); g.link(sp2, "ReturnValue", sp3, "A"); g.val(sp3, "B", str(BODY_SMOOTH))
    vib = n("Math|Interpolation|VInterpTo", 1650, y + 2750)
    g.link(bsg, "BodySmooth", vib, "Current"); g.link(raw, "ReturnValue", vib, "Target"); g.link(*DT, vib, "DeltaTime"); g.link(sp3, "ReturnValue", vib, "InterpSpeed")
    s_bs = g.var_set("BodySmooth", 2420, y); g.exe(s_acc, "then", s_bs); g.link(vib, "ReturnValue", s_bs, "BodySmooth")
    hp = n("Utilities|Operators|Subtract", 1850, y + 2750); g.link(raw, "ReturnValue", hp, "A"); g.link(s_bs, "Output_Get", hp, "B")
    hpg = n("Utilities|Operators|Multiply", 2000, y + 2750); g.link(hp, "ReturnValue", hpg, "A"); g.val(hpg, "B", "(X=%f,Y=%f,Z=0.000000)" % (IDLE_BOUNCE, IDLE_ROLL))
    hpc = n(["Math|Vector|ClampVectorSize", "Math|Vector|ClampVectorSize(Vector)"], 2150, y + 2750); g.link(hpg, "ReturnValue", hpc, "A"); g.val(hpc, "Min", "0.0"); g.val(hpc, "Max", str(IDLE_MAX))
    fade = n(["Math|Float|MapRangeClamped", "Math|Float|MapRangeClamped(Float)"], 2150, y + 2950); g.link(spd, "Speed", fade, "Value")
    g.val(fade, "InRangeA", "0.0"); g.val(fade, "InRangeB", str(IDLE_FADE)); g.val(fade, "OutRangeA", "1.0"); g.val(fade, "OutRangeB", "0.0")
    hpf = n("Utilities|Operators|Multiply", 2250, y + 2850); g.link(hpc, "ReturnValue", hpf, "A"); g.link(fade, "ReturnValue", hpf, "B")
    hpb = n("Math|Vector|BreakVector", 2300, y + 2750); g.link(hpf, "ReturnValue", hpb, "InVec")
    txi = n("Utilities|Operators|Add", 2450, y + 2750); g.link(tx, "ReturnValue", txi, "A"); g.link(hpb, "X", txi, "B")
    tyi = n("Utilities|Operators|Add", 2450, y + 2900); g.link(ty, "ReturnValue", tyi, "A"); g.link(hpb, "Y", tyi, "B")
    cx = n("Math|Float|Clamp(Float)", 1450, y + 300); g.link(txi, "ReturnValue", cx, "Value"); g.val(cx, "Min", str(-MAXB)); g.val(cx, "Max", str(MAXB))
    cy = n("Math|Float|Clamp(Float)", 1450, y + 450); g.link(tyi, "ReturnValue", cy, "Value"); g.val(cy, "Min", str(-MAXB)); g.val(cy, "Max", str(MAXB))
    tgt = n("Math|Vector|MakeVector", 1600, y + 350); g.link(cx, "ReturnValue", tgt, "X"); g.link(cy, "ReturnValue", tgt, "Y"); g.val(tgt, "Z", "0.0")
    bend = g.var_get("AntBend", 1600, y + 550); bvel = g.var_get("AntBendVel", 1600, y + 650)
    e = n("Utilities|Operators|Subtract", 1800, y + 400); g.link(tgt, "ReturnValue", e, "A"); g.link(bend, "AntBend", e, "B")
    ek = n("Utilities|Operators|Multiply", 1950, y + 400); g.link(e, "ReturnValue", ek, "A"); g.val(ek, "B", "(X=%f,Y=%f,Z=%f)" % (K, K, K))
    vc = n("Utilities|Operators|Multiply", 1950, y + 600); g.link(bvel, "AntBendVel", vc, "A"); g.val(vc, "B", "(X=%f,Y=%f,Z=%f)" % (C, C, C))
    f = n("Utilities|Operators|Subtract", 2100, y + 450); g.link(ek, "ReturnValue", f, "A"); g.link(vc, "ReturnValue", f, "B")
    fdt = n("Utilities|Operators|Multiply", 2250, y + 450); g.link(f, "ReturnValue", fdt, "A"); g.link(*DT, fdt, "B")
    nv = n("Utilities|Operators|Add", 2400, y + 500); g.link(bvel, "AntBendVel", nv, "A"); g.link(fdt, "ReturnValue", nv, "B")
    g.dump(ek); g.dump(fdt)
    s_bv = g.var_set("AntBendVel", 2550, y); g.exe(s_bs, "then", s_bv); g.link(nv, "ReturnValue", s_bv, "AntBendVel")
    bdt = n("Utilities|Operators|Multiply", 2700, y + 450); g.link(s_bv, "Output_Get", bdt, "A"); g.link(*DT, bdt, "B")
    nb = n("Utilities|Operators|Add", 2850, y + 450); g.link(bend, "AntBend", nb, "A"); g.link(bdt, "ReturnValue", nb, "B")
    cl = n(["Math|Vector|ClampVectorSize", "Math|Vector|ClampVectorSize(Vector)"], 3000, y + 450); g.link(nb, "ReturnValue", cl, "A"); g.val(cl, "Min", "0.0"); g.val(cl, "Max", str(MAXB))
    g.dump(cl)
    s_b = g.var_set("AntBend", 3150, y); g.exe(s_bv, "then", s_b); g.link(cl, "ReturnValue", s_b, "AntBend")
    s_pv = g.var_set("PrevVel", 3400, y); g.exe(s_b, "then", s_pv); g.link(vel, "ReturnValue", s_pv, "PrevVel")
    # The antenna segment bones are siblings (all parented to MASTER-ROTATION), so bending is done per segment:
    # segment k tilts (k+1)/4 of the bend, and is moved so it starts where the previous tilted segment ends.
    br2 = n("Math|Vector|BreakVector", 3400, y + 300); g.link(s_b, "Output_Get", br2, "InVec")
    prev_exec = s_pv
    rots = []
    for k in range(4):
        f = (k + 1) / 4.0
        pm = n("Utilities|Operators|Multiply", 3600, y + 250 + k * 300); g.link(br2, "X", pm, "A"); g.val(pm, "B", str(SIGN_P * f))
        rm = n("Utilities|Operators|Multiply", 3600, y + 350 + k * 300); g.link(br2, "Y", rm, "A"); g.val(rm, "B", str(SIGN_R * f))
        mr = n("Math|Rotator|MakeRotator", 3800, y + 300 + k * 300); g.link(pm, "ReturnValue", mr, "Pitch"); g.link(rm, "ReturnValue", mr, "Roll")
        sr = g.var_set("AntRot%d" % k, 3900 + k * 250, y); g.exe(prev_exec, "then", sr); g.link(mr, "ReturnValue", sr, "AntRot%d" % k)
        prev_exec = sr; rots.append(mr)
    acc = None
    for k in range(3):
        rv = n("Math|Vector|RotateVector", 4100, y + 1500 + k * 200)
        g.val(rv, "A", "(X=0.000000,Y=0.000000,Z=%f)" % SEG); g.link(rots[k], "ReturnValue", rv, "B")
        if acc is None:
            acc = rv
        else:
            ad = n("Utilities|Operators|Add", 4300, y + 1500 + k * 200); g.link(acc, "ReturnValue", ad, "A"); g.link(rv, "ReturnValue", ad, "B"); acc = ad
        off = n("Utilities|Operators|Subtract", 4500, y + 1500 + k * 200)
        g.link(acc, "ReturnValue", off, "A"); g.val(off, "B", "(X=0.000000,Y=0.000000,Z=%f)" % (SEG * (k + 1)))
        so = g.var_set("AntOff%d" % (k + 1), 4900 + k * 250, y); g.exe(prev_exec, "then", so); g.link(off, "ReturnValue", so, "AntOff%d" % (k + 1))
        prev_exec = so
    g.dump(rv)

    # ============ AnimGraph
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    a = gh.G(ag, log)
    oldmb = [nd for nd in ag.list_all_nodes() if nd.get_class().get_name() in ("AnimGraphNode_ModifyBone",) or (nd.get_class().get_name() == "K2Node_VariableGet" and ("AntennaRot" in str(BEL.get_node_title(nd)) or "AntRot" in str(BEL.get_node_title(nd)) or "AntOff" in str(BEL.get_node_title(nd))))]
    ag.remove_nodes(oldmb); log("removed anim", len(oldmb))
    l2c = [nd for nd in ag.list_all_nodes() if nd.get_class().get_name() == "AnimGraphNode_LocalToComponentSpace"][0]
    wc = [nd for nd in ag.list_all_nodes() if nd.get_class().get_name() == "AnimGraphNode_WheelController"][0]
    lp = BEL.get_node_pos(l2c); wp = BEL.get_node_pos(wc)
    log("l2c", lp.x, lp.y, "wc", wp.x, wp.y)
    prev, prevpin = l2c, "ComponentPose"
    for i, bone in enumerate(SEGS):
        nd = None
        for nm in ("Animation|SkeletalControls|Transform(Modify)Bone", "Animation|SkeletalControls|TransformModifyBone", "Animation|SkeletalControls|ModifyBone"):
            nd = ag.create_node_from_name(nm, unreal.Vector2D(lp.x + 60 + i * 260, lp.y + 300), [])
            if nd: break
        if nd is None: log("!! modify bone node failed"); break
        st = nd.get_editor_property("node")
        br_ = unreal.BoneReference(); br_.set_editor_property("bone_name", bone); st.set_editor_property("bone_to_modify", br_)
        st.set_editor_property("rotation_mode", unreal.BoneModificationMode.BMM_ADDITIVE)
        st.set_editor_property("rotation_space", unreal.BoneControlSpace.BCS_COMPONENT_SPACE)
        st.set_editor_property("translation_mode", unreal.BoneModificationMode.BMM_ADDITIVE if i > 0 else unreal.BoneModificationMode.BMM_IGNORE)
        st.set_editor_property("translation_space", unreal.BoneControlSpace.BCS_COMPONENT_SPACE)
        st.set_editor_property("scale_mode", unreal.BoneModificationMode.BMM_IGNORE)
        nd.set_editor_property("node", st)
        if i == 0: a.dump(nd)
        a.link(prev, prevpin, nd, "ComponentPose")
        vg = a.var_get("AntRot%d" % i, lp.x + i * 260, lp.y + 500)
        a.link(vg, "AntRot%d" % i, nd, "Rotation")
        if i > 0:
            vo = a.var_get("AntOff%d" % i, lp.x + i * 260, lp.y + 600)
            a.link(vo, "AntOff%d" % i, nd, "Translation")
        prev, prevpin = nd, "Pose"
    a.link(prev, prevpin, wc, "ComponentPose")
    if "AntennaRot" in [str(x) for x in BEL.list_member_variable_names(abp)]:
        BEL.remove_unused_variables(abp)
    BEL.compile_blueprint(abp)
    for gname, e2 in (("event", ed), ("anim", ag)):
        for nd in e2.list_nodes_with_errors(): log("ERROR", gname, BEL.get_node_title(nd))
        for nd in e2.list_nodes_with_warnings(): log("WARN", gname, BEL.get_node_title(nd))
    log("saved", EAL.save_asset(ABP, only_if_is_dirty=False))
    log("done")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_ANTENNA_DONE")
