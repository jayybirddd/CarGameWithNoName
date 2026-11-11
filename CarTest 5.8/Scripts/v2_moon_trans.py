import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_trans.txt"
L = []
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
def movement(bp):
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        o = SDL.get_object(SDS.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.ChaosWheeledVehicleMovementComponent): return o
try:
    src = movement(unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn"))
    moon = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn_Moon")
    dst = movement(moon)
    dst.set_editor_property("transmission_setup", src.get_editor_property("transmission_setup"))
    dst.set_editor_property("engine_setup", src.get_editor_property("engine_setup"))
    BEL.compile_blueprint(moon)
    unreal.EditorAssetLibrary.save_asset("/Game/Car/Blueprints/BP_CarPawn_Moon")
    dst = movement(unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn_Moon"))
    L.append("moon trans " + dst.get_editor_property("transmission_setup").export_text())
    L.append("moon engine " + dst.get_editor_property("engine_setup").export_text()[-200:])
except Exception:
    L.append(traceback.format_exc())
open(OUT, "w").write("\n".join(L))
