import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_build1.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
KEEP = {"DEF-BODY","DEF-BASE-ANTENNAE","DEF-ANTENAE0-001","DEF-ANTENAE0-002","DEF-ANTENAE0-003","DEF-ANTENAE0-004",
        "CTRL-BODY","Bone","CTRL-ANTENAE","TGT-ANTENAE0-002","TGT-ANTENAE0-003","TGT-ANTENAE0-004"}
SRC = {"AS_Default":"SK_CarCAR_ArmatureAction","AS_Idle":"SK_CarCAR_ArmatureAction_002","AS_Accelerate":"SK_CarCAR_ArmatureAction_003",
       "AS_Decelerate":"SK_CarCAR_ArmatureAction_004","AS_TurnLeft":"SK_CarCAR_ArmatureAction_005","AS_TurnRight":"SK_CarCAR_ArmatureAction_006"}
try:
    # 1) rename raw imports to readable names (kept as full clips, in Mesh/Raw)
    for nice, raw in SRC.items():
        s = "/Game/Car/Mesh/" + raw
        d = "/Game/Car/Animations/Raw/" + nice + "_Full"
        if EAL.does_asset_exist(s) and not EAL.does_asset_exist(d):
            p("rename", s, "->", d, EAL.rename_asset(s, d))
    # 2) body-only copies
    for nice in SRC:
        full = "/Game/Car/Animations/Raw/" + nice + "_Full"
        body = "/Game/Car/Animations/" + nice
        if EAL.does_asset_exist(body): EAL.delete_asset(body)
        a = EAL.duplicate_asset(full, body)
        ctrl = a.get_editor_property("controller")
        names = unreal.AnimationLibrary.get_animation_track_names(a)
        ctrl.open_bracket(unreal.Text("strip"), False)
        removed = []
        for n in names:
            if str(n).upper() not in {k.upper() for k in KEEP}:
                ctrl.remove_bone_track(n, False); removed.append(str(n))
        ctrl.close_bracket(False)
        p("body", body, "removed", len(removed), "left", [str(x) for x in unreal.AnimationLibrary.get_animation_track_names(a)])
        EAL.save_asset(body)
    # 3) additive turn copies (local space, base = reference pose)
    for nice in ["AS_TurnLeft","AS_TurnRight","AS_Accelerate"]:
        src = "/Game/Car/Animations/" + nice
        add = "/Game/Car/Animations/" + nice + "_Add"
        if EAL.does_asset_exist(add): EAL.delete_asset(add)
        a = EAL.duplicate_asset(src, add)
        a.set_editor_property("additive_anim_type", unreal.AdditiveAnimationType.AAT_LOCAL_SPACE_BASE)
        a.set_editor_property("ref_pose_type", unreal.AdditiveBasePoseType.ABPT_REF_POSE)
        EAL.save_asset(add)
        p("additive", add)
    # 4) physics / material info from the old mesh
    old = unreal.load_asset("/Game/Car_Rig_and_Anims/Mesh/car_acceleration")
    for mat in old.materials:
        p("old material", mat.material_slot_name, mat.material_interface.get_path_name() if mat.material_interface else None)
    pa = old.physics_asset
    for bs in pa.get_editor_property("skeletal_body_setups"):
        ag = bs.get_editor_property("agg_geom")
        p("old body", bs.get_editor_property("bone_name"), "boxes", len(ag.get_editor_property("box_elems")),
          "spheres", len(ag.get_editor_property("sphere_elems")), "sphyls", len(ag.get_editor_property("sphyl_elems")),
          "convex", len(ag.get_editor_property("convex_elems")))
        for b in ag.get_editor_property("box_elems"):
            p("   box center", b.get_editor_property("center"), "rot", b.get_editor_property("rotation"), "xyz", b.x, b.y, b.z)
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_BUILD1_DONE")
