# v4: gathers every level into /Game/Levels under descriptive names.
# Each map is opened and saved under its new name (like "Save Current Level As"), then the old copy is deleted.
# Re-runnable: maps already moved are skipped.
import unreal, traceback, os
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v4_rename_levels.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
CONTENT = "D:/PersonalGameFiles/CarTest 5.8/Content"
MOVES = [("/Game/Car/Maps/CarTestTrack", "/Game/Levels/L_EarthTestTrack"),
         ("/Game/Car/Maps/CarTestMoonGrav", "/Game/Levels/L_MoonTestTrack"),
         ("/Game/Car/Maps/CarTestBoostCharge", "/Game/Levels/L_MoonBoostCharge"),
         ("/Game/Maps/CarTestMap", "/Game/Levels/L_Sandbox")]
def on_disk(p): return os.path.exists(CONTENT + p[len("/Game"):] + ".umap")
try:
    if not EAL.does_directory_exist("/Game/Levels"): EAL.make_directory("/Game/Levels")
    for old, new in MOVES:
        if on_disk(new): log("already moved", new); continue
        if not on_disk(old): log("!! missing", old); continue
        log("load", old, LES.load_level(old))
        w = UES.get_editor_world()
        ok = unreal.EditorLoadingAndSavingUtils.save_map(w, new)
        log("save as", new, ok, "editor world now", UES.get_editor_world().get_path_name(), "on disk", on_disk(new))
    # open a moved level so none of the old ones is loaded, then remove the old copies
    log("load", LES.load_level("/Game/Levels/L_EarthTestTrack"), UES.get_editor_world().get_path_name())
    for old, new in MOVES:
        if on_disk(new) and on_disk(old):
            log("delete old", old, EAL.delete_asset(old))
    for d in ("/Game/Car/Maps", "/Game/Maps"):
        left = EAL.list_assets(d, True, False)
        log("left in", d, [str(x) for x in left])
        if not left: log("remove empty folder", d, EAL.delete_directory(d))
    # point the project's startup / default map at the renamed track
    s = unreal.get_default_object(unreal.GameMapsSettings)
    log("maps settings before", s.get_editor_property("game_default_map"), s.get_editor_property("editor_startup_map"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V4_RENAME_DONE")
