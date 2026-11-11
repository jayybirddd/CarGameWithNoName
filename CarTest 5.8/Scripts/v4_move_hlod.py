# Moves L_Sandbox's HLOD helper asset next to it, fixes the redirector, and removes the empty /Game/Maps folder.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v4_move_hlod.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
try:
    LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log("load", LES.load_level("/Game/Levels/L_EarthTestTrack"))
    src, dst = "/Game/Maps/CarTestMap_HLOD0_Instancing", "/Game/Levels/L_Sandbox_HLOD0_Instancing"
    if EAL.does_asset_exist(src):
        log("rename", EAL.rename_asset(src, dst))
    reds = [a for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path("/Game/Maps", True)]
    log("left in /Game/Maps", [str(a.package_name) + ":" + str(a.asset_class_path.asset_name) for a in reds])
    objs = [unreal.load_asset(str(a.package_name)) for a in reds if str(a.asset_class_path.asset_name) == "ObjectRedirector"]
    if objs:
        unreal.AssetToolsHelpers.get_asset_tools().fixup_referencers(objs)
        log("fixed redirectors", len(objs))
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    log("hlod referencers", [str(x) for x in ar.get_referencers(dst, unreal.AssetRegistryDependencyOptions())])
    log("save sandbox", LES.load_level("/Game/Levels/L_Sandbox"), LES.save_current_level())
    log("back", LES.load_level("/Game/Levels/L_EarthTestTrack"))
    log("left in /Game/Maps after", [str(a.package_name) for a in ar.get_assets_by_path("/Game/Maps", True)])
    if not EAL.list_assets("/Game/Maps", True, False): log("remove /Game/Maps", EAL.delete_directory("/Game/Maps"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V4_HLOD_DONE")
