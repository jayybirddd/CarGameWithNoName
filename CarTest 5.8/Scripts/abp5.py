import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_abp2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
ABP = "/Game/Car/Blueprints/ABP_CarBody"
def anim(n): return unreal.load_asset("/Game/Car/Animations/" + n)
try:
    abp = unreal.load_asset(ABP)
    # variables
    have = [str(x) for x in BEL.list_member_variable_names(abp)]
    for nm, tp in [("Speed","real"),("Throttle","real"),("Brake","real"),("SteerSmoothed","real"),("LeanLeft","real"),("LeanRight","real"),("BodyState","int"),("IsAccelerating","bool"),("IsBraking","bool")]:
        if nm not in have: BEL.add_member_variable(abp, nm, BEL.get_basic_type_by_name(tp))
    BEL.compile_blueprint(abp)

    # ================= EventGraph
    ed = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "EventGraph")
    upd = ed.find_event_node("BlueprintUpdateAnimation")
    rm = [n for n in ed.list_all_nodes() if upd is None or n != upd]
    ed.remove_nodes(rm)
    g = gh.G(ed, log)
    if upd is None:
        upd = g.n("AddEvent|EventBlueprintUpdateAnimation", 0, 0)
    upd.set_node_pos(unreal.IntPoint(0, 0))
    g.dump(upd)
    own = g.n("Animation|TryGetPawnOwner", 0, 200)
    cast = g.n("Utilities|Casting|CastToBP_CarPawn", 250, 0)
    g.exe(upd, "then", cast); g.link(own, "ReturnValue", cast, "Object")
    g.dump(cast)
    mvg = ed.add_get_member_variable_node("VehicleMovementComponent", "/Script/ChaosVehicles.WheeledVehiclePawn")
    if mvg: mvg.set_node_pos(unreal.IntPoint(500, 200)); g.dump(mvg)
    castout = None
    for p in g.pins(cast):
        if g.norm(unreal.BlueprintGraphPinLibrary.get_pin_name(p)).startswith("as"): castout = str(unreal.BlueprintGraphPinLibrary.get_pin_name(p))
    g.link(cast, castout, mvg, "self")
    MV = lambda: None
    gt = g.n("Game|Components|ChaosVehicleMovement|GetThrottleInput", 800, 150)
    gb = g.n("Game|Components|ChaosVehicleMovement|GetBrakeInput", 800, 250)
    gs = g.n("Game|Components|ChaosVehicleMovement|GetSteeringInput", 800, 350)
    gf = g.n("Game|Components|ChaosVehicleMovement|GetForwardSpeed", 800, 450)
    for nd in (gt, gb, gs, gf): g.link(mvg, "VehicleMovementComponent", nd, "self")
    g.dump(gt)
    kmh = g.n("Utilities|Operators|Multiply", 1000, 450); g.link(gf, "ReturnValue", kmh, "A"); g.val(kmh, "B", "0.036")
    s_speed = g.var_set("Speed", 700, 0); s_thr = g.var_set("Throttle", 950, 0); s_brk = g.var_set("Brake", 1200, 0)
    g.exe(cast, "then", gt); g.exe(gt, "then", gb); g.exe(gb, "then", gs); g.exe(gs, "then", s_speed); g.exe(s_speed, "then", s_thr); g.exe(s_thr, "then", s_brk)
    g.link(kmh, "ReturnValue", s_speed, "Speed"); g.link(gt, "ReturnValue", s_thr, "Throttle"); g.link(gb, "ReturnValue", s_brk, "Brake")
    # steer smoothing
    ssg = g.var_get("SteerSmoothed", 1200, 350)
    fi = g.n("Math|Interpolation|FInterpTo", 1400, 300)
    g.link(ssg, "SteerSmoothed", fi, "Current"); g.link(gs, "ReturnValue", fi, "Target")
    g.link(upd, "DeltaTimeX", fi, "DeltaTime"); g.val(fi, "InterpSpeed", "5.0")
    s_ss = g.var_set("SteerSmoothed", 1450, 0); g.exe(s_brk, "then", s_ss); g.link(fi, "ReturnValue", s_ss, "SteerSmoothed")
    # speed factor
    ab = g.n("Math|Float|Absolute(Float)", 1250, 600); g.link(s_speed, "Output_Get", ab, "A")
    mrc = g.n("Math|Float|MapRangeClamped", 1450, 600)
    g.link(ab, "ReturnValue", mrc, "Value"); g.val(mrc, "InRangeA", "5.0"); g.val(mrc, "InRangeB", "40.0"); g.val(mrc, "OutRangeA", "0.0"); g.val(mrc, "OutRangeB", "1.0")
    g.dump(mrc)
    # lean left = max(-steer,0)*f ; right = max(steer,0)*f
    neg = g.n("Utilities|Operators|Multiply", 1700, 450); g.link(s_ss, "Output_Get", neg, "A"); g.val(neg, "B", "-1.0")
    mxl = g.n("Math|Float|Max(Float)", 1850, 450); g.link(neg, "ReturnValue", mxl, "A"); g.val(mxl, "B", "0.0")
    mxr = g.n("Math|Float|Max(Float)", 1850, 550); g.link(s_ss, "Output_Get", mxr, "A"); g.val(mxr, "B", "0.0")
    ml = g.n("Utilities|Operators|Multiply", 2000, 450); g.link(mxl, "ReturnValue", ml, "A"); g.link(mrc, "ReturnValue", ml, "B")
    mr = g.n("Utilities|Operators|Multiply", 2000, 550); g.link(mxr, "ReturnValue", mr, "A"); g.link(mrc, "ReturnValue", mr, "B")
    s_ll = g.var_set("LeanLeft", 1700, 0); s_lr = g.var_set("LeanRight", 1950, 0)
    g.exe(s_ss, "then", s_ll); g.exe(s_ll, "then", s_lr)
    g.link(ml, "ReturnValue", s_ll, "LeanLeft"); g.link(mr, "ReturnValue", s_lr, "LeanRight")
    # body state
    gtB = g.n("Utilities|Operators|Greater(>)", 2200, 300); g.link(s_brk, "Output_Get", gtB, "A"); g.val(gtB, "B", "0.1")
    gtS = g.n("Utilities|Operators|Greater(>)", 2200, 400); g.link(s_speed, "Output_Get", gtS, "A"); g.val(gtS, "B", "3.0")
    andB = g.n("Math|Boolean|ANDBoolean", 2400, 350); g.link(gtB, "ReturnValue", andB, "A"); g.link(gtS, "ReturnValue", andB, "B")
    gtT = g.n("Utilities|Operators|Greater(>)", 2200, 500); g.link(s_thr, "Output_Get", gtT, "A"); g.val(gtT, "B", "0.1")
    gtR = g.n("Utilities|Operators|Greater(>)", 2200, 600); g.link(s_speed, "Output_Get", gtR, "A"); g.val(gtR, "B", "-3.0")
    andT = g.n("Math|Boolean|ANDBoolean", 2400, 550); g.link(gtT, "ReturnValue", andT, "A"); g.link(gtR, "ReturnValue", andT, "B")
    si1 = g.n("Math|Integer|SelectInt", 2600, 550); g.val(si1, "A", "1"); g.val(si1, "B", "0"); g.link(andT, "ReturnValue", si1, "bPickA")
    si2 = g.n("Math|Integer|SelectInt", 2800, 400); g.val(si2, "A", "2"); g.link(si1, "ReturnValue", si2, "B"); g.link(andB, "ReturnValue", si2, "bPickA")
    g.dump(si1); g.dump(gtB)
    s_bs = g.var_set("BodyState", 2200, 0); g.exe(s_lr, "then", s_bs); g.link(si2, "ReturnValue", s_bs, "BodyState")
    s_ia = g.var_set("IsAccelerating", 2450, 0); g.exe(s_bs, "then", s_ia); g.link(andT, "ReturnValue", s_ia, "IsAccelerating")
    s_ib = g.var_set("IsBraking", 2700, 0); g.exe(s_ia, "then", s_ib); g.link(andB, "ReturnValue", s_ib, "IsBraking")

    # ================= AnimGraph
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    root = None
    rm = []
    for n in ag.list_all_nodes():
        if n.get_class().get_name() == "AnimGraphNode_Root": root = n
        else: rm.append(n)
    ag.remove_nodes(rm)
    a = gh.G(ag, log)
    root.set_node_pos(unreal.IntPoint(2200, 0))
    def seqp(name, x, y, loop, evaluator=False, t=0.0):
        nd = a.n("Animation|Sequences|SequenceEvaluator" if evaluator else "Animation|Sequences|SequencePlayer", x, y)
        try:
            st = nd.get_editor_property("node")
            st.set_editor_property("sequence", anim(name))
            if evaluator:
                st.set_editor_property("explicit_time", t)
            else:
                st.set_editor_property("loop_animation", loop)
            nd.set_editor_property("node", st)
        except Exception as e:
            log("seq prop err", name, e, [x for x in dir(nd.get_editor_property("node")) if not x.startswith("_")][:60])
        return nd
    idle = seqp("AS_Idle", 0, 0, True)
    acc = seqp("AS_Accelerate", 0, 200, False)
    dec = seqp("AS_Decelerate", 0, 400, False)
    a.dump(idle)
    def bbool(x, y, tpose, fpose, var, tt, ft):
        nd = a.n("Animation|Blends|BlendPosesbybool", x, y)
        a.dump(nd)
        try:
            st = nd.get_editor_property("node")
            txt = st.export_text()
            log("bool node text", txt[:600])
            ok = st.import_text("(ChildUpateMode=ResetChildOnActivate,BlendTime=(0.300000,0.400000))") if hasattr(st, "import_text") else None
            log("import reset", ok, st.export_text()[:300])
            nd.set_editor_property("node", st)
        except Exception as e: log("bool node err", e)
        a.link(tpose, "Pose", nd, "BlendPose_0"); a.link(fpose, "Pose", nd, "BlendPose_1")
        vg = a.var_get(var, x - 150, y + 250); a.link(vg, var, nd, "bActiveValue")
        a.val(nd, "BlendTime_0", str(tt)); a.val(nd, "BlendTime_1", str(ft))
        return nd
    b1 = bbool(300, 150, acc, idle, "IsAccelerating", 0.3, 0.45)
    bl = bbool(550, 250, dec, b1, "IsBraking", 0.15, 0.35)
    tl = seqp("AS_TurnLeft_Add", 400, 450, False, True, 1.0)
    tr = seqp("AS_TurnRight_Add", 800, 450, False, True, 1.0)
    ad1 = a.n("Animation|Blends|ApplyAdditive", 700, 150)
    ad2 = a.n("Animation|Blends|ApplyAdditive", 1100, 150)
    a.dump(ad1)
    a.link(bl, "Pose", ad1, "Base"); a.link(tl, "Pose", ad1, "Additive")
    a.link(ad1, "Pose", ad2, "Base"); a.link(tr, "Pose", ad2, "Additive")
    llg = a.var_get("LeanLeft", 550, 350); a.link(llg, "LeanLeft", ad1, "Alpha")
    lrg = a.var_get("LeanRight", 950, 350); a.link(lrg, "LeanRight", ad2, "Alpha")
    l2c = a.n("Animation|ConvertSpaces|LocalToComponent", 1400, 150)
    wc = a.n("Animation|SkeletalControls|WheelControllerforWheeledVehicle", 1600, 150)
    c2l = a.n("Animation|ConvertSpaces|ComponentToLocal", 1900, 150)
    a.dump(l2c); a.dump(wc); a.dump(c2l); a.dump(root)
    a.link(ad2, "Pose", l2c, "LocalPose")
    a.link(l2c, "ComponentPose", wc, "ComponentPose")
    a.link(wc, "Pose", c2l, "ComponentPose")
    a.link(c2l, "Pose", root, "Result")
    BEL.compile_blueprint(abp)
    for gname, e in (("event", ed), ("anim", ag)):
        for nd in e.list_nodes_with_errors(): log("ERROR", gname, BEL.get_node_title(nd))
        for nd in e.list_nodes_with_warnings(): log("WARN", gname, BEL.get_node_title(nd))
    EAL.save_asset(ABP)

    # ---- hook the ABP + physics into the car
    SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    SDL = unreal.SubobjectDataBlueprintFunctionLibrary
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    for h in SDS.k2_gather_subobject_data_for_blueprint(car):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.SkeletalMeshComponent):
            o.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
            o.set_editor_property("anim_class", abp.generated_class())
            bi = o.get_editor_property("body_instance")
            bi.set_editor_property("simulate_physics", True)
            o.set_editor_property("body_instance", bi)
            log("mesh anim", o.get_editor_property("anim_class"), "sim", o.get_editor_property("body_instance").get_editor_property("simulate_physics"))
    BEL.compile_blueprint(car); EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_ABP2_DONE")
