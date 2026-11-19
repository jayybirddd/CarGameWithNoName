# Places the separated car and the driving car in the editor world for a moment and records their bone positions
# (component space at yaw 0), so the wreck pieces can be laid out to match. Removes the temp actors afterwards.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v7_bones.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
BONES = ["DEF-BODY", "DEF-BASE-ANTENNAE", "DEF-ANTENAE0-001", "DEF-ANTENAE0-004", "DEF-FRONT-WHEEL_L", "DEF-FRONT-WHEEL_R", "DEF-BACK-WHEEL_L", "DEF-BACK-WHEEL_R"]
made = []
try:
    for nm, path in (("separated", "/Game/Car/SeparatedCar/CAR_separated"), ("SK_Car", "/Game/Car/Mesh/SK_Car")):
        a = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -50000), unreal.Rotator())
        made.append(a)
        c = a.skeletal_mesh_component
        c.set_skinned_asset_and_update(unreal.load_asset(path)) if hasattr(c, "set_skinned_asset_and_update") else c.set_skeletal_mesh(unreal.load_asset(path))
        for b in BONES:
            p = c.get_socket_location(b)
            log(nm, b, "%.1f %.1f %.1f" % (p.x, p.y, p.z + 50000))
        b_ = c.bounds; log(nm, "bounds", b_.origin.x, b_.origin.y, b_.origin.z + 50000, b_.box_extent)
except Exception:
    log(traceback.format_exc())
for a in made: EAS.destroy_actor(a)
with open(OUT, "w") as f: f.write("\n".join(L))
