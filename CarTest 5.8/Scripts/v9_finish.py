# v9 wrap-up: tutorial leads to Track 1, sandbox HLOD redirector cleanup, then rebuild the menus (v5_assets.py).
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_finish.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    log("load tutorial", LES.load_level("/Game/Levels/L_Tutorial"))
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == "LevelRules":
            a.set_editor_property("NextLevel", unreal.Name("L_Track1")); log("tutorial next ->", a.get_editor_property("NextLevel"))
    log("saved", LES.save_current_level())
    red = "/Game/Levels/L_Sandbox_HLOD0_Instancing"
    if EAL.does_asset_exist(red):
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        refs = [str(x) for x in ar.get_referencers(red, unreal.AssetRegistryDependencyOptions())]
        log("hlod redirector referencers", refs)
        for r in refs: log("resave", r, EAL.save_asset(r, only_if_is_dirty=False))
        if not [str(x) for x in ar.get_referencers(red, unreal.AssetRegistryDependencyOptions())]:
            log("delete redirector", EAL.delete_asset(red))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
