import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_build2.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary

def setp(obj, name, val):
    try:
        obj.set_editor_property(name, val); return True
    except Exception as e:
        p("  !set", obj.get_name(), name, e); return False

def make_bp(path, parent):
    if EAL.does_asset_exist(path):
        return unreal.load_asset(path)
    pkg, name = path.rsplit("/", 1)
    f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", parent)
    return AT.create_asset(name, pkg, unreal.Blueprint, f)

try:
    mesh = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    # ---------- physics asset
    if not mesh.physics_asset:
        pa = unreal.EditorSkeletalMeshLibrary.create_physics_asset(mesh)
        p("physics asset", pa)
    p("mesh physics", mesh.physics_asset)
    EAL.save_asset("/Game/Car/Mesh/SK_Car")

    # ---------- wheels
    def wheel(path, front):
        bp = make_bp(path, unreal.ChaosVehicleWheel)
        cdo = unreal.get_default_object(bp.generated_class())
        setp(cdo, "axle_type", unreal.AxleType.FRONT if front else unreal.AxleType.REAR)
        setp(cdo, "wheel_radius", 23.5)
        setp(cdo, "wheel_width", 22.0)
        setp(cdo, "wheel_mass", 20.0)
        setp(cdo, "affected_by_steering", front)
        setp(cdo, "max_steer_angle", 38.0 if front else 0.0)
        setp(cdo, "affected_by_brake", True)
        setp(cdo, "affected_by_handbrake", not front)
        setp(cdo, "affected_by_engine", True)
        setp(cdo, "max_brake_torque", 1800.0)
        setp(cdo, "max_hand_brake_torque", 3500.0 if not front else 0.0)
        setp(cdo, "friction_force_multiplier", 3.0 if front else 2.8)
        setp(cdo, "cornering_stiffness", 1000.0)
        setp(cdo, "suspension_max_raise", 8.0)
        setp(cdo, "suspension_max_drop", 10.0)
        setp(cdo, "spring_rate", 250.0)
        setp(cdo, "spring_preload", 50.0)
        setp(cdo, "suspension_damping_ratio", 0.5)
        setp(cdo, "suspension_smoothing", 4)
        setp(cdo, "rollbar_scaling", 0.5)
        BEL.compile_blueprint(bp); EAL.save_asset(path)
        return bp
    wf = wheel("/Game/Car/Blueprints/BP_Wheel_Front", True)
    wr = wheel("/Game/Car/Blueprints/BP_Wheel_Rear", False)

    # ---------- input actions
    def ia(name, vt):
        path = "/Game/Car/Input/" + name
        if EAL.does_asset_exist(path): return unreal.load_asset(path)
        a = AT.create_asset(name, "/Game/Car/Input", unreal.InputAction, unreal.InputAction_Factory())
        a.set_editor_property("value_type", vt); EAL.save_asset(path); return a
    A1, A2, B = unreal.InputActionValueType.AXIS1D, unreal.InputActionValueType.AXIS2D, unreal.InputActionValueType.BOOLEAN
    ia_thr = ia("IA_Throttle", A1)   # W / RT  (+)   S / LT (-) -> brake & reverse
    ia_steer = ia("IA_Steer", A1)
    ia_hb = ia("IA_Handbrake", B)
    ia_look = ia("IA_Look", A2)
    ia_reset = ia("IA_Reset", B)
    ia_cam = ia("IA_ToggleCamera", B)
    imc_path = "/Game/Car/Input/IMC_Car"
    imc = unreal.load_asset(imc_path) if EAL.does_asset_exist(imc_path) else AT.create_asset("IMC_Car", "/Game/Car/Input", unreal.InputMappingContext, unreal.InputMappingContext_Factory())
    imc.unmap_all()
    def key(n): k = unreal.Key(); k.set_editor_property("key_name", n); return k
    def mp(action, keyname, negate=False, swizzle=False):
        m = imc.map_key(action, key(keyname))
        mods = []
        if swizzle: mods.append(unreal.InputModifierSwizzleAxis())
        if negate: mods.append(unreal.InputModifierNegate())
        if mods: m.set_editor_property("modifiers", mods)
        # map_key returns a copy in some versions; re-fetch
        return m
    mp(ia_thr, "W"); mp(ia_thr, "Up"); mp(ia_thr, "Gamepad_RightTriggerAxis")
    mp(ia_thr, "S", negate=True); mp(ia_thr, "Down", negate=True); mp(ia_thr, "Gamepad_LeftTriggerAxis", negate=True)
    mp(ia_steer, "D"); mp(ia_steer, "Right"); mp(ia_steer, "A", negate=True); mp(ia_steer, "Left", negate=True)
    mp(ia_steer, "Gamepad_LeftX")
    mp(ia_hb, "SpaceBar"); mp(ia_hb, "Gamepad_FaceButton_Bottom")
    mp(ia_look, "Mouse2D"); mp(ia_look, "Gamepad_Right2D")
    mp(ia_reset, "R"); mp(ia_reset, "Gamepad_Special_Right")
    mp(ia_cam, "C"); mp(ia_cam, "Gamepad_FaceButton_Top")
    # modifiers: map_key may hand back a copy, so rebuild via the mappings array
    maps = list(imc.get_editor_property("mappings"))
    negs = {("IA_Throttle","S"),("IA_Throttle","Down"),("IA_Throttle","Gamepad_LeftTriggerAxis"),("IA_Steer","A"),("IA_Steer","Left")}
    for m in maps:
        an = m.get_editor_property("action").get_name(); kn = str(m.get_editor_property("key").get_editor_property("key_name"))
        if (an, kn) in negs:
            m.set_editor_property("modifiers", [unreal.InputModifierNegate()])
    imc.set_editor_property("mappings", maps)
    for m in imc.get_editor_property("mappings"):
        p("map", m.get_editor_property("action").get_name(), m.get_editor_property("key").get_editor_property("key_name"), [type(x).__name__ for x in m.get_editor_property("modifiers")])
    EAL.save_asset(imc_path)
    # default mapping context for all local players
    try:
        s = unreal.get_default_object(unreal.EnhancedInputDeveloperSettings)
        dmc = unreal.DefaultContextSetting()
        dmc.set_editor_property("input_mapping_context", imc)
        dmc.set_editor_property("priority", 0)
        setp(s, "default_mapping_contexts", [dmc])
        setp(s, "enable_default_mapping_contexts", True)
        s.save_config() if hasattr(s, "save_config") else None
        p("default ctx", s.get_editor_property("default_mapping_contexts"))
    except Exception as e:
        p("default ctx err", traceback.format_exc())

    # ---------- car pawn
    car_path = "/Game/Car/Blueprints/BP_CarPawn"
    car = make_bp(car_path, unreal.WheeledVehiclePawn)
    handles = SDS.k2_gather_subobject_data_for_blueprint(car)
    comps = {}
    for h in handles:
        d = SDS.k2_find_subobject_data_from_handle(h)
        o = SDL.get_object(d)
        comps[str(SDL.get_variable_name(d))] = (h, o)
    p("components", {k: type(v[1]).__name__ for k, v in comps.items()})
    root_h, skm = None, None
    for k, (h, o) in comps.items():
        if isinstance(o, unreal.SkeletalMeshComponent): root_h, skm = h, o
    setp(skm, "skeletal_mesh_asset", mesh) or setp(skm, "skeletal_mesh", mesh)
    setp(skm, "simulate_physics", True)
    try: skm.set_collision_profile_name("Vehicle")
    except Exception as e: p("profile err", e)
    if "SpringArm" not in comps:
        prm = unreal.AddNewSubobjectParams(parent_handle=root_h, new_class=unreal.SpringArmComponent, blueprint_context=car)
        sh, fr = SDS.add_new_subobject(prm)
        SDS.rename_subobject_member_variable(car, sh, "SpringArm")
        prm2 = unreal.AddNewSubobjectParams(parent_handle=sh, new_class=unreal.CameraComponent, blueprint_context=car)
        ch, fr2 = SDS.add_new_subobject(prm2)
        SDS.rename_subobject_member_variable(car, ch, "ChaseCamera")
        prm3 = unreal.AddNewSubobjectParams(parent_handle=root_h, new_class=unreal.CameraComponent, blueprint_context=car)
        ih, fr3 = SDS.add_new_subobject(prm3)
        SDS.rename_subobject_member_variable(car, ih, "HoodCamera")
        handles = SDS.k2_gather_subobject_data_for_blueprint(car)
        comps = {}
        for h in handles:
            d = SDS.k2_find_subobject_data_from_handle(h)
            comps[str(SDL.get_variable_name(d))] = (h, SDL.get_object(d))
    p("components2", {k: type(v[1]).__name__ for k, v in comps.items()})
    arm = comps["SpringArm"][1]
    setp(arm, "relative_location", unreal.Vector(0, 0, 90))
    setp(arm, "relative_rotation", unreal.Rotator(roll=0, pitch=-12, yaw=0))
    setp(arm, "target_arm_length", 650.0)
    setp(arm, "socket_offset", unreal.Vector(0, 0, 60))
    setp(arm, "use_pawn_control_rotation", False)
    setp(arm, "inherit_pitch", False); setp(arm, "inherit_roll", False); setp(arm, "inherit_yaw", True)
    setp(arm, "enable_camera_lag", True); setp(arm, "camera_lag_speed", 8.0)
    setp(arm, "enable_camera_rotation_lag", True); setp(arm, "camera_rotation_lag_speed", 5.0)
    setp(arm, "do_collision_test", True)
    cam = comps["ChaseCamera"][1]; setp(cam, "field_of_view", 90.0)
    hood = comps["HoodCamera"][1]
    setp(hood, "relative_location", unreal.Vector(10, 0, 115)); setp(hood, "field_of_view", 95.0)
    setp(hood, "auto_activate", False)
    mv = None
    for k, (h, o) in comps.items():
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent): mv = o
    def ws(bone, wc):
        s = unreal.ChaosWheelSetup(); s.set_editor_property("wheel_class", wc); s.set_editor_property("bone_name", bone); return s
    setp(mv, "wheel_setups", [ws("DEF-FRONT-WHEEL_L", wf.generated_class()), ws("DEF-FRONT-WHEEL_R", wf.generated_class()),
                             ws("DEF-BACK-WHEEL_L", wr.generated_class()), ws("DEF-BACK-WHEEL_R", wr.generated_class())])
    setp(mv, "mass", 1200.0)
    setp(mv, "chassis_width", 150.0); setp(mv, "chassis_height", 130.0)
    setp(mv, "drag_coefficient", 0.3); setp(mv, "downforce_coefficient", 0.3)
    setp(mv, "enable_center_of_mass_override", True)
    setp(mv, "center_of_mass_override", unreal.Vector(10, 0, 30))
    eng = mv.get_editor_property("engine_setup")
    for k, vv in [("max_torque", 450.0), ("max_rpm", 6500.0), ("engine_idle_rpm", 900.0), ("engine_brake_effect", 0.2),
                  ("engine_rev_up_moi", 5.0), ("engine_rev_down_rate", 600.0)]:
        setp(eng, k, vv)
    setp(mv, "engine_setup", eng)
    tr = mv.get_editor_property("transmission_setup")
    setp(tr, "use_automatic_gears", True); setp(tr, "forward_gear_ratios", [4.25, 2.52, 1.66, 1.22, 1.0])
    setp(tr, "final_ratio", 3.08); setp(tr, "change_up_rpm", 5800.0); setp(tr, "change_down_rpm", 2600.0); setp(tr, "gear_change_time", 0.25)
    setp(mv, "transmission_setup", tr)
    df = mv.get_editor_property("differential_setup")
    setp(df, "differential_type", unreal.VehicleDifferentialType.ALL_WHEEL_DRIVE); setp(df, "front_rear_split", 0.35)
    setp(mv, "differential_setup", df)
    p("engine", mv.get_editor_property("engine_setup"))
    p("trans", mv.get_editor_property("transmission_setup"))
    p("diff", mv.get_editor_property("differential_setup"))
    p("steer", mv.get_editor_property("steering_setup"))
    # variables for the graph
    for nm, tp, val in [("CameraYaw", "real", "0.0"), ("UsingHoodCam", "bool", "false")]:
        try:
            pt = BEL.get_basic_type_by_name(tp)
            BEL.add_member_variable(car, nm, pt)
        except Exception as e: p("var err", nm, e)
    BEL.compile_blueprint(car); EAL.save_asset(car_path)

    # ---------- game mode
    gm_path = "/Game/Car/Blueprints/BP_CarGameMode"
    gm = make_bp(gm_path, unreal.GameModeBase)
    gcdo = unreal.get_default_object(gm.generated_class())
    setp(gcdo, "default_pawn_class", car.generated_class())
    BEL.compile_blueprint(gm); EAL.save_asset(gm_path)
    try:
        gms = unreal.get_default_object(unreal.GameMapsSettings)
        p("gamemaps attrs", [x for x in dir(gms) if "game" in x.lower() or "map" in x.lower()][:40])
    except Exception as e: p("gms err", e)
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_BUILD2_DONE")
