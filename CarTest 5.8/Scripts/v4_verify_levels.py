# Opens each level in /Game/Levels and reports its contents, gravity, game mode and level rules.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v4_verify_levels.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for lv in ("L_Sandbox", "L_MoonTestTrack", "L_MoonBoostCharge", "L_EarthTestTrack"):
        p = "/Game/Levels/" + lv
        log("==", p, "load", LES.load_level(p), UES.get_editor_world().get_path_name())
        ws = UES.get_editor_world().get_world_settings()
        gm = ws.get_editor_property("default_game_mode")
        acts = EAS.get_all_level_actors()
        counts = {}
        for a in acts:
            k = a.get_class().get_name(); counts[k] = counts.get(k, 0) + 1
        log("  gravity", ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), "gm", gm.get_name() if gm else None)
        log("  actors", len(acts), {k: v for k, v in sorted(counts.items()) if v})
        for a in acts:
            if a.get_class().get_name() == "BP_LevelRules_C":
                log("  rules", {k: a.get_editor_property(k) for k in ("BoostRegenEnabled", "PadsChargeMeter", "StartingLives", "StartingBoost")})
    hl = "/Game/Maps/CarTestMap_HLOD0_Instancing"
    log("hlod referencers", [str(x) for x in ar.get_referencers(hl, unreal.AssetRegistryDependencyOptions())] if unreal.EditorAssetLibrary.does_asset_exist(hl) else "gone")
    log("in registry", [str(x.package_name) for x in ar.get_assets_by_path("/Game/Car/Maps", True)], [str(x.package_name) for x in ar.get_assets_by_path("/Game/Levels", True)])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V4_VERIFY_DONE")
