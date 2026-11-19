# Reports the separated car: bones (with parents), bounds vs the driving car, materials, and its physics asset.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v7_probe_sep.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
try:
    sk = unreal.load_asset("/Game/Car/SeparatedCar/CAR_separated")
    car = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    for nm, m in (("separated", sk), ("SK_Car", car)):
        b = m.get_bounds(); log(nm, "bounds origin", b.origin, "ext", b.box_extent)
    try:
        mod = unreal.SkeletonModifier(); mod.set_skeletal_mesh(sk)
        for n in mod.get_all_bone_names(): log("bone", n, "<-", mod.get_parent_name(n))
    except Exception as e: log("modifier err", e)
    log("materials", [str(x.get_editor_property("material_slot_name")) for x in sk.get_editor_property("materials")])
    pa = unreal.load_asset("/Game/Car/SeparatedCar/CAR_separated_PhysicsAsset")
    log("physics asset props", [p for p in dir(pa) if "constraint" in p.lower() or "body" in p.lower() or "skeletal" in p.lower()])
    for k in ("skeletal_body_setups", "constraint_setup"):
        try:
            v = pa.get_editor_property(k); log(k, len(v), [str(x.get_editor_property("bone_name")) if hasattr(x, "get_editor_property") else x for x in v][:40])
        except Exception as e: log(k, "ERR", e)
    try:
        cs = pa.get_editor_property("constraint_setup")
        for c in cs[:40]:
            d = c.get_editor_property("default_instance")
            log("  constraint", d.get_editor_property("constraint_bone1"), "-", d.get_editor_property("constraint_bone2"))
    except Exception as e: log("constraint detail ERR", e)
    sms = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    log("sk editor subsystem", [m for m in dir(sms) if not m.startswith("_")][:60])
    log("lod sections", sk.get_num_sections(0) if hasattr(sk, "get_num_sections") else "?")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
