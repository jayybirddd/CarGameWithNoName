import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_fixanim2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
SCALE = 101.6978988647461
try:
    a0 = unreal.load_asset("/Game/Car/Animations/AS_Idle")
    dm = a0.get_editor_property("data_model_interface")
    log("dm methods", [x for x in dir(dm) if not x.startswith("_") and x not in dir(unreal.Object)])
    log("getbonepose doc", (AL.get_bone_poses_for_frame.__doc__ or "")[:600])
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in reg.get_assets_by_path("/Game/Car/Animations", recursive=False):
        if str(ad.asset_class_path.asset_name) != "AnimSequence": continue
        a = unreal.load_asset(str(ad.package_name))
        dm = a.get_editor_property("data_model_interface")
        names = [str(n) for n in AL.get_animation_track_names(a)]
        nkeys = AL.get_num_keys(a)
        # sample local poses per key
        frames = []
        for k in range(nkeys):
            frames.append(list(AL.get_bone_poses_for_frame(a, names, k, False)))
        ctrl = a.get_editor_property("controller")
        ctrl.open_bracket(unreal.Text("rescale"), False)
        n = 0; first = None
        for i, tn in enumerate(names):
            pos = [unreal.Vector(f[i].translation.x * SCALE, f[i].translation.y * SCALE, f[i].translation.z * SCALE) for f in frames]
            rot = [f[i].rotation for f in frames]
            scl = [unreal.Vector(1, 1, 1) for f in frames]
            if tn.lower() == "def-body": first = (frames[0][i].translation, pos[0])
            if ctrl.set_bone_track_keys(tn, pos, rot, scl, False): n += 1
            else: log("fail", ad.asset_name, tn)
        ctrl.close_bracket(False)
        if str(ad.asset_name).endswith("_Add"):
            a.set_editor_property("ref_pose_type", unreal.AdditiveBasePoseType.ABPT_LOCAL_ANIM_FRAME)
            a.set_editor_property("ref_frame_index", 0)
        EAL.save_asset(str(ad.package_name))
        log("rescaled", ad.asset_name, "keys", nkeys, "tracks", n, "def-body", first)
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("optional_skeletal_mesh", unreal.load_asset("/Game/Car/Mesh/SK_Car"))
    for nm, t in [("AS_Idle", 0.0), ("AS_TurnLeft", 1.0), ("AS_Accelerate", 0.75), ("AS_Decelerate", 0.5)]:
        a = unreal.load_asset("/Game/Car/Animations/" + nm)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(a, t, opts)
        for b in ["DEF-BODY", "DEF-ANTENAE0-004"]:
            tr = unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD); r = tr.rotation.rotator()
            log("eval", nm, t, b, "loc(%.1f,%.1f,%.1f) rot(p%.1f,y%.1f,r%.1f) s%.2f" % (tr.translation.x, tr.translation.y, tr.translation.z, r.pitch, r.yaw, r.roll, tr.scale3d.x))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_FIXANIM2_DONE")
