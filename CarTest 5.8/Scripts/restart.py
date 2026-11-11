import unreal, subprocess, os
w = unreal.EditorLevelLibrary.get_editor_world()
p = w.get_path_name()
unreal.log("CLAUDE world " + p)
if p.startswith("/Temp/"):
    unreal.EditorLoadingAndSavingUtils.save_map(w, "/Game/Maps/CarTestMap")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
exe = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.engine_dir()), "Binaries/Win64/UnrealEditor.exe")
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.get_project_file_path())
subprocess.Popen([exe, proj])
unreal.SystemLibrary.quit_editor()
