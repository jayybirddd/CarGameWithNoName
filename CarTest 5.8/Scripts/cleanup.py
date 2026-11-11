import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_cleanup.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
SCALE = 101.6978988647461
try:
    # rescale the raw reference clips so they match the fixed skeleton
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in reg.get_assets_by_path("/Game/Car/Animations/Raw", recursive=False):
        if str(ad.asset_class_path.asset_name) != "AnimSequence": continue
        a = unreal.load_asset(str(ad.package_name))
        names = [str(n) for n in AL.get_animation_track_names(a)]
        nk = AL.get_num_keys(a)
        frames = [list(AL.get_bone_poses_for_frame(a, names, k, False)) for k in range(nk)]
        ctrl = a.get_editor_property("controller")
        ctrl.open_bracket(unreal.Text("rescale"), False)
        n = 0
        for i, tn in enumerate(names):
            if tn.lower() == "car":
                pos = [unreal.Vector(0, 0, 0) for f in frames]; rot = [unreal.Quat() for f in frames]
            else:
                pos = [f[i].translation * SCALE for f in frames]; rot = [f[i].rotation for f in frames]
            if ctrl.set_bone_track_keys(tn, pos, rot, [unreal.Vector(1, 1, 1)] * nk, False): n += 1
        ctrl.close_bracket(False)
        EAL.save_asset(str(ad.package_name))
        log("raw rescaled", ad.asset_name, n)
    # move superseded content into _Old (nothing is deleted)
    for src, dst in [("/Game/Car-Game", "/Game/_Old/Car-Game"), ("/Game/Car_Rig_and_Anims", "/Game/_Old/Car_Rig_and_Anims")]:
        if EAL.does_directory_exist(src):
            log("move", src, EAL.rename_directory(src, dst))
    # fix redirectors
    reds = [ad for ad in reg.get_assets_by_path("/Game", recursive=True) if str(ad.asset_class_path.asset_name) == "ObjectRedirector"]
    objs = [unreal.load_asset(str(r.package_name)) for r in reds]
    objs = [o for o in objs if o]
    if objs:
        unreal.AssetToolsHelpers.get_asset_tools().fixup_referencers(objs)
    log("redirectors fixed", len(objs))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("saved")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_CLEANUP_DONE")
