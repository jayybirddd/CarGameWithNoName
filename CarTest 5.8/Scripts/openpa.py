import unreal
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play() if hasattr(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem), "editor_request_end_play") else None
pa = unreal.load_asset("/Game/Car/Mesh/SK_Car_PhysicsAsset")
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([pa])
