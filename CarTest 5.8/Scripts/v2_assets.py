# v2: boost / gears / air-control / antenna — assets, inputs, transmission, components, variables
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_assets.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
CAR = "/Game/Car/Blueprints/BP_CarPawn"
FX = "/Game/Car/FX"

def mexp(mat, cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)
def con(a, ao, b, bi):
    ok = MEL.connect_material_expressions(a, ao, b, bi)
    if not ok: log("!! mat link failed", a.get_name(), ao, "->", b.get_name(), bi)
    return ok

def new_material(name):
    path = FX + "/" + name
    if EAL.does_asset_exist(path):
        m = unreal.load_asset(path)
        MEL.delete_all_material_expressions(m)
        return m
    return AT.create_asset(name, FX, unreal.Material, unreal.MaterialFactoryNew())

try:
    # ---------------- flame material (additive, unlit, flickering)
    m = new_material("M_BoostFlame")
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    col = mexp(m, unreal.MaterialExpressionVectorParameter, -900, 0)
    col.set_editor_property("parameter_name", "FlameColor"); col.set_editor_property("default_value", unreal.LinearColor(1.0, 0.32, 0.04, 1))
    core = mexp(m, unreal.MaterialExpressionVectorParameter, -900, 200)
    core.set_editor_property("parameter_name", "CoreColor"); core.set_editor_property("default_value", unreal.LinearColor(1.0, 0.85, 0.55, 1))
    fr = mexp(m, unreal.MaterialExpressionFresnel, -900, 400); fr.set_editor_property("exponent", 1.5)
    om = mexp(m, unreal.MaterialExpressionOneMinus, -700, 400); con(fr, "", om, "")
    lp = mexp(m, unreal.MaterialExpressionLinearInterpolate, -500, 100)
    con(col, "", lp, "A"); con(core, "", lp, "B"); con(om, "", lp, "Alpha")
    tm = mexp(m, unreal.MaterialExpressionTime, -900, 600)
    k = mexp(m, unreal.MaterialExpressionConstant, -900, 700); k.set_editor_property("r", 7.0)
    tk = mexp(m, unreal.MaterialExpressionMultiply, -700, 600); con(tm, "", tk, "A"); con(k, "", tk, "B")
    sn = mexp(m, unreal.MaterialExpressionSine, -550, 600); con(tk, "", sn, "")
    fl = mexp(m, unreal.MaterialExpressionMultiply, -400, 600); con(sn, "", fl, "A")
    c25 = mexp(m, unreal.MaterialExpressionConstant, -550, 700); c25.set_editor_property("r", 0.25); con(c25, "", fl, "B")
    fl2 = mexp(m, unreal.MaterialExpressionAdd, -250, 600); con(fl, "", fl2, "A")
    c1 = mexp(m, unreal.MaterialExpressionConstant, -400, 700); c1.set_editor_property("r", 1.0); con(c1, "", fl2, "B")
    inten = mexp(m, unreal.MaterialExpressionScalarParameter, -400, 300)
    inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 12.0)
    e1 = mexp(m, unreal.MaterialExpressionMultiply, -250, 100); con(lp, "", e1, "A"); con(inten, "", e1, "B")
    e2 = mexp(m, unreal.MaterialExpressionMultiply, -100, 100); con(e1, "", e2, "A"); con(fl2, "", e2, "B")
    MEL.connect_material_property(e2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_asset(FX + "/M_BoostFlame")
    log("flame material ok")

    # ---------------- speed-lines post-process material
    s = new_material("M_SpeedLines")
    s.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    try: s.set_editor_property("blendable_location", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
    except Exception as e: log("blendable loc", e)
    uv = mexp(s, unreal.MaterialExpressionTextureCoordinate, -1600, 0)
    half = mexp(s, unreal.MaterialExpressionConstant2Vector, -1600, 120); half.set_editor_property("r", 0.5); half.set_editor_property("g", 0.5)
    d = mexp(s, unreal.MaterialExpressionSubtract, -1450, 50); con(uv, "", d, "A"); con(half, "", d, "B")
    mx = mexp(s, unreal.MaterialExpressionComponentMask, -1300, 0); mx.set_editor_property("r", True); mx.set_editor_property("g", False); con(d, "", mx, "")
    my = mexp(s, unreal.MaterialExpressionComponentMask, -1300, 100); my.set_editor_property("r", False); my.set_editor_property("g", True); con(d, "", my, "")
    at2 = mexp(s, unreal.MaterialExpressionArctangent2, -1150, 50); con(my, "", at2, "Y"); con(mx, "", at2, "X")
    rad = mexp(s, unreal.MaterialExpressionLength, -1150, 250); con(d, "", rad, "")
    k40 = mexp(s, unreal.MaterialExpressionConstant, -1150, 150); k40.set_editor_property("r", 38.0)
    a40 = mexp(s, unreal.MaterialExpressionMultiply, -1000, 50); con(at2, "", a40, "A"); con(k40, "", a40, "B")
    slc = mexp(s, unreal.MaterialExpressionFloor, -880, 50); con(a40, "", slc, "")
    tme = mexp(s, unreal.MaterialExpressionTime, -1150, 400)
    k24 = mexp(s, unreal.MaterialExpressionConstant, -1150, 480); k24.set_editor_property("r", 18.0)
    t24 = mexp(s, unreal.MaterialExpressionMultiply, -1000, 400); con(tme, "", t24, "A"); con(k24, "", t24, "B")
    tfl = mexp(s, unreal.MaterialExpressionFloor, -880, 400); con(t24, "", tfl, "")
    h1k = mexp(s, unreal.MaterialExpressionConstant, -880, 150); h1k.set_editor_property("r", 12.9898)
    h1 = mexp(s, unreal.MaterialExpressionMultiply, -750, 50); con(slc, "", h1, "A"); con(h1k, "", h1, "B")
    h2k = mexp(s, unreal.MaterialExpressionConstant, -880, 500); h2k.set_editor_property("r", 78.233)
    h2 = mexp(s, unreal.MaterialExpressionMultiply, -750, 400); con(tfl, "", h2, "A"); con(h2k, "", h2, "B")
    hs = mexp(s, unreal.MaterialExpressionAdd, -620, 200); con(h1, "", hs, "A"); con(h2, "", hs, "B")
    hsin = mexp(s, unreal.MaterialExpressionSine, -500, 200); con(hs, "", hsin, "")
    hbk = mexp(s, unreal.MaterialExpressionConstant, -500, 300); hbk.set_editor_property("r", 4375.85)
    hb = mexp(s, unreal.MaterialExpressionMultiply, -380, 200); con(hsin, "", hb, "A"); con(hbk, "", hb, "B")
    hf = mexp(s, unreal.MaterialExpressionFrac, -260, 200); con(hb, "", hf, "")
    thr = mexp(s, unreal.MaterialExpressionConstant, -260, 300); thr.set_editor_property("r", 0.86)
    hm = mexp(s, unreal.MaterialExpressionSubtract, -140, 200); con(hf, "", hm, "A"); con(thr, "", hm, "B")
    k6 = mexp(s, unreal.MaterialExpressionConstant, -140, 300); k6.set_editor_property("r", 6.0)
    hx = mexp(s, unreal.MaterialExpressionMultiply, -20, 200); con(hm, "", hx, "A"); con(k6, "", hx, "B")
    line = mexp(s, unreal.MaterialExpressionSaturate, 100, 200); con(hx, "", line, "")
    r0 = mexp(s, unreal.MaterialExpressionConstant, -1000, 300); r0.set_editor_property("r", 0.24)
    rm = mexp(s, unreal.MaterialExpressionSubtract, -880, 250); con(rad, "", rm, "A"); con(r0, "", rm, "B")
    k35 = mexp(s, unreal.MaterialExpressionConstant, -880, 330); k35.set_editor_property("r", 3.0)
    rx = mexp(s, unreal.MaterialExpressionMultiply, -750, 250); con(rm, "", rx, "A"); con(k35, "", rx, "B")
    mask = mexp(s, unreal.MaterialExpressionSaturate, -620, 300); con(rx, "", mask, "")
    st1 = mexp(s, unreal.MaterialExpressionMultiply, 220, 250); con(line, "", st1, "A"); con(mask, "", st1, "B")
    ip = mexp(s, unreal.MaterialExpressionScalarParameter, 220, 400); ip.set_editor_property("parameter_name", "Intensity"); ip.set_editor_property("default_value", 0.0)
    st2 = mexp(s, unreal.MaterialExpressionMultiply, 360, 300); con(st1, "", st2, "A"); con(ip, "", st2, "B")
    k07 = mexp(s, unreal.MaterialExpressionConstant, 360, 420); k07.set_editor_property("r", 0.4)
    st3 = mexp(s, unreal.MaterialExpressionMultiply, 480, 300); con(st2, "", st3, "A"); con(k07, "", st3, "B")
    sc = mexp(s, unreal.MaterialExpressionSceneTexture, 220, 0)
    sc.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
    scm = mexp(s, unreal.MaterialExpressionComponentMask, 380, 0)
    for ch, v in (("r", True), ("g", True), ("b", True), ("a", False)): scm.set_editor_property(ch, v)
    con(sc, "Color", scm, "")
    wh = mexp(s, unreal.MaterialExpressionConstant3Vector, 380, 120); wh.set_editor_property("constant", unreal.LinearColor(1.0, 1.0, 1.0, 1))
    out = mexp(s, unreal.MaterialExpressionLinearInterpolate, 620, 50)
    con(scm, "", out, "A"); con(wh, "", out, "B"); con(st3, "", out, "Alpha")
    MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(s); EAL.save_asset(FX + "/M_SpeedLines")
    log("speedlines material ok")

    # ---------------- input actions + mappings
    def ia(name, vt):
        path = "/Game/Car/Input/" + name
        if EAL.does_asset_exist(path): return unreal.load_asset(path)
        a = AT.create_asset(name, "/Game/Car/Input", unreal.InputAction, unreal.InputAction_Factory())
        a.set_editor_property("value_type", vt); EAL.save_asset(path); return a
    B = unreal.InputActionValueType.BOOLEAN
    acts = {n: ia(n, B) for n in ("IA_Boost", "IA_ShiftUp", "IA_ShiftDown", "IA_ToggleTransmission")}
    imc = unreal.load_asset("/Game/Car/Input/IMC_Car")
    have = set()
    for mp in imc.get_editor_property("default_key_mappings").get_editor_property("mappings"):
        have.add((mp.get_editor_property("action").get_name(), str(mp.get_editor_property("key").get_editor_property("key_name"))))
    def key(n): k = unreal.Key(); k.set_editor_property("key_name", n); return k
    want = [("IA_Boost", "LeftShift"), ("IA_Boost", "Gamepad_FaceButton_Left"),
            ("IA_ShiftUp", "E"), ("IA_ShiftUp", "Gamepad_RightShoulder"),
            ("IA_ShiftDown", "Q"), ("IA_ShiftDown", "Gamepad_LeftShoulder"),
            ("IA_ToggleTransmission", "T"), ("IA_ToggleTransmission", "Gamepad_DPad_Up")]
    for an, kn in want:
        if (an, kn) not in have:
            imc.map_key(acts[an], key(kn)); log("mapped", an, kn)
    EAL.save_asset("/Game/Car/Input/IMC_Car")
    for mp in imc.get_editor_property("default_key_mappings").get_editor_property("mappings"):
        log(" map", mp.get_editor_property("action").get_name(), mp.get_editor_property("key").get_editor_property("key_name"))

    # ---------------- car: transmission, components, variables
    car = unreal.load_asset(CAR)
    comps = {}
    def gather():
        comps.clear()
        for h in SDS.k2_gather_subobject_data_for_blueprint(car):
            dd = SDS.k2_find_subobject_data_from_handle(h)
            comps[str(SDL.get_variable_name(dd))] = (h, SDL.get_object(dd))
    gather()
    mv = comps["VehicleMovementComponent"][1]
    tr = mv.get_editor_property("transmission_setup")
    tr.set_editor_property("forward_gear_ratios", [3.60, 2.40, 1.78, 1.38, 1.10, 0.90])
    tr.set_editor_property("reverse_gear_ratios", [3.20])
    tr.set_editor_property("final_ratio", 3.40)
    tr.set_editor_property("change_up_rpm", 6000.0)
    tr.set_editor_property("change_down_rpm", 3000.0)
    tr.set_editor_property("gear_change_time", 0.20)
    tr.set_editor_property("use_automatic_gears", True)
    mv.set_editor_property("transmission_setup", tr)
    eng = mv.get_editor_property("engine_setup")
    eng.set_editor_property("max_rpm", 7000.0)
    eng.set_editor_property("max_torque", 420.0)
    mv.set_editor_property("engine_setup", eng)
    log("trans", mv.get_editor_property("transmission_setup").export_text())
    for nm in ("ChaseCamera", "HoodCamera"):
        if nm in comps: log("fov", nm, comps[nm][1].get_editor_property("field_of_view"))
    root_h = comps["Mesh"][0]
    cone = unreal.load_asset("/Engine/BasicShapes/Cone")
    flame_mat = unreal.load_asset(FX + "/M_BoostFlame")
    def add(cls, name, parent):
        if name in comps: return comps[name][1]
        prm = unreal.AddNewSubobjectParams(parent_handle=parent, new_class=cls, blueprint_context=car)
        h, fail = SDS.add_new_subobject(prm)
        SDS.rename_subobject_member_variable(car, h, name)
        gather()
        return comps[name][1]
    for nm, y in (("BoostFlameL", -46.0), ("BoostFlameR", 46.0)):
        c = add(unreal.StaticMeshComponent, nm, root_h)
        c.set_editor_property("static_mesh", cone)
        c.set_editor_property("override_materials", [flame_mat])
        c.set_editor_property("relative_location", unreal.Vector(-150.0, y, 32.0))
        c.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0))
        c.set_editor_property("relative_scale3d", unreal.Vector(0.001, 0.001, 0.001))
        c.set_editor_property("cast_shadow", False)
        c.set_collision_profile_name("NoCollision")
        c.set_editor_property("generate_overlap_events", False)
        log("comp", nm, c.get_editor_property("relative_location"), c.get_editor_property("relative_rotation"))
    lt = add(unreal.PointLightComponent, "BoostLight", root_h)
    lt.set_editor_property("relative_location", unreal.Vector(-175.0, 0.0, 35.0))
    lt.set_editor_property("intensity", 0.0)
    lt.set_editor_property("light_color", unreal.Color(r=255, g=120, b=30, a=255))
    lt.set_editor_property("attenuation_radius", 450.0)
    lt.set_editor_property("cast_shadows", False)
    log("comps", sorted(comps.keys()))

    have = [str(x) for x in BEL.list_member_variable_names(car)]
    R, Bo, I = BEL.get_basic_type_by_name("real"), BEL.get_basic_type_by_name("bool"), BEL.get_basic_type_by_name("int")
    newvars = [("BoostAmount", R), ("BoostHeld", Bo), ("Boosting", Bo), ("BoostRegenTimer", R), ("BoostFX", R),
               ("BoostDrainPerSec", R), ("BoostRegenPerSec", R), ("BoostRegenDelay", R), ("BoostAccel", R),
               ("BaseFOV", R), ("AutoGears", Bo), ("NumForwardGears", I),
               ("PitchAxis", R), ("InAir", Bo), ("AirPitchRate", R), ("AirPitchResponse", R)]
    for nm, tp in newvars:
        if nm not in have: BEL.add_member_variable(car, nm, tp)
    try:
        objt = BEL.get_object_reference_type(unreal.MaterialInstanceDynamic) if hasattr(BEL, "get_object_reference_type") else None
    except Exception as e:
        objt = None; log("objref err", e)
    log("objref type", objt)
    if objt is not None and "SpeedLinesMID" not in have:
        BEL.add_member_variable(car, "SpeedLinesMID", objt)
    for nm in ("BoostDrainPerSec", "BoostRegenPerSec", "BoostRegenDelay", "BoostAccel", "AirPitchRate", "AirPitchResponse", "AutoGears", "NumForwardGears", "BoostAmount"):
        BEL.set_blueprint_variable_instance_editable(car, nm, True)
        BEL.set_blueprint_variable_category(car, nm, "Car Tuning")
    BEL.compile_blueprint(car)
    cdo = unreal.get_default_object(car.generated_class())
    defaults = {"BoostAmount": 1.0, "BoostDrainPerSec": 0.25, "BoostRegenPerSec": 0.06, "BoostRegenDelay": 1.5,
                "BoostAccel": 650.0, "AutoGears": True, "NumForwardGears": 6, "AirPitchRate": 55.0, "AirPitchResponse": 2.5}
    for k, v in defaults.items():
        done = False
        for nm in (k, unreal.StringLibrary.conv_name_to_string(k)):
            try: cdo.set_editor_property(nm, v); done = True; break
            except Exception as e: err = e
        if not done:
            import re
            sn = re.sub(r"(?<!^)(?=[A-Z])", "_", k).lower()
            try: cdo.set_editor_property(sn, v); done = True
            except Exception as e: log("!! default", k, e)
        log("default", k, v, done)
    BEL.compile_blueprint(car)
    EAL.save_asset(CAR)
    log("vars", [x for x in [str(v) for v in BEL.list_member_variable_names(car)] if not x.startswith("/Script")])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_ASSETS_DONE")
