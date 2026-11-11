import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_cleanup2.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
reg = unreal.AssetRegistryHelpers.get_asset_registry()
try:
    try:
        log("move", EAL.rename_directory("/Game/Car_Rig_and_Anims", "/Game/_Old/Car_Rig_and_Anims"))
    except Exception as e:
        log("move err (first line)", str(e).splitlines()[0][:300])
    log("still at old path", len(reg.get_assets_by_path("/Game/Car_Rig_and_Anims", recursive=True)),
        "in _Old", len(reg.get_assets_by_path("/Game/_Old/Car_Rig_and_Anims", recursive=True)))
    reds = [ad for ad in reg.get_assets_by_path("/Game", recursive=True) if str(ad.asset_class_path.asset_name) == "ObjectRedirector"]
    objs = [o for o in (unreal.load_asset(str(r.package_name)) for r in reds) if o]
    try:
        if objs: unreal.AssetToolsHelpers.get_asset_tools().fixup_referencers(objs)
    except Exception as e: log("fixup err", str(e).splitlines()[0][:300])
    log("redirectors", len(objs), "left", len([ad for ad in reg.get_assets_by_path("/Game", recursive=True) if str(ad.asset_class_path.asset_name) == "ObjectRedirector"]))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    # sanity: the new car still loads cleanly
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    unreal.BlueprintEditorLibrary.compile_blueprint(car)
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    unreal.BlueprintEditorLibrary.compile_blueprint(abp)
    log("compiled ok")
except Exception:
    log(traceback.format_exc()[:2000])
with open(OUT, "w") as f: f.write("\n".join(L))
