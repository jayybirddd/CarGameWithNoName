# v2 scripted test drive (PIE). Logs gears / boost / antenna / air pitch to Saved/claude_v2_test.txt
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_test.txt"
S = {"t0": None, "last": -1, "lines": [], "h": None, "phase": "", "done": False, "tp1": False, "tp2": False}
def log(s): S["lines"].append(s) if not s.startswith("setv err") or len(S["lines"]) < 5 else None
def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def car():
    w = world()
    if not w: return None
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn): return a
def setv(a, k, v):
    try: a.set_editor_property(k, v)
    except Exception as e: log("setv err %s %s" % (k, e))
def getv(a, k):
    try: return a.get_editor_property(k)
    except Exception: return None
def finish():
    if S["done"]: return
    S["done"] = True
    unreal.unregister_slate_post_tick_callback(S["h"])
    with open(OUT, "w") as f: f.write("\n".join(S["lines"]))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    unreal.log("CLAUDE_V2_TEST_DONE")
def tick(dt):
    try:
        a = car()
        if S["t0"] is None:
            if a is None: return
            S["t0"] = time.time()
        t = time.time() - S["t0"]
        if a is None: return
        mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
        mesh = a.get_editor_property("mesh")
        # ---- scenario
        if t < 1.0: ph = "settle"
        elif t < 3.5: ph = "air+throttle"
        elif t < 6.0: ph = "air+brake"
        elif t < 8.0: ph = "settle2"
        elif t < 12.0: ph = "throttle"
        elif t < 15.0: ph = "throttle+boost"
        elif t < 21.0: ph = "brake(regen)"
        else: ph = "end"
        if ph != S["phase"]:
            S["phase"] = ph; log("== phase %s at %.2f" % (ph, t))
            if ph.startswith("air"):
                loc = a.get_actor_location(); rot = a.get_actor_rotation()
                a.set_actor_location_and_rotation(unreal.Vector(loc.x, loc.y, loc.z + 900.0), unreal.Rotator(0.0, rot.yaw, 0.0), False, True)
                mesh.set_physics_linear_velocity(a.get_actor_forward_vector() * 1200.0)
                mesh.set_physics_angular_velocity_in_degrees(unreal.Vector(0, 0, 0))
        thr = 1.0 if ph in ("throttle", "throttle+boost", "air+throttle") else 0.0
        brk = 1.0 if ph in ("air+brake", "brake(regen)") else 0.0
        mv.set_throttle_input(thr); mv.set_brake_input(brk)
        setv(a, "BoostHeld", ph == "throttle+boost")
        setv(a, "PitchAxis", thr - brk if ph.startswith("air") else 0.0)
        if ph == "end":
            finish(); return
        if t - S["last"] < 0.2: return
        S["last"] = t
        rot = a.get_actor_rotation()
        line = "t%5.2f %-15s spd %6.1f rpm %5.0f gear %2d auto %s | boost %.2f boosting %s fx %.2f timer %.1f | air %s pitch %6.1f pav %6.1f" % (
            t, ph, mv.get_forward_speed() * 0.036, mv.get_engine_rotation_speed(), mv.get_current_gear(), mv.get_use_auto_gears(),
            getv(a, "BoostAmount") or 0, getv(a, "Boosting"), getv(a, "BoostFX") or 0, getv(a, "BoostRegenTimer") or 0,
            getv(a, "InAir"), rot.pitch, (mesh.get_physics_angular_velocity_in_degrees().dot(a.get_actor_right_vector())))
        try:
            ai = mesh.get_anim_instance()
            b = ai.get_editor_property("AntBend")
            base = mesh.get_socket_transform("DEF-ANTENAE0-001", unreal.RelativeTransformSpace.RTS_COMPONENT).translation
            tip = mesh.get_socket_transform("DEF-ANTENAE0-004", unreal.RelativeTransformSpace.RTS_COMPONENT).translation
            d = tip - base
            r = ai.get_editor_property("AntRot3")
            line += " | ant bend(%.1f,%.1f) rot(p%.1f r%.1f) tipoff(%.1f,%.1f,%.1f)" % (b.x, b.y, r.pitch, r.roll, d.x, d.y, d.z)
        except Exception as e:
            line += " | anterr %s" % e
        try:
            fl = a.get_editor_property("BoostFlameL")
            line += " flame %.2f" % fl.get_editor_property("relative_scale3d").z
        except Exception as e:
            line += " flerr %s" % e
        log(line)
    except Exception:
        log(traceback.format_exc()); finish()
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
