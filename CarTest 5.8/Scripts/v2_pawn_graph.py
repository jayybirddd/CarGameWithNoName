# v2: adds boost / manual gears / air pitch logic to BP_CarPawn's event graph.
# Re-runnable: removes the nodes it placed (y >= 3900) before rebuilding them.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_pawn_graph.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
PL = unreal.BlueprintGraphPinLibrary
CAR = "/Game/Car/Blueprints/BP_CarPawn"
Y0 = 4000
try:
    car = unreal.load_asset(CAR)
    graph = BEL.find_event_graph(car)
    ed = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    def pos(nd):
        p = BEL.get_node_pos(nd)
        return (p.x, p.y)
    old = [nd for nd in ed.list_all_nodes() if pos(nd)[1] >= Y0 - 100]
    ed.remove_nodes(old); log("removed old v2 nodes", len(old))
    g = gh.G(ed, log)
    def n(names, x, y, cls=None):
        if isinstance(names, str): names = [names]
        for nm in names:
            nd = ed.create_node_from_name(nm, unreal.Vector2D(x, y), [], cls) if cls else ed.create_node_from_name(nm, unreal.Vector2D(x, y), [])
            if nd is not None: return nd
        log("!! node failed", names); return None
    def title(nd): return str(BEL.get_node_title(nd)).split("\n")[0]
    def find(pred):
        return [nd for nd in ed.list_all_nodes() if pred(nd)]
    mv = lambda x, y: g.var_get("VehicleMovementComponent", x, y)

    # air steadying: share of the air pitch controller that stays on with no throttle/brake held,
    # pulling the pitch spin back toward zero (0 = free spin, 1 = stops as hard as a held key).
    # Off (0) on the regular car so Earth-gravity handling is unchanged; BP_CarPawn_Moon sets its own value (v2_moon_setup.py).
    if "AirStabilize" not in [str(x) for x in BEL.list_member_variable_names(car)]:
        BEL.add_member_variable(car, "AirStabilize", BEL.get_basic_type_by_name("real"))
        BEL.compile_blueprint(car)
    # ---------- defaults that need the compiled class
    cdo = unreal.get_default_object(car.generated_class())
    for k, v in (("BaseFOV", 90.0), ("AirStabilize", 0.0)):
        try: cdo.set_editor_property(k, v)
        except Exception as e: log("default err", k, e)

    # ---------- BeginPlay: speed-lines MID on both cameras, gearbox mode
    amc = find(lambda nd: "AddMappingContext" in title(nd).replace(" ", ""))[0]
    y = Y0
    cdmi = n("Rendering|Material|CreateDynamicMaterialInstance", 300, y, getattr(unreal, "KismetMaterialLibrary", None) or unreal.MaterialLibrary)
    g.val(cdmi, "Parent", "/Game/Car/FX/M_SpeedLines.M_SpeedLines")
    smid = g.var_set("SpeedLinesMID", 650, y)
    g.exe(amc, "then", cdmi); g.exe(cdmi, "then", smid); g.link(cdmi, "ReturnValue", smid, "SpeedLinesMID")
    ab1 = n("Rendering|AddorUpdateBlendable", 950, y, unreal.CameraComponent)
    ab2 = n("Rendering|AddorUpdateBlendable", 1250, y, unreal.CameraComponent)
    g.dump(ab1)
    g.link(g.var_get("ChaseCamera", 800, y + 200), "ChaseCamera", ab1, "self")
    g.link(g.var_get("HoodCamera", 1100, y + 200), "HoodCamera", ab2, "self")
    for ab in (ab1, ab2):
        g.link(smid, "Output_Get", ab, "InBlendableObject"); g.val(ab, "InWeight", "1.0")
    g.exe(smid, "then", ab1); g.exe(ab1, "then", ab2)
    sua = n(["Game|Components|ChaosVehicleMovement|SetUseAutomaticGears"], 1550, y)
    g.dump(sua)
    g.link(mv(1450, y + 200), "VehicleMovementComponent", sua, "self")
    g.link(g.var_get("AutoGears", 1450, y + 280), "AutoGears", sua, "bUseAuto")
    g.exe(ab2, "then", sua)

    # ---------- BeginPlay: copy this level's rules (a BP_LevelRules placed in the map); no rules actor = car defaults
    RULESC = "/Game/Car/Placeholders/BP_LevelRules.BP_LevelRules_C"
    goc = n(["Utilities|GetActorOfClass", "Actor|GetActorOfClass"], 1850, y + 250)
    g.val(goc, "ActorClass", RULESC); g.dump(goc)
    rc = n("Utilities|Casting|CastToBP_LevelRules", 1850, y)
    g.exe(sua, "then", goc); g.exe(goc, "then", rc); g.link(goc, "ReturnValue", rc, "Object")
    rco = [str(PL.get_pin_name(p)) for p in g.pins(rc) if str(PL.get_pin_name(p)).startswith("As")][0]
    def rget(name, x, yy):
        nd = ed.add_get_member_variable_node(name, RULESC)
        if nd is None: log("!! rules get", name); return None
        nd.set_node_pos(unreal.IntPoint(x, yy)); g.link(rc, rco, nd, "self"); return nd
    s_pc = g.var_set("PadsChargeMeter", 2150, y); g.exe(rc, "then", s_pc); g.link(rget("PadsChargeMeter", 2000, y + 250), "PadsChargeMeter", s_pc, "PadsChargeMeter")
    s_ml = g.var_set("MaxLives", 2400, y); g.exe(s_pc, "then", s_ml); g.link(rget("StartingLives", 2250, y + 350), "StartingLives", s_ml, "MaxLives")
    s_lv = g.var_set("Lives", 2650, y); g.exe(s_ml, "then", s_lv); g.link(s_ml, "Output_Get", s_lv, "Lives")
    s_ba = g.var_set("BoostAmount", 2900, y); g.exe(s_lv, "then", s_ba); g.link(rget("StartingBoost", 2750, y + 250), "StartingBoost", s_ba, "BoostAmount")
    # no auto-recharge on this level: regen rate 0 (the regen math in Tick is otherwise untouched)
    rsel = n("Math|Float|SelectFloat", 3000, y + 300)
    g.link(g.var_get("BoostRegenPerSec", 2850, y + 400), "BoostRegenPerSec", rsel, "A"); g.val(rsel, "B", "0.0")
    g.link(rget("BoostRegenEnabled", 2850, y + 500), "BoostRegenEnabled", rsel, "bPickA")
    s_rg = g.var_set("BoostRegenPerSec", 3150, y); g.exe(s_ba, "then", s_rg); g.link(rsel, "ReturnValue", s_rg, "BoostRegenPerSec")

    # ---------- input: boost held
    y = Y0 + 500
    ev = n("Input|EnhancedActionEvents|IA_Boost", 0, y)
    s1 = g.var_set("BoostHeld", 350, y); s0 = g.var_set("BoostHeld", 350, y + 150)
    g.exe(ev, "Started", s1); g.exe(ev, "Completed", s0)
    g.val(s1, "BoostHeld", "true"); g.val(s0, "BoostHeld", "false")

    # ---------- input: pause toggle (IA_Pause triggers while paused; BP_CarHUD draws the pause screen)
    evp = n("Input|EnhancedActionEvents|IA_Pause", 600, y)
    igp = n("Game|IsGamePaused", 600, y + 250)
    ngp = n("Math|Boolean|NOTBoolean", 800, y + 250); g.link(igp, "ReturnValue", ngp, "A")
    sgp = n("Game|SetGamePaused", 900, y); g.exe(evp, "Started", sgp); g.link(ngp, "ReturnValue", sgp, "bPaused")

    # ---------- input: throttle axis copy for air pitch (hook the existing IA_Throttle chain)
    sbs = find(lambda nd: title(nd) == "SetBrakeInput")
    evt = find(lambda nd: "IA_Throttle" in title(nd))[0]
    sbs.sort(key=lambda nd: pos(nd)[1])
    log("brake setters", [pos(x) for x in sbs])
    pa1 = g.var_set("PitchAxis", 1200, y); pa0 = g.var_set("PitchAxis", 1200, y + 150)
    g.exe(sbs[0], "then", pa1); g.exe(sbs[1], "then", pa0)
    g.link(evt, "ActionValue", pa1, "PitchAxis"); g.val(pa0, "PitchAxis", "0.0")

    # ---------- input: auto / manual toggle
    y = Y0 + 800
    ev = n("Input|EnhancedActionEvents|IA_ToggleTransmission", 0, y)
    ag = g.var_get("AutoGears", 150, y + 150)
    nt = n("Math|Boolean|NOTBoolean", 300, y + 150)
    sag = g.var_set("AutoGears", 450, y)
    sua2 = n(["Game|Components|ChaosVehicleMovement|SetUseAutomaticGears"], 750, y)
    g.exe(ev, "Started", sag); g.link(ag, "AutoGears", nt, "A"); g.link(nt, "ReturnValue", sag, "AutoGears")
    g.exe(sag, "then", sua2); g.link(mv(600, y + 200), "VehicleMovementComponent", sua2, "self")
    g.link(sag, "Output_Get", sua2, "bUseAuto")

    # ---------- input: manual shift up / down (skips neutral: 1 <-> R)
    def shifter(action, delta, y):
        ev = n("Input|EnhancedActionEvents|" + action, 0, y)
        br = n("Utilities|FlowControl|Branch", 300, y)
        ag = g.var_get("AutoGears", 100, y + 150)
        nt = n("Math|Boolean|NOTBoolean", 200, y + 150)
        g.exe(ev, "Started", br, "execute"); g.link(ag, "AutoGears", nt, "A"); g.link(nt, "ReturnValue", br, "Condition")
        m = mv(300, y + 250)
        tg = n("Game|Components|ChaosVehicleMovement|GetTargetGear", 450, y + 250)
        g.link(m, "VehicleMovementComponent", tg, "self")
        # the target gear goes stale in automatic, so shift from the current gear; it only reads 0 mid-shift or in neutral
        cg = n("Game|Components|ChaosVehicleMovement|GetCurrentGear", 450, y + 400)
        g.link(m, "VehicleMovementComponent", cg, "self")
        cz = n(["Utilities|Operators|Equal(==)", "Utilities|Operators|Equal"], 500, y + 500)
        g.link(cg, "ReturnValue", cz, "A"); g.val(cz, "B", "0")
        bg = n("Math|Integer|SelectInt", 560, y + 250)
        g.link(tg, "ReturnValue", bg, "A"); g.link(cg, "ReturnValue", bg, "B"); g.link(cz, "ReturnValue", bg, "bPickA")
        ad = n("Utilities|Operators|Add", 650, y + 250); g.link(bg, "ReturnValue", ad, "A"); g.val(ad, "B", str(delta))
        cl = n(["Math|Integer|Clamp(Integer)", "Math|Integer|Clamp(integer)", "Math|Integer|Clamp"], 800, y + 250)
        g.link(ad, "ReturnValue", cl, "Value"); g.val(cl, "Min", "-1")
        g.link(g.var_get("NumForwardGears", 650, y + 380), "NumForwardGears", cl, "Max")
        eq = n(["Utilities|Operators|Equal(==)", "Utilities|Operators|Equal"], 950, y + 350)
        g.link(cl, "ReturnValue", eq, "A"); g.val(eq, "B", "0")
        si = n("Math|Integer|SelectInt", 1100, y + 250)
        g.val(si, "A", str(delta)); g.link(cl, "ReturnValue", si, "B"); g.link(eq, "ReturnValue", si, "bPickA")
        st = n("Game|Components|ChaosVehicleMovement|SetTargetGear", 1300, y)
        g.exe(br, "then", st); g.link(m, "VehicleMovementComponent", st, "self")
        g.link(si, "ReturnValue", st, "GearNum"); g.val(st, "bImmediate", "false")
        g.dump(cl); g.dump(eq); g.dump(st)
    shifter("IA_ShiftUp", 1, Y0 + 1100)
    shifter("IA_ShiftDown", -1, Y0 + 1600)

    # ---------- Tick: boost meter, boost force, FX, air pitch control
    tick = ed.find_event_node("ReceiveTick")
    seq = find(lambda nd: title(nd) == "Sequence")[0]
    names = [str(PL.get_pin_name(p)) for p in g.pins(seq)]
    if "then_2" not in names: ed.add_node_pin(seq)
    y = Y0 + 2200
    dt = lambda x, yy: tick  # DeltaSeconds pin lives on the tick node
    held = g.var_get("BoostHeld", 0, y + 200); amt = g.var_get("BoostAmount", 0, y + 300)
    gt0 = n("Utilities|Operators|Greater(>)", 150, y + 300); g.link(amt, "BoostAmount", gt0, "A"); g.val(gt0, "B", "0.0")
    an = n("Math|Boolean|ANDBoolean", 300, y + 250); g.link(held, "BoostHeld", an, "A"); g.link(gt0, "ReturnValue", an, "B")
    sbst = g.var_set("Boosting", 400, y); g.exe(seq, "then_2", sbst); g.link(an, "ReturnValue", sbst, "Boosting")
    B = lambda: sbst  # Output_Get of the Boosting setter
    # drain / regen
    dr = g.var_get("BoostDrainPerSec", 500, y + 400)
    m1 = n("Utilities|Operators|Multiply", 650, y + 400); g.link(dr, "BoostDrainPerSec", m1, "A"); g.link(tick, "DeltaSeconds", m1, "B")
    sub = n("Utilities|Operators|Subtract", 800, y + 350); g.link(amt, "BoostAmount", sub, "A"); g.link(m1, "ReturnValue", sub, "B")
    mx = n("Math|Float|Max(Float)", 950, y + 350); g.link(sub, "ReturnValue", mx, "A"); g.val(mx, "B", "0.0")
    rg = g.var_get("BoostRegenPerSec", 500, y + 550)
    m2 = n("Utilities|Operators|Multiply", 650, y + 550); g.link(rg, "BoostRegenPerSec", m2, "A"); g.link(tick, "DeltaSeconds", m2, "B")
    add = n("Utilities|Operators|Add", 800, y + 550); g.link(amt, "BoostAmount", add, "A"); g.link(m2, "ReturnValue", add, "B")
    mn = n("Math|Float|Min(Float)", 950, y + 550); g.link(add, "ReturnValue", mn, "A"); g.val(mn, "B", "1.0")
    tmr = g.var_get("BoostRegenTimer", 500, y + 700); dly = g.var_get("BoostRegenDelay", 500, y + 780)
    gtd = n("Utilities|Operators|Greater(>)", 800, y + 720); g.link(tmr, "BoostRegenTimer", gtd, "A"); g.link(dly, "BoostRegenDelay", gtd, "B")
    sf1 = n("Math|Float|SelectFloat", 1100, y + 550); g.link(mn, "ReturnValue", sf1, "A"); g.link(amt, "BoostAmount", sf1, "B"); g.link(gtd, "ReturnValue", sf1, "bPickA")
    sf2 = n("Math|Float|SelectFloat", 1250, y + 400); g.link(mx, "ReturnValue", sf2, "A"); g.link(sf1, "ReturnValue", sf2, "B"); g.link(sbst, "Output_Get", sf2, "bPickA")
    samt = g.var_set("BoostAmount", 1400, y); g.exe(sbst, "then", samt); g.link(sf2, "ReturnValue", samt, "BoostAmount")
    tadd = n("Utilities|Operators|Add", 1250, y + 750); g.link(tmr, "BoostRegenTimer", tadd, "A"); g.link(tick, "DeltaSeconds", tadd, "B")
    sf3 = n("Math|Float|SelectFloat", 1400, y + 700); g.val(sf3, "A", "0.0"); g.link(tadd, "ReturnValue", sf3, "B"); g.link(sbst, "Output_Get", sf3, "bPickA")
    stmr = g.var_set("BoostRegenTimer", 1650, y); g.exe(samt, "then", stmr); g.link(sf3, "ReturnValue", stmr, "BoostRegenTimer")
    # on/off as 1/0
    on = n("Math|Float|SelectFloat", 1650, y + 300); g.val(on, "A", "1.0"); g.val(on, "B", "0.0"); g.link(sbst, "Output_Get", on, "bPickA")
    # boost pad push: 1/0 while the pad timer runs (timer counts down in the then_3 chain)
    pgt = n("Utilities|Operators|Greater(>)", 1650, y + 950); g.link(g.var_get("PadBoostTimer", 1500, y + 950), "PadBoostTimer", pgt, "A"); g.val(pgt, "B", "0.0")
    pon = n("Math|Float|SelectFloat", 1800, y + 950); g.val(pon, "A", "1.0"); g.val(pon, "B", "0.0"); g.link(pgt, "ReturnValue", pon, "bPickA")
    fxt = n("Math|Float|Max(Float)", 1950, y + 900); g.link(on, "ReturnValue", fxt, "A"); g.link(pon, "ReturnValue", fxt, "B")
    # force
    fwd = n("Transformation|GetActorForwardVector", 1700, y + 450)
    acc = g.var_get("BoostAccel", 1700, y + 550)
    fm = n("Utilities|Operators|Multiply", 1900, y + 500); g.link(acc, "BoostAccel", fm, "A"); g.link(on, "ReturnValue", fm, "B")
    fv = n("Utilities|Operators|Multiply", 2050, y + 450); g.link(fwd, "ReturnValue", fv, "A"); g.link(fm, "ReturnValue", fv, "B")
    af = n("Physics|AddForce", 2200, y)
    g.exe(stmr, "then", af); g.link(g.var_get("Mesh", 2050, y + 200), "Mesh", af, "self")
    g.link(fv, "ReturnValue", af, "Force"); g.val(af, "bAccelChange", "true")
    g.dump(af); g.dump(fv)
    # FX alpha
    fxg = g.var_get("BoostFX", 2200, y + 500)
    fi = n("Math|Interpolation|FInterpTo", 2400, y + 450)
    g.link(fxg, "BoostFX", fi, "Current"); g.link(fxt, "ReturnValue", fi, "Target"); g.link(tick, "DeltaSeconds", fi, "DeltaTime"); g.val(fi, "InterpSpeed", "6.0")
    sfx = g.var_set("BoostFX", 2550, y); g.exe(af, "then", sfx); g.link(fi, "ReturnValue", sfx, "BoostFX")
    FXO = (sfx, "Output_Get")
    # speed lines
    ssp = n("Rendering|Material|SetScalarParameterValue", 2800, y, unreal.MaterialInstanceDynamic)
    g.exe(sfx, "then", ssp); g.link(g.var_get("SpeedLinesMID", 2650, y + 200), "SpeedLinesMID", ssp, "self")
    g.val(ssp, "ParameterName", "Intensity"); g.link(*FXO, ssp, "Value")
    g.dump(ssp)
    # flames
    rnd = n("Math|Random|RandomFloatinRange", 2800, y + 450); g.val(rnd, "Min", "0.75"); g.val(rnd, "Max", "1.25")
    w = n("Utilities|Operators|Multiply", 3000, y + 350); g.link(*FXO, w, "A"); g.val(w, "B", "0.32")
    ln1 = n("Utilities|Operators|Multiply", 3000, y + 450); g.link(*FXO, ln1, "A"); g.link(rnd, "ReturnValue", ln1, "B")
    ln = n("Utilities|Operators|Multiply", 3150, y + 450); g.link(ln1, "ReturnValue", ln, "A"); g.val(ln, "B", "0.75")
    mvk = n("Math|Vector|MakeVector", 3300, y + 350)
    g.link(w, "ReturnValue", mvk, "X"); g.link(w, "ReturnValue", mvk, "Y"); g.link(ln, "ReturnValue", mvk, "Z")
    prev = ssp
    for i, nm in enumerate(("BoostFlameL", "BoostFlameR")):
        srs = n("Transformation|SetRelativeScale3D", 3100 + i * 300, y)
        g.exe(prev, "then", srs); g.link(g.var_get(nm, 3000 + i * 300, y + 200), nm, srs, "self")
        g.link(mvk, "ReturnValue", srs, "NewScale3D"); prev = srs
    li = n("Utilities|Operators|Multiply", 3550, y + 450); g.link(ln1, "ReturnValue", li, "A"); g.val(li, "B", "80.0")
    si = n(["Rendering|Lighting|SetIntensity", "Rendering|Components|Light|SetIntensity"], 3700, y)
    g.exe(prev, "then", si); g.link(g.var_get("BoostLight", 3600, y + 200), "BoostLight", si, "self")
    g.link(li, "ReturnValue", si, "NewIntensity")
    g.dump(si)
    # FOV kick
    fk = n("Utilities|Operators|Multiply", 3850, y + 350); g.link(*FXO, fk, "A"); g.val(fk, "B", "14.0")
    fa = n("Utilities|Operators|Add", 4000, y + 350); g.link(g.var_get("BaseFOV", 3850, y + 450), "BaseFOV", fa, "A"); g.link(fk, "ReturnValue", fa, "B")
    sfov = n(["Camera|SetFieldOfView", "Rendering|SetFieldOfView", "Camera|Camera|SetFieldOfView"], 4000, y)
    g.exe(si, "then", sfov); g.link(g.var_get("ChaseCamera", 3900, y + 200), "ChaseCamera", sfov, "self")
    g.link(fa, "ReturnValue", sfov, "InFieldOfView")
    g.dump(sfov)
    # air check: short trace straight down from the car
    y2 = y + 1000
    loc = n("Transformation|GetActorLocation", 4100, y2 + 200)
    up = n("Utilities|Operators|Add", 4300, y2 + 150); g.link(loc, "ReturnValue", up, "A"); g.val(up, "B", "(X=0.000000,Y=0.000000,Z=40.000000)")
    dn = n("Utilities|Operators|Add", 4300, y2 + 300); g.link(loc, "ReturnValue", dn, "A"); g.val(dn, "B", "(X=0.000000,Y=0.000000,Z=-75.000000)")
    lt = n("Collision|LineTraceByChannel", 4500, y2)
    g.exe(sfov, "then", lt); g.link(up, "ReturnValue", lt, "Start"); g.link(dn, "ReturnValue", lt, "End")
    g.dump(lt)
    nh = n("Math|Boolean|NOTBoolean", 4800, y2 + 200); g.link(lt, "ReturnValue", nh, "A")
    sair = g.var_set("InAir", 4950, y2); g.exe(lt, "then", sair); g.link(nh, "ReturnValue", sair, "InAir")
    # pitch rate controller, only while airborne: full strength while throttle/brake is held, AirStabilize share otherwise
    # (with no key held the target rate is 0, so it just bleeds off the spin)
    rv = n("Transformation|GetActorRightVector", 4900, y2 + 400)
    avd = n("Physics|GetPhysicsAngularVelocityinDegrees", 4900, y2 + 550)
    g.link(g.var_get("Mesh", 4750, y2 + 550), "Mesh", avd, "self")
    dot = n("Math|Vector|DotProduct", 5100, y2 + 500); g.link(avd, "ReturnValue", dot, "A"); g.link(rv, "ReturnValue", dot, "B")
    pa = g.var_get("PitchAxis", 4900, y2 + 700)
    tr = n("Utilities|Operators|Multiply", 5100, y2 + 700); g.link(pa, "PitchAxis", tr, "A"); g.link(g.var_get("AirPitchRate", 4900, y2 + 800), "AirPitchRate", tr, "B")
    er = n("Utilities|Operators|Subtract", 5300, y2 + 600); g.link(tr, "ReturnValue", er, "A"); g.link(dot, "ReturnValue", er, "B")
    rs = n("Utilities|Operators|Multiply", 5450, y2 + 600); g.link(er, "ReturnValue", rs, "A"); g.link(g.var_get("AirPitchResponse", 5300, y2 + 750), "AirPitchResponse", rs, "B")
    ab = n("Math|Float|Absolute(Float)", 5300, y2 + 850); g.link(pa, "PitchAxis", ab, "A")
    mx = n(["Math|Float|Max(Float)", "Math|Float|Max"], 5450, y2 + 900); g.link(ab, "ReturnValue", mx, "A"); g.link(g.var_get("AirStabilize", 5300, y2 + 950), "AirStabilize", mx, "B")
    rs2 = n("Utilities|Operators|Multiply", 5600, y2 + 650); g.link(rs, "ReturnValue", rs2, "A"); g.link(mx, "ReturnValue", rs2, "B")
    airf = n("Math|Float|SelectFloat", 5600, y2 + 850); g.val(airf, "A", "1.0"); g.val(airf, "B", "0.0"); g.link(sair, "Output_Get", airf, "bPickA")
    rs3 = n("Utilities|Operators|Multiply", 5750, y2 + 700); g.link(rs2, "ReturnValue", rs3, "A"); g.link(airf, "ReturnValue", rs3, "B")
    tv = n("Utilities|Operators|Multiply", 5900, y2 + 500); g.link(rv, "ReturnValue", tv, "A"); g.link(rs3, "ReturnValue", tv, "B")
    at = n(["Physics|AddTorqueinDegrees", "Physics|AddTorqueInDegrees"], 5200, y2)
    g.exe(sair, "then", at); g.link(g.var_get("Mesh", 5100, y2 + 200), "Mesh", at, "self")
    g.link(tv, "ReturnValue", at, "Torque"); g.val(at, "bAccelChange", "true")
    g.dump(at); g.dump(tv)

    # ---------- Tick (then_3): pad boost + hit cooldown timers, pad push force, out of lives
    names = [str(PL.get_pin_name(p)) for p in g.pins(seq)]
    if "then_3" not in names: ed.add_node_pin(seq)
    y3 = Y0 + 4600
    prev = None
    for i, var in enumerate(("PadBoostTimer", "HitCooldown")):
        vg = g.var_get(var, 0, y3 + 300 + i * 150)
        sb = n("Utilities|Operators|Subtract", 200, y3 + 300 + i * 150); g.link(vg, var, sb, "A"); g.link(tick, "DeltaSeconds", sb, "B")
        mz = n("Math|Float|Max(Float)", 350, y3 + 300 + i * 150); g.link(sb, "ReturnValue", mz, "A"); g.val(mz, "B", "0.0")
        sv = g.var_set(var, 300 + i * 250, y3); g.link(mz, "ReturnValue", sv, var)
        if prev is None: g.exe(seq, "then_3", sv)
        else: g.exe(prev, "then", sv)
        prev = sv
    fwd2 = n("Transformation|GetActorForwardVector", 700, y3 + 300)
    pm = n("Utilities|Operators|Multiply", 850, y3 + 400); g.link(g.var_get("PadAccel", 700, y3 + 450), "PadAccel", pm, "A"); g.link(pon, "ReturnValue", pm, "B")
    pf = n("Utilities|Operators|Multiply", 1000, y3 + 300); g.link(fwd2, "ReturnValue", pf, "A"); g.link(pm, "ReturnValue", pf, "B")
    af2 = n("Physics|AddForce", 1000, y3)
    g.exe(prev, "then", af2); g.link(g.var_get("Mesh", 850, y3 + 200), "Mesh", af2, "self")
    g.link(pf, "ReturnValue", af2, "Force"); g.val(af2, "bAccelChange", "true")
    # out of lives (once): stop the car and take driving input away
    le0 = n(["Utilities|Operators|LessEqual(<=)", "Utilities|Operators|LessEqual"], 1250, y3 + 300); g.link(g.var_get("Lives", 1100, y3 + 300), "Lives", le0, "A"); g.val(le0, "B", "0")
    nol = n("Math|Boolean|NOTBoolean", 1250, y3 + 420); g.link(g.var_get("OutOfLives", 1100, y3 + 420), "OutOfLives", nol, "A")
    an0 = n("Math|Boolean|ANDBoolean", 1400, y3 + 350); g.link(le0, "ReturnValue", an0, "A"); g.link(nol, "ReturnValue", an0, "B")
    bro = n("Utilities|FlowControl|Branch", 1300, y3); g.exe(af2, "then", bro); g.link(an0, "ReturnValue", bro, "Condition")
    sol = g.var_set("OutOfLives", 1550, y3); g.exe(bro, "then", sol); g.val(sol, "OutOfLives", "true")
    sti = n("Game|Components|ChaosVehicleMovement|SetThrottleInput", 1800, y3); g.exe(sol, "then", sti); g.link(mv(1700, y3 + 200), "VehicleMovementComponent", sti, "self"); g.val(sti, "Throttle", "0.0")
    shb = n("Game|Components|ChaosVehicleMovement|SetHandbrakeInput", 2050, y3); g.exe(sti, "then", shb); g.link(mv(1950, y3 + 200), "VehicleMovementComponent", shb, "self"); g.val(shb, "bNewHandbrake", "true")
    gpc = n("Game|GetPlayerController", 2150, y3 + 250)
    dis = n("Input|DisableInput", 2300, y3); g.exe(shb, "then", dis); g.link(gpc, "ReturnValue", dis, "PlayerController")
    # BP_CarHUD sees OutOfLives and shows the game over screen (retry / level select / title)
    g.dump(dis); g.dump(shb)

    # ---------- refresh the on-screen controls hint
    for nd in find(lambda nd: title(nd) == "Append"):
        g.val(nd, "D", "    [W/S drive  A/D steer  Space handbrake  Shift boost  T auto/manual  E/Q gear up/down  R reset  C camera]")

    BEL.compile_blueprint(car)
    for nd in ed.list_nodes_with_errors(): log("ERROR node", title(nd))
    for nd in ed.list_nodes_with_warnings(): log("WARN node", title(nd))
    log("saved", EAL.save_asset(CAR, only_if_is_dirty=False))
    log("nodes", len(ed.list_all_nodes()))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_PAWN_DONE")
