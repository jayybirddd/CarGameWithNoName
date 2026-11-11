import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_check.txt"
L = []
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
try:
    for path in ("/Game/Car/Blueprints/BP_CarPawn", "/Game/Car/Blueprints/BP_CarPawn_Moon", "/Game/Car/Blueprints/ABP_CarBody", "/Game/Car/Blueprints/BP_CarHUD", "/Game/Car/Blueprints/BP_CarGameMode", "/Game/Car/Blueprints/BP_CarGameMode_Moon"):
        bp = unreal.load_asset(path)
        BEL.compile_blueprint(bp)
        L.append("%s status %s" % (path, bp.get_editor_property("status") if hasattr(bp, "get_editor_property") else "?"))
    moon = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn_Moon")
    names = []
    for h in SDS.k2_gather_subobject_data_for_blueprint(moon):
        d = SDS.k2_find_subobject_data_from_handle(h); o = SDL.get_object(d)
        names.append(str(SDL.get_variable_name(d)))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
            L.append("moon trans " + o.get_editor_property("transmission_setup").export_text())
            L.append("moon wheels " + str([w.export_text()[-80:] for w in o.get_editor_property("wheel_setups")]))
    L.append("moon comps %s" % names)
    cdo = unreal.get_default_object(moon.generated_class())
    for k in ("BoostAccel", "AirPitchRate", "AutoGears", "NumForwardGears"):
        L.append("moon %s = %s" % (k, cdo.get_editor_property(k)))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(False, True)
    L.append("saved")
except Exception:
    L.append(traceback.format_exc())
open(OUT, "w").write("\n".join(L))
