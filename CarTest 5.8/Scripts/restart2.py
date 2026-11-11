import unreal, subprocess, os
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
exe = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.engine_dir()), "Binaries/Win64/UnrealEditor.exe")
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.get_project_file_path())
subprocess.Popen([exe, proj])
unreal.SystemLibrary.quit_editor()
