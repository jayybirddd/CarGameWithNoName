# Scripted drift on open floor: 3 s straight, 3 s full steer + drift button, then straight. Logs slip, drift timer and
# the boost payout. Optional globals: MAP, TELEPORT (x, y, yaw), STEER (drift steer, default 1.0).
import unreal, time, math, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_drift_test.txt"
_map = globals().get("MAP"); _tp = globals().get("TELEPORT", (-12000, 12000, 0)); _steer = globals().get("STEER", 1.0)
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
        a = cars[0]; mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
        if S["t0"] is None:
            a.set_actor_location_and_rotation(unreal.Vector(_tp[0], _tp[1], 120), unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(_tp[2])), False, True)
            S["t0"] = time.time(); S["b0"] = a.get_editor_property("BoostAmount"); return
        t = time.time() - S["t0"]
        drift = 3.0 <= t < 6.0
        steer = _steer if drift else 0.0
        mv.set_throttle_input(1.0 if t < 8.5 else 0.0); mv.set_brake_input(0.0); mv.set_steering_input(steer)
        a.set_editor_property("SteerAxis", steer); a.set_editor_property("DriftHeld", drift)
        if t - S["last"] >= 0.25:
            S["last"] = t
            v = a.get_velocity(); f = a.get_actor_forward_vector()
            sp = math.hypot(v.x, v.y)
            slip = math.degrees(math.atan2(v.x * f.y - v.y * f.x, v.x * f.x + v.y * f.y)) if sp > 50 else 0.0
            S["L"].append("t%5.2f kmh %5.1f slip %6.1f yaw %6.1f held %d drifting %d dtime %.2f boost %.3f lastcharge %.3f popup %.2f" % (
                t, mv.get_forward_speed() * 0.036, slip, a.get_actor_rotation().yaw, drift, a.get_editor_property("Drifting"),
                a.get_editor_property("DriftTime"), a.get_editor_property("BoostAmount"), a.get_editor_property("DriftLastCharge"), a.get_editor_property("DriftPopup")))
        if t > 10.0: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
if _map: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(_map)
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
