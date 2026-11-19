# Reports the track level's layout and the car's current handling settings (engine, wheels, handbrake).
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_probe.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def movement(bp):
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent): return o
try:
    log("editor world", UES.get_editor_world().get_path_name())
    log("load track", LES.load_level("/Game/Levels/l_TestingTrack"))
    ws = UES.get_editor_world().get_world_settings()
    gm = ws.get_editor_property("default_game_mode")
    log("gravity", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), "gm", gm.get_name() if gm else None)
    for a in EAS.get_all_level_actors():
        o, e = a.get_actor_bounds(False)
        extra = ""
        if isinstance(a, unreal.StaticMeshActor):
            sm = a.static_mesh_component.get_editor_property("static_mesh")
            extra = "mesh %s scale %s" % (sm.get_path_name() if sm else None, a.get_actor_scale3d())
        log("actor", a.get_actor_label(), a.get_class().get_name(), "center (%.0f,%.0f,%.0f) ext (%.0f,%.0f,%.0f)" % (o.x, o.y, o.z, e.x, e.y, e.z),
            "rot", a.get_actor_rotation(), extra)
    tt = unreal.load_asset("/Game/Environment/Track/TestTrack")
    if tt:
        b = tt.get_bounds(); log("TestTrack mesh bounds", b.origin, b.box_extent, "tris", tt.get_num_triangles(0) if hasattr(tt, "get_num_triangles") else "?")
        bs = tt.get_editor_property("body_setup")
        log("collision", bs.get_editor_property("collision_trace_flag") if bs else None)
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    mv = movement(car)
    for k in ("mass", "drag_coefficient", "downforce_coefficient", "chassis_height", "enable_center_of_mass_override", "center_of_mass_override", "inertia_tensor_scale"):
        try: log("mv", k, mv.get_editor_property(k))
        except Exception as e: log("mv", k, "ERR", e)
    log("engine", mv.get_editor_property("engine_setup").export_text()[-260:])
    log("diff", mv.get_editor_property("differential_setup").export_text())
    log("steer", mv.get_editor_property("steering_setup").export_text()[-200:])
    for w in ("BP_Wheel_Front", "BP_Wheel_Rear"):
        cdo = unreal.get_default_object(unreal.load_asset("/Game/Car/Blueprints/" + w).generated_class())
        vals = {}
        for k in ("wheel_radius", "wheel_width", "friction_force_multiplier", "cornering_stiffness", "side_slip_modifier", "slip_threshold", "skid_threshold",
                  "max_steer_angle", "affected_by_handbrake", "affected_by_engine", "max_brake_torque", "max_hand_brake_torque", "spring_rate", "spring_preload",
                  "suspension_max_raise", "suspension_max_drop", "suspension_damping_ratio", "wheel_load_ratio", "traction_control_enabled", "abs_enabled", "lateral_slip_graph_multiplier"):
            try: vals[k] = cdo.get_editor_property(k)
            except Exception as e: vals[k] = "ERR"
        log(w, vals)
    cdo = unreal.get_default_object(car.generated_class())
    log("car vars", {k: cdo.get_editor_property(k) for k in ("BoostAccel", "PadAccel", "BoostDrainPerSec", "BoostRegenPerSec")})
    ed = unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(car))
    log("handbrake nodes", [str(unreal.BlueprintEditorLibrary.get_node_title(n)).splitlines()[0] for n in ed.list_all_nodes() if "andbrake" in str(unreal.BlueprintEditorLibrary.get_node_title(n))])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V6_PROBE_DONE")
