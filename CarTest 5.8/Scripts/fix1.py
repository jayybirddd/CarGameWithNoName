import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_fix1.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
try:
    for cp in ["/Game/Car-Game/CarStuff/VehicleMovementComp_ExternalCurve", "/Game/Car-Game/CarStuff/VehicleMovementComp_ExternalCurveEdited"]:
        c = unreal.load_asset(cp)
        log(cp, [(t, round(c.get_float_value(t), 3)) for t in (0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)])
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    for h in SDS.k2_gather_subobject_data_for_blueprint(car):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
            eng = o.get_editor_property("engine_setup")
            log("engine before", eng.export_text()[:800])
            ok = eng.import_text('(TorqueCurve=(EditorCurveData=(Keys=((Time=0.0,Value=0.55),(Time=1000.0,Value=0.7),(Time=2500.0,Value=0.9),(Time=4000.0,Value=1.0),(Time=5500.0,Value=0.95),(Time=6500.0,Value=0.75)))),MaxTorque=450.0,MaxRPM=6500.0,EngineIdleRPM=900.0,EngineBrakeEffect=0.2,EngineRevUpMOI=5.0,EngineRevDownRate=600.0)')
            log("import", ok)
            o.set_editor_property("engine_setup", eng)
            log("engine after", o.get_editor_property("engine_setup").export_text()[:800])
            log("trans", o.get_editor_property("transmission_setup").export_text()[:600])
            log("diff", o.get_editor_property("differential_setup").export_text()[:300])
            log("steer", o.get_editor_property("steering_setup").export_text()[:600])
    BEL.compile_blueprint(car); EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_FIX1_DONE")
