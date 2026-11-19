# v9: moves the existing levels into /Game/Levels/Testing with a TEST_ prefix (they're test beds, not playable levels).
# Each map is saved under its new name ("Save Current Level As"), then the old copy is deleted. Re-runnable.
# The open level is saved first so its unsaved edits are kept and switching levels doesn't prompt.
import unreal, traceback, os
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_rename_tests.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
CONTENT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Content"
MOVES = [("/Game/Levels/L_EarthTestTrack", "/Game/Levels/Testing/TEST_EarthTestTrack"),
         ("/Game/Levels/L_MoonTestTrack", "/Game/Levels/Testing/TEST_MoonTestTrack"),
         ("/Game/Levels/L_EarthBoostCharge", "/Game/Levels/Testing/TEST_EarthBoostCharge"),
         ("/Game/Levels/L_MoonBoostCharge", "/Game/Levels/Testing/TEST_MoonBoostCharge"),
         ("/Game/Levels/L_Sandbox", "/Game/Levels/Testing/TEST_Sandbox"),
         ("/Game/Levels/l_TestingTrack", "/Game/Levels/Testing/TEST_TrackPrototype")]
def on_disk(p): return os.path.exists(CONTENT + p[len("/Game"):] + ".umap")
try:
    log("save open level", UES.get_editor_world().get_path_name(), LES.save_current_level())
    if not EAL.does_directory_exist("/Game/Levels/Testing"): EAL.make_directory("/Game/Levels/Testing")
    for old, new in MOVES:
        if on_disk(new): log("already moved", new); continue
        if not on_disk(old): log("!! missing", old); continue
        log("load", old, LES.load_level(old))
        log("save as", new, unreal.EditorLoadingAndSavingUtils.save_map(UES.get_editor_world(), new), "on disk", on_disk(new))
    log("load", LES.load_level("/Game/Levels/Testing/TEST_EarthTestTrack"), UES.get_editor_world().get_path_name())
    for old, new in MOVES:
        if on_disk(new) and on_disk(old):
            log("delete old", old, EAL.delete_asset(old))
    # the sandbox's HLOD helper asset follows it into the Testing folder
    hl, hl_new = "/Game/Levels/L_Sandbox_HLOD0_Instancing", "/Game/Levels/Testing/TEST_Sandbox_HLOD0_Instancing"
    if EAL.does_asset_exist(hl): log("move hlod", EAL.rename_asset(hl, hl_new))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V9_RENAME_DONE")
