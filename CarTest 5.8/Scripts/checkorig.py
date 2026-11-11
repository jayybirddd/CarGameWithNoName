import unreal
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_checkorig.txt"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level("/Game/Car/Maps/CarTestTrack")
ws = unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
with open(OUT, "w") as f:
    f.write("orig override %s %s gm %s\n" % (ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), ws.get_editor_property("default_game_mode").get_name()))
