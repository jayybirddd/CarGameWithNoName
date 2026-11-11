import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_tune1.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
try:
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    for h in SDS.k2_gather_subobject_data_for_blueprint(car):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent):
            props = [x for x in dir(o) if any(k in x for k in ("idle", "brake", "threshold", "drag", "resistance", "stop"))]
            log("props", props)
            eng = o.get_editor_property("engine_setup")
            eng.set_editor_property("engine_brake_effect", 0.05)
            eng.set_editor_property("max_torque", 380.0)
            o.set_editor_property("engine_setup", eng)
            for k, v in [("idle_brake_input", 0.0)]:
                try: o.set_editor_property(k, v); log("set", k, v)
                except Exception as e: log("no", k, e)
            for k in ["idle_brake_input", "stop_threshold", "wrong_direction_threshold", "drag_coefficient", "downforce_coefficient", "mass"]:
                try: log("val", k, o.get_editor_property(k))
                except Exception as e: log("noval", k)
            log("engine", o.get_editor_property("engine_setup").export_text()[-260:])
    BEL.compile_blueprint(car); EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
