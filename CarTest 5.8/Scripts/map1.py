import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_map1.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    path = "/Game/Car/Maps/CarTestTrack"
    if EAL.does_asset_exist(path):
        les.load_level(path)
    else:
        les.new_level(path)
        def spawn(cls, loc, rot=unreal.Rotator(0,0,0)):
            return eas.spawn_actor_from_class(cls, loc, rot)
        plane = unreal.load_asset("/Engine/BasicShapes/Plane")
        cube = unreal.load_asset("/Engine/BasicShapes/Cube")
        grid = unreal.load_asset("/Engine/EngineMaterials/WorldGridMaterial")
        floor = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
        floor.static_mesh_component.set_static_mesh(plane)
        floor.set_actor_scale3d(unreal.Vector(600, 600, 1))
        floor.static_mesh_component.set_material(0, grid)
        floor.set_actor_label("Floor")
        # a few ramps and bumps
        for i, (x, y, yaw, pitch, sx) in enumerate([(4000, 0, 0, 12, 8), (-3000, 2500, 90, 8, 6), (2500, -4000, 45, 15, 5)]):
            r = spawn(unreal.StaticMeshActor, unreal.Vector(x, y, 30), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw))
            r.static_mesh_component.set_static_mesh(cube); r.set_actor_scale3d(unreal.Vector(sx, 6, 0.6))
            r.set_actor_label("Ramp_%d" % i)
        for i in range(10):
            b = spawn(unreal.StaticMeshActor, unreal.Vector(-1500 + i * 300, -1500, -20), unreal.Rotator(0, 0, 0))
            b.static_mesh_component.set_static_mesh(cube); b.set_actor_scale3d(unreal.Vector(0.6, 8, 0.4))
            b.set_actor_label("Bump_%d" % i)
        sun = spawn(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(roll=0, pitch=-45, yaw=30))
        try: sun.light_component.set_editor_property("atmosphere_sun_light", True)
        except Exception as e: log("sun", e)
        spawn(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
        sl = spawn(unreal.SkyLight, unreal.Vector(0, 0, 500))
        try: sl.light_component.set_editor_property("real_time_capture", True)
        except Exception as e: log("skylight", e)
        spawn(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
        spawn(unreal.PlayerStart, unreal.Vector(0, 0, 150))
    world = unreal.EditorLevelLibrary.get_editor_world()
    ws = world.get_world_settings()
    gm = unreal.load_asset("/Game/Car/Blueprints/BP_CarGameMode")
    ws.set_editor_property("default_game_mode", gm.generated_class())
    les.save_current_level()
    log("world", world.get_path_name(), "gm", ws.get_editor_property("default_game_mode"))
    try:
        gms = unreal.GameMapsSettings.get_game_maps_settings()
        for k, v in [("global_default_game_mode", unreal.SoftClassPath(gm.generated_class().get_path_name())),
                     ("editor_startup_map", unreal.SoftObjectPath(path + ".CarTestTrack")),
                     ("game_default_map", unreal.SoftObjectPath(path + ".CarTestTrack"))]:
            try: gms.set_editor_property(k, v)
            except Exception as e: log("gms", k, e)
        try: gms.save_config(); log("saved gms")
        except Exception as e: log("gms save", e)
    except Exception as e: log("gms err", e)
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_MAP1_DONE")
