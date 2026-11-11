import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe1.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
try:
    for nm in ["PhysicsAssetFactory","PhysicsAssetGenerationSettings","PhysicsAssetEditorSubsystem","SkeletalMeshEditorSubsystem","EditorSkeletalMeshLibrary","PhysicsAssetUtils","SkeletalBodySetup","PhysAssetCreateParams"]:
        c = getattr(unreal, nm, None)
        p(nm, c is not None, [x for x in dir(c) if not x.startswith("_")][:80] if c else "")
    pa = unreal.load_asset("/Game/Car_Rig_and_Anims/Mesh/car_acceleration_PhysicsAsset")
    p("pa dir", [x for x in dir(pa) if not x.startswith("_")])
    try:
        gs = unreal.get_default_object(unreal.PhysicsAssetGenerationSettings)
        p("gen settings", gs.get_editor_property("create_params"))
    except Exception as e: p("gs err", e)
    p("wheel class", unreal.ChaosVehicleWheel, [x for x in dir(unreal.ChaosVehicleWheel) if not x.startswith("_")][:200])
    p("move comp", [x for x in dir(unreal.ChaosWheeledVehicleMovementComponent) if not x.startswith("_")])
    p("bp lib", [x for x in dir(unreal.BlueprintEditorLibrary) if not x.startswith("_")])
    p("subobj", [x for x in dir(unreal.SubobjectDataSubsystem) if not x.startswith("_")])
    p("imc", [x for x in dir(unreal.InputMappingContext) if not x.startswith("_")])
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
