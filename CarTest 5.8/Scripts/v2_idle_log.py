# Starts PIE and records the antenna spring: sits idling for the summary window (0.5-9 s), then W may be held.
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_idle_log.txt"
S = {"t0": None, "last": -1, "L": [], "h": None, "done": False, "x": [], "y": []}
def fin():
    S["done"] = True
    unreal.unregister_slate_post_tick_callback(S["h"])
    if S["y"]:
        S["L"].append("after settle: bendX %.2f..%.2f bendY %.2f..%.2f samples %d" % (min(S["x"]), max(S["x"]), min(S["y"]), max(S["y"]), len(S["y"])))
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
        ai = a.get_component_by_class(unreal.SkeletalMeshComponent).get_anim_instance()
        if ai is None: return
        if S["t0"] is None: S["t0"] = time.time()
        t = time.time() - S["t0"]
        b = ai.get_editor_property("AntBend"); s = ai.get_editor_property("BodySmooth")
        if 0.5 < t < 9.0:
            S["x"].append(b.x); S["y"].append(b.y)
        if t - S["last"] >= 0.1:
            S["last"] = t
            S["L"].append("t%5.2f spd %.1f bend %.2f %.2f avg z %.2f pitch %.2f flag %.2f" % (t, a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent).get_forward_speed() * 0.036, b.x, b.y, s.x, s.y, s.z))
        if t > 15.0: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
