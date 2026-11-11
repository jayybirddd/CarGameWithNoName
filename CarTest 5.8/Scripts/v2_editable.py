import unreal
BEL = unreal.BlueprintEditorLibrary
car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
for nm in ("BoostHeld", "PitchAxis"):
    BEL.set_blueprint_variable_instance_editable(car, nm, True)
    BEL.set_blueprint_variable_category(car, nm, "Car State")
BEL.compile_blueprint(car)
unreal.EditorAssetLibrary.save_asset("/Game/Car/Blueprints/BP_CarPawn")
