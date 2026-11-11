import unreal
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe7.txt"
L = []
base = set(dir(unreal.Object))
mesh = unreal.load_asset("/Game/Car/Mesh/SK_Car")
mod = unreal.SkeletonModifier(); mod.set_skeletal_mesh(mesh)
for b in ["CAR", "ROOT", "MASTER-ROTATION", "DEF-BODY"]:
    t = mod.get_bone_transform(b, True); r = t.rotation.rotator()
    L.append("mesh-ref %s loc(%.2f,%.2f,%.2f) rot(p%.1f,y%.1f,r%.1f) s(%.2f)" % (b, t.translation.x, t.translation.y, t.translation.z, r.pitch, r.yaw, r.roll, t.scale3d.x))
L.append("Skeleton: " + " ".join(x for x in dir(unreal.Skeleton) if not x.startswith("_") and x not in base))
a = unreal.load_asset("/Game/Car/Animations/AS_Idle")
L.append("AnimSequence: " + " ".join(x for x in dir(a) if not x.startswith("_") and x not in base))
c = a.get_editor_property("controller")
L.append("Controller: " + " ".join(x for x in dir(c) if not x.startswith("_") and x not in base))
for nm in ["data_model", "data_model_interface", "DataModel"]:
    try: L.append(nm + " -> " + str(a.get_editor_property(nm)))
    except Exception as e: L.append(nm + " err " + str(e))
L.append("ESML: " + " ".join(x for x in dir(unreal.EditorSkeletalMeshLibrary) if not x.startswith("_") and x not in base))
L.append("AL: " + " ".join(x for x in dir(unreal.AnimationLibrary) if not x.startswith("_") and x not in base))
with open(OUT, "w") as f: f.write("\n".join(L))
