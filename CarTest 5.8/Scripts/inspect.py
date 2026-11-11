import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_inspect.txt"
lines = []
def p(*a):
    lines.append(" ".join(str(x) for x in a))
def sec(name, fn):
    p("==== " + name)
    try:
        fn()
    except Exception:
        p(traceback.format_exc())

def plugins():
    for c in ["/Script/ChaosVehicles.ChaosWheeledVehicleMovementComponent",
              "/Script/ChaosVehicles.WheeledVehiclePawn",
              "/Script/ChaosVehicles.VehicleAnimationInstance",
              "/Script/EnhancedInput.InputAction"]:
        p(c, "->", unreal.load_class(None, c) is not None if True else "")
sec("classes", plugins)

reg = unreal.AssetRegistryHelpers.get_asset_registry()
def assets():
    for path in ["/Game/Car_Rig_and_Anims", "/Game/Car-Game"]:
        for ad in reg.get_assets_by_path(path, recursive=True):
            p(str(ad.package_name), str(ad.asset_class_path.asset_name))
sec("assets", assets)

MESH = "/Game/Car_Rig_and_Anims/Mesh/car_acceleration"
def mesh():
    m = unreal.load_asset(MESH)
    p("mesh", m)
    b = m.get_bounds()
    p("bounds origin", b.origin, "extent", b.box_extent)
    sk = m.skeleton
    p("skeleton", sk.get_path_name())
    p("physics asset", m.physics_asset.get_path_name() if m.physics_asset else None)
    p("materials", [str(x.material_slot_name) for x in m.materials])
    pose = unreal.AnimPoseExtensions.get_reference_pose(sk)
    names = unreal.AnimPoseExtensions.get_bone_names(pose)
    p("bone count", len(names))
    for n in names:
        t = unreal.AnimPoseExtensions.get_bone_pose(pose, n, unreal.AnimPoseSpaces.WORLD)
        p("  bone", n, "loc", t.translation, "rot", t.rotation.rotator())
sec("mesh", mesh)

def anims():
    for ad in reg.get_assets_by_path("/Game/Car_Rig_and_Anims/Animations", recursive=True):
        a = unreal.load_asset(str(ad.package_name))
        try:
            p(ad.asset_name, type(a).__name__, "len", a.get_play_length() if hasattr(a,"get_play_length") else "?",
              "skel", a.get_editor_property("skeleton").get_path_name())
            try:
                curves = unreal.AnimationLibrary.get_animation_track_names(a)
                p("   tracks", list(curves))
            except Exception as e:
                p("   tracks err", e)
        except Exception as e:
            p(ad.asset_name, "err", e)
sec("anims", anims)

def bps():
    for path in ["/Game/Car_Rig_and_Anims/Blueprints/BP_Car", "/Game/Car_Rig_and_Anims/Blueprints/ABP_Car",
                 "/Game/Car-Game/CarStuff/BP_Car", "/Game/Car-Game/CarStuff/BP_Car_Front_Wheel",
                 "/Game/Car-Game/CarStuff/BP_Car_Rear_Wheels", "/Game/Car-Game/CarStuff/RigAndAnims/AnimBP_Car"]:
        try:
            b = unreal.load_asset(path)
            gc = b.generated_class() if b else None
            parent = b.get_editor_property("parent_class") if b else None
            p(path, "parent", parent.get_name() if parent else None)
            if isinstance(b, unreal.AnimBlueprint):
                p("   target skel", b.get_editor_property("target_skeleton").get_path_name() if b.get_editor_property("target_skeleton") else None)
            if gc:
                cdo = unreal.get_default_object(gc)
                if isinstance(cdo, unreal.Actor):
                    for c in cdo.get_components_by_class(unreal.ActorComponent):
                        p("   comp", c.get_name(), type(c).__name__)
        except Exception as e:
            p(path, "err", e)
sec("blueprints", bps)

def ias():
    for path in ["/Game/Car_Rig_and_Anims/Blueprints/IA_Move", "/Game/Car_Rig_and_Anims/Blueprints/IA_Turn"]:
        a = unreal.load_asset(path)
        p(path, a.get_editor_property("value_type") if a else None)
sec("input", ias)

with open(OUT, "w") as f:
    f.write("\n".join(lines))
unreal.log("CLAUDE_INSPECT_DONE " + OUT)
