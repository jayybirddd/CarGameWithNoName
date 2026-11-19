# v9: lap racing - BP_RaceGate (placeholder arch with a trigger) and BP_RaceManager (one per race level).
# Gate 0 is START / FINISH; gates 1..NumGates-1 run around the track in order. Only the next gate in order counts.
# The manager times the race, counts laps (Laps, default 3), wins the race after the last lap, and puts the car back
# at the last gate passed if it falls below FallZ. BP_CarHUD reads the manager for the LAP / TIME / GATES LEFT line.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gplace as gp; importlib.reload(gp)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_race_assets.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
gp.LOG = log
EAL, BEL = gp.EAL, gp.BEL
PH = "/Game/Car/Placeholders"
MGRC = PH + "/BP_RaceManager.BP_RaceManager_C"
XF = BEL.get_struct_type(unreal.Transform.static_struct())
EQ_INT = ["Math|Integer|Equal(Integer)", "Utilities|Operators|Equal(==)", "Utilities|Operators|Equal"]
def mi(name, color):
    p = PH + "/" + name
    m = unreal.load_asset(p) if EAL.does_asset_exist(p) else gp.AT.create_asset(name, PH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(m, unreal.load_asset(PH + "/M_Placeholder"))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(m, "Color", color)
    EAL.save_asset(p, only_if_is_dirty=False); return m
try:
    gate_mi = mi("MI_Placeholder_Gate", unreal.LinearColor(0.1, 0.55, 1.0, 1))
    # ---------------- manager (built first: the gate's graph sets its variables)
    mgr = gp.new_bp("BP_RaceManager", PH)
    I, R, B = gp.T("int"), gp.T("real"), gp.T("bool")
    gp.add_vars(mgr, [("Laps", I), ("NumGates", I), ("FallZ", R)], "Race")
    gp.add_vars(mgr, [("Lap", I), ("NextGate", I), ("RaceTime", R), ("Finished", B), ("GateHit", I), ("GateHitTransform", XF),
                      ("RespawnTransform", XF), ("GatePopup", R), ("LastGate", I), ("LastGateTime", R)], "", editable=False)
    gp.set_defaults(mgr, {"Laps": 3, "NumGates": 8, "FallZ": -100000.0, "Lap": 1, "NextGate": 1, "GateHit": -1})
    gp.text_comp(mgr, "Label", "RACE MANAGER", unreal.Vector(0, 0, 100), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), 40.0, unreal.Color(r=255, g=255, b=255, a=255)).set_editor_property("hidden_in_game", True)
    BEL.compile_blueprint(mgr)
    ed, g, n = gp.graph(mgr)
    # BeginPlay: race starts at the player start
    bpe = ed.find_event_node("ReceiveBeginPlay")
    gps = n(["Utilities|GetActorOfClass", "Actor|GetActorOfClass"], 200, -400); g.exe(bpe, "then", gps); g.val(gps, "ActorClass", "/Script/Engine.PlayerStart")
    pxf = n("Transformation|GetActorTransform", 400, -250, unreal.Actor); g.link(gps, "ReturnValue", pxf, "self")
    srs0 = g.var_set("RespawnTransform", 600, -400); g.exe(gps, "then", srs0); g.link(pxf, "ReturnValue", srs0, "RespawnTransform")
    tk = ed.find_event_node("ReceiveTick")
    seq = n("Utilities|FlowControl|Sequence", 200, 0); g.exe(tk, "then", seq); ed.add_node_pin(seq)
    # then_0: clock + popup timer
    nf = n("Math|Boolean|NOTBoolean", 400, 300); g.link(g.var_get("Finished", 250, 300), "Finished", nf, "A")
    ad = n("Utilities|Operators|Add", 400, 200); g.link(g.var_get("RaceTime", 250, 200), "RaceTime", ad, "A"); g.link(tk, "DeltaSeconds", ad, "B")
    tsel = n("Math|Float|SelectFloat", 550, 200); g.link(ad, "ReturnValue", tsel, "A"); g.link(g.var_get("RaceTime", 400, 400), "RaceTime", tsel, "B"); g.link(nf, "ReturnValue", tsel, "bPickA")
    srt = g.var_set("RaceTime", 700, 0); g.exe(seq, "then_0", srt); g.link(tsel, "ReturnValue", srt, "RaceTime")
    pg = n("Utilities|Operators|Subtract", 700, 300); g.link(g.var_get("GatePopup", 550, 350), "GatePopup", pg, "A"); g.link(tk, "DeltaSeconds", pg, "B")
    pz = n("Math|Float|Max(Float)", 850, 300); g.link(pg, "ReturnValue", pz, "A"); g.val(pz, "B", "0.0")
    spp = g.var_set("GatePopup", 950, 0); g.exe(srt, "then", spp); g.link(pz, "ReturnValue", spp, "GatePopup")
    # then_1: a gate was hit -> if it's the next one, advance
    y = 800
    gh = g.var_get("GateHit", 200, y + 200)
    ge = n(EQ_INT, 400, y + 200); g.link(gh, "GateHit", ge, "A"); g.link(g.var_get("NextGate", 250, y + 300), "NextGate", ge, "B")
    bg = n("Utilities|FlowControl|Branch", 600, y); g.exe(seq, "then_1", bg); g.link(ge, "ReturnValue", bg, "Condition")
    slg = g.var_set("LastGate", 850, y); g.exe(bg, "then", slg); g.link(g.var_get("GateHit", 700, y + 200), "GateHit", slg, "LastGate")
    slt = g.var_set("LastGateTime", 1100, y); g.exe(slg, "then", slt); g.link(g.var_get("RaceTime", 950, y + 200), "RaceTime", slt, "LastGateTime")
    srs = g.var_set("RespawnTransform", 1350, y); g.exe(slt, "then", srs); g.link(g.var_get("GateHitTransform", 1200, y + 200), "GateHitTransform", srs, "RespawnTransform")
    spo = g.var_set("GatePopup", 1600, y); g.exe(srs, "then", spo); g.val(spo, "GatePopup", "2.5")
    nz = n(EQ_INT, 1700, y + 250); g.link(g.var_get("NextGate", 1550, y + 250), "NextGate", nz, "A"); g.val(nz, "B", "0")
    bl = n("Utilities|FlowControl|Branch", 1850, y); g.exe(spo, "then", bl); g.link(nz, "ReturnValue", bl, "Condition")
    clear = g.var_set("GateHit", 4200, y); g.val(clear, "GateHit", "-1"); g.exe(bg, "else", clear)
    # crossed START / FINISH: lap done
    la = n("Utilities|Operators|Add", 2050, y + 250); g.link(g.var_get("Lap", 1900, y + 250), "Lap", la, "A"); g.val(la, "B", "1")
    sla = g.var_set("Lap", 2100, y - 200); g.exe(bl, "then", sla); g.link(la, "ReturnValue", sla, "Lap")
    gt = n("Utilities|Operators|Greater(>)", 2300, y - 50); g.link(sla, "Output_Get", gt, "A"); g.link(g.var_get("Laps", 2150, y), "Laps", gt, "B")
    bw = n("Utilities|FlowControl|Branch", 2350, y - 200); g.exe(sla, "then", bw); g.link(gt, "ReturnValue", bw, "Condition")
    sn1 = g.var_set("NextGate", 2600, y - 100); g.exe(bw, "else", sn1); g.val(sn1, "NextGate", "1"); g.exe(sn1, "then", clear)
    # race won: freeze the clock, show the last lap number, and hand over to the victory screen like the finish line does
    sfin = g.var_set("Finished", 2600, y - 400); g.exe(bw, "then", sfin); g.val(sfin, "Finished", "true")
    slap = g.var_set("Lap", 2850, y - 400); g.exe(sfin, "then", slap); g.link(g.var_get("Laps", 2700, y - 250), "Laps", slap, "Lap")
    pp = n("Game|GetPlayerPawn", 2850, y - 650)
    cc = n("Utilities|Casting|CastToBP_CarPawn", 3100, y - 400); g.exe(slap, "then", cc); g.link(pp, "ReturnValue", cc, "Object")
    sw = gp.member(ed, g, cc, gp.CARC, "Won", 3350, y - 400, setter=True); g.exe(cc, "then", sw); g.val(sw, "Won", "true")
    mvc = gp.member(ed, g, cc, gp.VEH, "VehicleMovementComponent", 3350, y - 200)
    st = n("Game|Components|ChaosVehicleMovement|SetThrottleInput", 3600, y - 400); g.exe(sw, "then", st); g.link(mvc, "VehicleMovementComponent", st, "self"); g.val(st, "Throttle", "0.0")
    sh = n("Game|Components|ChaosVehicleMovement|SetHandbrakeInput", 3850, y - 400); g.exe(st, "then", sh); g.link(mvc, "VehicleMovementComponent", sh, "self"); g.val(sh, "bNewHandbrake", "true")
    dis = n("Input|DisableInput", 4100, y - 400, unreal.Actor); g.exe(sh, "then", dis); g.link(cc, gp.as_pin(g, cc), dis, "self")
    g.link(n("Game|GetPlayerController", 3950, y - 250), "ReturnValue", dis, "PlayerController"); g.exe(dis, "then", clear); g.exe(cc, "CastFailed", clear)
    # any other gate: next one, wrapping to START / FINISH after the last
    nx = n("Utilities|Operators|Add", 2100, y + 400); g.link(g.var_get("NextGate", 1950, y + 400), "NextGate", nx, "A"); g.val(nx, "B", "1")
    ov = n(["Utilities|Operators|GreaterEqual(>=)", "Utilities|Operators|GreaterEqual"], 2250, y + 500); g.link(nx, "ReturnValue", ov, "A"); g.link(g.var_get("NumGates", 2100, y + 550), "NumGates", ov, "B")
    wrap = n("Math|Integer|SelectInt", 2400, y + 400); g.val(wrap, "A", "0"); g.link(nx, "ReturnValue", wrap, "B"); g.link(ov, "ReturnValue", wrap, "bPickA")
    sn2 = g.var_set("NextGate", 2600, y + 200); g.exe(bl, "else", sn2); g.link(wrap, "ReturnValue", sn2, "NextGate"); g.exe(sn2, "then", clear)
    # then_2: fell off the track -> back to the last gate passed, stopped
    y = 2000
    pp2 = n("Game|GetPlayerPawn", 200, y + 200)
    loc = n("Transformation|GetActorLocation", 400, y + 200, unreal.Actor); g.link(pp2, "ReturnValue", loc, "self")
    bz = n("Math|Vector|BreakVector", 600, y + 200); g.link(loc, "ReturnValue", bz, "InVec")
    low = n("Utilities|Operators|Less(<)", 800, y + 200); g.link(bz, "Z", low, "A"); g.link(g.var_get("FallZ", 650, y + 300), "FallZ", low, "B")
    nf2 = n("Math|Boolean|NOTBoolean", 800, y + 350); g.link(g.var_get("Finished", 650, y + 400), "Finished", nf2, "A")
    af = n("Math|Boolean|ANDBoolean", 950, y + 250); g.link(low, "ReturnValue", af, "A"); g.link(nf2, "ReturnValue", af, "B")
    bf = n("Utilities|FlowControl|Branch", 1000, y); g.exe(seq, "then_2", bf); g.link(af, "ReturnValue", bf, "Condition")
    rt = n("Math|Transform|BreakTransform", 1100, y + 300); g.link(g.var_get("RespawnTransform", 950, y + 450), "RespawnTransform", rt, "InTransform")
    up = n("Utilities|Operators|Add", 1300, y + 300); g.link(rt, "Location", up, "A"); g.val(up, "B", "(X=0.000000,Y=0.000000,Z=150.000000)")
    tp = n(["Transformation|SetActorLocationAndRotation"], 1300, y, unreal.Actor); g.exe(bf, "then", tp); g.link(pp2, "ReturnValue", tp, "self")
    g.link(up, "ReturnValue", tp, "NewLocation"); g.link(rt, "Rotation", tp, "NewRotation"); g.val(tp, "bTeleport", "true"); g.dump(tp)
    cc2 = n("Utilities|Casting|CastToBP_CarPawn", 1600, y); g.exe(tp, "then", cc2); g.link(pp2, "ReturnValue", cc2, "Object")
    msh = gp.member(ed, g, cc2, gp.VEH, "Mesh", 1650, y + 250)
    zv = n(["Physics|SetPhysicsLinearVelocity", "Physics|SetPhysicsLinearVelocity(Component)"], 1850, y); g.exe(cc2, "then", zv); g.link(msh, "Mesh", zv, "self")
    za = n(["Physics|SetPhysicsAngularVelocityinDegrees", "Physics|SetPhysicsAngularVelocityInDegrees"], 2100, y); g.exe(zv, "then", za); g.link(msh, "Mesh", za, "self")
    gp.finish(mgr, ed, PH + "/BP_RaceManager")

    # ---------------- gate: posts + banner + labels + trigger; widths are set per placed gate by the level builder
    gate = gp.new_bp("BP_RaceGate", PH)
    gp.add_vars(gate, [("GateIndex", I)], "Race Gate")
    for nm, yy in (("PostL", -1300.0), ("PostR", 1300.0)):
        gp.shape_comp(gate, nm, "/Engine/BasicShapes/Cylinder", gate_mi, unreal.Vector(0, yy, 300), unreal.Vector(0.5, 0.5, 6.0))
    gp.shape_comp(gate, "Banner", "/Engine/BasicShapes/Cube", gate_mi, unreal.Vector(0, 0, 640), unreal.Vector(0.3, 26.5, 1.0))
    white = unreal.Color(r=255, g=255, b=255, a=255)
    gp.text_comp(gate, "LabelFront", "GATE", unreal.Vector(-20, 0, 640), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), 80.0, white)
    gp.text_comp(gate, "LabelBack", "GATE", unreal.Vector(20, 0, 640), unreal.Rotator(), 80.0, white)
    tr = gp.add_comp(gate, unreal.BoxComponent, "Trigger")
    tr.set_editor_property("box_extent", unreal.Vector(150, 1300, 600)); tr.set_editor_property("relative_location", unreal.Vector(0, 0, 400))
    gp.trigger_only(tr)
    BEL.compile_blueprint(gate)
    ed, g, n = gp.graph(gate)
    ev = ed.find_event_node("ReceiveActorBeginOverlap")
    cc = n("Utilities|Casting|CastToBP_CarPawn", 250, 0); g.exe(ev, "then", cc); g.link(ev, "OtherActor", cc, "Object")
    gm = n(["Utilities|GetActorOfClass", "Actor|GetActorOfClass"], 500, 0); g.exe(cc, "then", gm); g.val(gm, "ActorClass", MGRC)
    mc = n("Utilities|Casting|CastToBP_RaceManager", 750, 0); g.exe(gm, "then", mc); g.link(gm, "ReturnValue", mc, "Object")
    sgx = gp.member(ed, g, mc, MGRC, "GateHitTransform", 1000, 0, setter=True); g.exe(mc, "then", sgx)
    g.link(n("Transformation|GetActorTransform", 850, 250, unreal.Actor), "ReturnValue", sgx, "GateHitTransform")
    sgi = gp.member(ed, g, mc, MGRC, "GateHit", 1250, 0, setter=True); g.exe(sgx, "then", sgi); g.link(g.var_get("GateIndex", 1100, 250), "GateIndex", sgi, "GateHit")
    gp.finish(gate, ed, PH + "/BP_RaceGate")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V9_RACE_ASSETS_DONE")
