# Fixes the redirector left in /Game/Maps after moving the HLOD asset, then removes the folder.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v4_fix_redirect.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    log("asset tools fixup methods", [m for m in dir(at) if "redirect" in m.lower() or "fixup" in m.lower()])
    red = unreal.load_asset("/Game/Maps/CarTestMap_HLOD0_Instancing")
    log("redirector", red)
    done = False
    for name in ("fixup_referencers", "fix_up_redirectors", "fixup_redirectors"):
        if hasattr(at, name):
            getattr(at, name)([red]); log("ran", name); done = True; break
    if not done:
        # fallback: re-save everything that references it, then delete the redirector
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        refs = [str(x) for x in ar.get_referencers("/Game/Maps/CarTestMap_HLOD0_Instancing", unreal.AssetRegistryDependencyOptions())]
        log("referencers", refs)
        for r in refs: log("resave", r, EAL.save_asset(r, only_if_is_dirty=False))
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    log("referencers now", [str(x) for x in ar.get_referencers("/Game/Maps/CarTestMap_HLOD0_Instancing", unreal.AssetRegistryDependencyOptions())])
    log("left", [str(a.package_name) for a in ar.get_assets_by_path("/Game/Maps", True)])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V4_FIX_REDIRECT_DONE")
