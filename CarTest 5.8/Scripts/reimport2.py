import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_reimport.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
try:
    p("chaos class", unreal.load_class(None, "/Script/ChaosVehicles.WheeledVehiclePawn"))
    SRC = "D:/PersonalGameFiles/CarTest/Content/Car Rig and Anims/car_rig.fbx"
    DEST = "/Game/Car/Mesh"
    ui = unreal.FbxImportUI()
    ui.import_mesh = True
    ui.import_as_skeletal = True
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    ui.import_animations = True
    ui.import_materials = False
    ui.import_textures = False
    ui.create_physics_asset = True
    ui.skeletal_mesh_import_data.import_rotation = unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0)
    ui.skeletal_mesh_import_data.import_uniform_scale = 1.0
    ui.anim_sequence_import_data.import_rotation = unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0)
    t = unreal.AssetImportTask()
    t.filename = SRC
    t.destination_path = DEST
    t.destination_name = "SK_Car"
    t.automated = True
    t.replace_existing = True
    t.save = True
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    for o in t.imported_object_paths: p("imported", o)
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_REIMPORT_DONE")
