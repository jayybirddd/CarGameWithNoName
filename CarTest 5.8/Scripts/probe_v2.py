import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_probe_v2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
try:
    log("project", unreal.Paths.get_project_file_path())
    for path in ("/Game/Car/Blueprints/BP_CarPawn", "/Game/Car/Blueprints/BP_CarPawn_Moon"):
        car = unreal.load_asset(path)
        log("==", path)
        log("vars", [str(x) for x in BEL.list_member_variable_names(car)])
        for h in SDS.k2_gather_subobject_data_for_blueprint(car):
            d = SDS.k2_find_subobject_data_from_handle(h)
            o = SDL.get_object(d)
            log(" comp", SDL.get_variable_name(d), type(o).__name__)
            if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
                log("  trans", o.get_editor_property("transmission_setup").export_text())
                log("  engine", o.get_editor_property("engine_setup").export_text()[-300:])
                log("  wheels", [w.export_text() for w in o.get_editor_property("wheel_setups")])
                for k in ("mass", "center_of_mass_override", "drag_coefficient", "chassis_width", "chassis_height", "enable_center_of_mass_override", "torque_control", "target_rotation_control", "stabilize_control"):
                    try: log("  ", k, o.get_editor_property(k))
                    except Exception as e: log("  no", k)
                try: log("  torque_control", o.get_editor_property("torque_control").export_text())
                except Exception as e: log("  tc err", e)
        g = BEL.find_event_graph(car)
        ed = unreal.BlueprintGraphEditor.get_graph_editor(g)
        log(" nodes", len(ed.list_all_nodes()), sorted(set(str(BEL.get_node_title(n)).split("\n")[0] for n in ed.list_all_nodes()))[:80])
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    log("abp vars", [str(x) for x in BEL.list_member_variable_names(abp)])
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    for n in ag.list_all_nodes():
        log(" anim node", n.get_class().get_name(), str(BEL.get_node_title(n)).replace("\n", " | "))
    sk = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    APE = unreal.AnimPoseExtensions
    ref = APE.get_reference_pose(sk.skeleton)
    for n in APE.get_bone_names(ref):
        if "ANT" in str(n).upper() or "BODY" in str(n).upper() or str(n) in ("ROOT", "CAR", "MASTER-LOCATION", "MASTER-ROTATION"):
            t = APE.get_bone_pose(ref, n, unreal.AnimPoseSpaces.WORLD)
            log(" bone", n, "parent", APE.get_bone_name_parent(ref, n) if hasattr(APE, "get_bone_name_parent") else "?", "w", t.translation, t.rotation.rotator())
    # niagara assets available
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for cls in ("NiagaraSystem",):
        f = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Niagara", cls)], recursive_paths=True)
        assets = ar.get_assets(f)
        log(cls, len(assets), [str(a.package_name) for a in assets][:60])
    for nm in dir(unreal):
        if "AnimDynamic" in nm or "SpringController" in nm or nm.startswith("AnimGraphNode_Spring"):
            log("cls", nm)
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_PROBE_V2_DONE")
