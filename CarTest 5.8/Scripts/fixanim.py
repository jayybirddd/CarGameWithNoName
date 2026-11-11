import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_fixanim.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
SCALE = 101.6978988647461
try:
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in reg.get_assets_by_path("/Game/Car/Animations", recursive=False):
        if str(ad.asset_class_path.asset_name) != "AnimSequence": continue
        a = unreal.load_asset(str(ad.package_name))
        ctrl = a.get_editor_property("controller")
        names = AL.get_animation_track_names(a)
        ctrl.open_bracket(unreal.Text("rescale"), False)
        n = 0; sample = None
        for tn in names:
            pos = list(AL.get_raw_track_position_data(a, tn))
            rot = list(AL.get_raw_track_rotation_data(a, tn))
            scl = list(AL.get_raw_track_scale_data(a, tn))
            if not pos: continue
            m = max(len(pos), len(rot), len(scl))
            pos = pos + [pos[-1]] * (m - len(pos)); rot = rot + [rot[-1]] * (m - len(rot)); scl = scl + [scl[-1]] * (m - len(scl))
            npos = [unreal.Vector(p.x * SCALE, p.y * SCALE, p.z * SCALE) for p in pos]
            if str(tn).lower() == "def-body": sample = (pos[0], npos[0])
            if ctrl.set_bone_track_keys(tn, npos, rot, scl, False): n += 1
            else: log("fail", ad.asset_name, tn)
        ctrl.close_bracket(False)
        if str(ad.asset_name).endswith("_Add"):
            a.set_editor_property("ref_pose_type", unreal.AdditiveBasePoseType.ABPT_LOCAL_ANIM_FRAME)
            a.set_editor_property("ref_frame_index", 0)
        EAL.save_asset(str(ad.package_name))
        log("rescaled", ad.asset_name, n, "tracks; def-body", sample)
    # verify world pose of DEF-BODY on the mesh
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("optional_skeletal_mesh", unreal.load_asset("/Game/Car/Mesh/SK_Car"))
    for nm, t in [("AS_Idle", 0.0), ("AS_TurnLeft", 1.0), ("AS_Accelerate", 0.75)]:
        a = unreal.load_asset("/Game/Car/Animations/" + nm)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(a, t, opts)
        for b in ["DEF-BODY", "MASTER-ROTATION", "DEF-FRONT-WHEEL_L"]:
            tr = unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD); r = tr.rotation.rotator()
            log("eval", nm, t, b, "loc(%.1f,%.1f,%.1f) rot(p%.1f,y%.1f,r%.1f) s%.2f" % (tr.translation.x, tr.translation.y, tr.translation.z, r.pitch, r.yaw, r.roll, tr.scale3d.x))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_FIXANIM_DONE")
