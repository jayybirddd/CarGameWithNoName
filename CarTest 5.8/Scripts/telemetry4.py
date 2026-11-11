import unreal, time
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_telemetry.txt"
state = {"t0": None, "last": 0, "lines": [], "h": None}
def find():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if not w: return None
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn):
        return a
def tick(dt):
    if state["t0"] is None:
        if find() is None: return
        state["t0"] = time.time()
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
            try:
                mesh = a.get_editor_property("mesh")
                ai = mesh.get_anim_instance()
                av = []
                for k in ("IsAccelerating", "IsBraking", "LeanLeft", "LeanRight", "Speed"):
                    v = ai.get_editor_property(k)
                    av.append("%s=%s" % (k, round(v, 2) if isinstance(v, float) else v))
                br = unreal.MathLibrary.make_relative_transform(mesh.get_socket_transform("DEF-BODY"), a.get_actor_transform()).rotation.rotator()
                wr = unreal.MathLibrary.make_relative_transform(mesh.get_socket_transform("DEF-FRONT-WHEEL_L"), a.get_actor_transform()).rotation.rotator()
                line += " || " + " ".join(av) + " body(p%.1f r%.1f) fwheel(p%.0f y%.1f)" % (br.pitch, br.roll, wr.pitch, wr.yaw)
            except Exception as e:
                line += " || animerr %s" % e
            for i in range(mv.get_num_wheels()):
                s = mv.get_wheel_state(i)
                d = s.to_dict()
                ws.append("w%d " % i + " ".join("%s=%s" % (k, (round(v, 2) if isinstance(v, float) else v)) for k, v in d.items() if k.lower() in ("in_contact","b_in_contact","slip_angle","skid_magnitude","is_skidding","is_slipping","b_is_skidding","b_is_slipping","spring_force","normalized_suspension_length","driving_surface","b_is_valid","is_valid") or "contact" in k.lower() or "slip" in k.lower() or "susp" in k.lower()))
                if i == 0 and len(state["lines"]) == 0: state["lines"].append("keys " + ",".join(d.keys()))
            state["lines"].append(line)
    except Exception as e:
        state["lines"].append("err %s" % e)
    if now > 20:
        unreal.unregister_slate_post_tick_callback(state["h"])
        with open(OUT, "w") as f: f.write("\n".join(state["lines"]))
        unreal.log("CLAUDE_TELEMETRY_DONE")
state["h"] = unreal.register_slate_post_tick_callback(tick)
