# Compares the Moon car/game mode/map against the base ones: what's inherited, what's overridden.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_probe.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
B = "/Game/Car/Blueprints/"
def comps(bp):
    out = {}
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        d = SDS.k2_find_subobject_data_from_handle(h); o = SDL.get_object(d)
        if o is not None: out[str(SDL.get_variable_name(d))] = o
    return out
PROPS = ["mass", "drag_coefficient", "downforce_coefficient", "chassis_height", "chassis_width", "enable_center_of_mass_override",
         "center_of_mass_override", "inertia_tensor_scale", "idle_brake_input", "stop_threshold", "wheel_setups", "torque_control", "target_rotation_control",
         "wheel_radius", "wheel_width", "friction_force_multiplier", "cornering_stiffness", "lateral_slip_graph_multiplier", "suspension_max_raise",
         "suspension_max_drop", "spring_rate", "spring_preload", "suspension_damping_ratio", "wheel_load_ratio", "max_brake_torque", "max_hand_brake_torque",
         "suspension_smoothing", "rollbar_scaling", "max_steer_angle", "affected_by_engine", "affected_by_handbrake", "traction_control_enabled", "abs_enabled",
         "target_arm_length", "camera_lag_speed", "relative_location", "air_control", "gravity_scale",
         "BoostAccel", "BoostDrainPerSec", "BoostRegenPerSec", "BoostRegenDelay", "AirPitchRate", "AirPitchResponse", "NumForwardGears", "AutoGears"]
def diff(tag, a, b):
    for p in PROPS:
        try:
            va = a.get_editor_property(p); vb = b.get_editor_property(p)
        except Exception:
            continue
        sa = va.export_text() if hasattr(va, "export_text") else str(va)
        sb = vb.export_text() if hasattr(vb, "export_text") else str(vb)
        if sa != sb and "0x" not in sa:
            log("  DIFF", tag, p, "| base:", sa[:300], "| moon:", sb[:300])
try:
    base = unreal.load_asset(B + "BP_CarPawn"); moon = unreal.load_asset(B + "BP_CarPawn_Moon")
    gc = moon.generated_class()
    try: log("moon is child of base", unreal.MathLibrary.class_is_child_of(gc, base.generated_class()))
    except Exception as e: log("child check err", e)
    for attr in ("get_super_class", "get_super_struct"):
        if hasattr(gc, attr): log("moon super", getattr(gc, attr)().get_name())
    try:
        ed = unreal.BlueprintGraphEditor.get_graph_editor_by_name(moon, "EventGraph")
        log("moon event nodes", [str(BEL.get_node_title(nd)).splitlines()[0] for nd in ed.list_all_nodes()] if ed else None)
    except Exception as e: log("moon graph err", e)
    log("moon vars", [str(x) for x in BEL.list_member_variable_names(moon)])
    cb, cm = comps(base), comps(moon)
    log("base comps", sorted(cb)); log("moon comps", sorted(cm))
    for k in sorted(set(cb) & set(cm)):
        if k in ("None",): continue
        diff(k, cb[k], cm[k])
    diff("CDO", unreal.get_default_object(base.generated_class()), unreal.get_default_object(moon.generated_class()))
    for w in ("Front", "Rear"):
        a = unreal.get_default_object(unreal.load_asset(B + "BP_Wheel_%s" % w).generated_class())
        b = unreal.get_default_object(unreal.load_asset(B + "BP_Wheel_%s_Moon" % w).generated_class())
        diff("Wheel" + w, a, b)
    gb = unreal.get_default_object(unreal.load_asset(B + "BP_CarGameMode").generated_class())
    gm = unreal.get_default_object(unreal.load_asset(B + "BP_CarGameMode_Moon").generated_class())
    for k in ("default_pawn_class", "hud_class", "player_controller_class"):
        log("gm", k, gb.get_editor_property(k).get_name(), "| moon", gm.get_editor_property(k).get_name())
    lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    w = unreal.EditorLevelLibrary.get_editor_world()
    log("editor world", w.get_path_name())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_MOON_PROBE_DONE")
