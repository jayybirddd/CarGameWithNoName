import unreal, time
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_telemetry.txt"
state = {"t0": time.time(), "last": 0, "lines": [], "h": None}
def find():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if not w: return None
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn):
        return a
def tick(dt):
    now = time.time() - state["t0"]
    if now - state["last"] < 0.25: return
    state["last"] = now
    try:
        a = find()
        if a:
            mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            sn = mv.get_snapshot() if False else None
            line = "t%.2f spd %.1f kmh rpm %.0f gear %d tgt %d thr %.2f brk %.2f hb %.2f steer %.2f loc %s" % (
                now, mv.get_forward_speed() * 0.036, mv.get_engine_rotation_speed(), mv.get_current_gear(), mv.get_target_gear(),
                mv.get_throttle_input(), mv.get_brake_input(), mv.get_handbrake_input(), mv.get_steering_input(), a.get_actor_location())
            ws = []
            for i in range(mv.get_num_wheels()):
                s = mv.get_wheel_state(i)
                ws.append("w%d contact=%s slip=%.2f skid=%.2f spin=%.0f" % (i, s.get_editor_property("in_contact"), s.get_editor_property("slip_angle"), s.get_editor_property("skid_magnitude"), s.get_editor_property("angular_velocity")))
            state["lines"].append(line + " | " + " ; ".join(ws))
    except Exception as e:
        state["lines"].append("err %s" % e)
    if now > 14:
        unreal.unregister_slate_post_tick_callback(state["h"])
        with open(OUT, "w") as f: f.write("\n".join(state["lines"]))
        unreal.log("CLAUDE_TELEMETRY_DONE")
state["h"] = unreal.register_slate_post_tick_callback(tick)
