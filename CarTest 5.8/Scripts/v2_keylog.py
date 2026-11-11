# Logs boost/gear state during PIE while real keys are pressed. Sends no input itself.
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_keylog.txt"
S = {"t0": None, "last": -1, "L": [], "h": None, "done": False}
def fin():
    S["done"] = True
    unreal.unregister_slate_post_tick_callback(S["h"])
    open(OUT, "w").write("\n".join(S["L"]))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
def tick(dt):
    if S["done"]: return
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not w: return
        cars = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
        if not cars: return
        a = cars[0]
        if S["t0"] is None: S["t0"] = time.time()
        t = time.time() - S["t0"]
        if t - S["last"] >= 0.25:
            S["last"] = t
            mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            S["L"].append("t%5.2f held %s boosting %s boost %.2f fx %.2f spd %.1f gear %d tgt %d auto %s" % (t, a.get_editor_property("BoostHeld"), a.get_editor_property("Boosting"), a.get_editor_property("BoostAmount"), a.get_editor_property("BoostFX"), mv.get_forward_speed() * 0.036, mv.get_current_gear(), mv.get_target_gear(), mv.get_use_auto_gears()))
        if t > 12.0: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
