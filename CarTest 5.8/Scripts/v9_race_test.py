# Race logic test (PIE): drops the car 6 m in front of each gate in order, moving through it, for every lap; also tries
# an out-of-order gate (should be ignored) and a fall off the track (should respawn at the last gate). Logs the
# manager's lap / next gate / time and the car's Won flag. Optional globals: MAP.
import unreal, time, math, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_race_test.txt"
_map = globals().get("MAP", "/Game/Levels/L_Track1")
S = {"t0": None, "L": [], "h": None, "done": False, "plan": None, "i": 0, "next_t": 2.0}
def fin():
    S["done"] = True
    unreal.unregister_slate_post_tick_callback(S["h"])
    open(OUT, "w").write("\n".join(S["L"]))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
def mstate(m, car):
    return "lap %d next %d time %.1f finished %d last %d popup %.1f won %d" % (m.get_editor_property("Lap"), m.get_editor_property("NextGate"), m.get_editor_property("RaceTime"),
        m.get_editor_property("Finished"), m.get_editor_property("LastGate"), m.get_editor_property("GatePopup"), car.get_editor_property("Won"))
def drop(car, gate, behind=600.0, speed=2000.0):
    f = gate.get_actor_forward_vector(); p = gate.get_actor_location()
    x, y = p.x - f.x * behind, p.y - f.y * behind
    w = gate.get_world()
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, p.z + 1500), unreal.Vector(x, y, p.z - 1500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [car], unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[0] if isinstance(r[0], unreal.HitResult) else r[-1]
    z = r.to_tuple()[4].z if r and r.to_tuple()[0] else p.z
    car.set_actor_location_and_rotation(unreal.Vector(x, y, z + 80), gate.get_actor_rotation(), False, True)
    mesh = car.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_physics_linear_velocity(unreal.Vector(f.x * speed, f.y * speed, 0)); mesh.set_physics_angular_velocity_in_degrees(unreal.Vector(0, 0, 0))
def tick(dt):
    if S["done"]: return
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not w: return
        cars = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
        mgrs = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if "RaceManager" in a.get_class().get_name()]
        if not cars or not mgrs: return
        car, m = cars[0], mgrs[0]
        if S["t0"] is None:
            S["t0"] = time.time()
            gates = sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if "RaceGate" in a.get_class().get_name()], key=lambda g: g.get_editor_property("GateIndex"))
            n = m.get_editor_property("NumGates")
            S["L"].append("map %s gates %d NumGates %d Laps %d FallZ %.0f" % (w.get_path_name(), len(gates), n, m.get_editor_property("Laps"), m.get_editor_property("FallZ")))
            plan = [("gate", gates[3], "out of order (expect ignored)")]
            for lap in range(m.get_editor_property("Laps")):
                for k in list(range(1, n)) + [0]:
                    plan.append(("gate", gates[k], "lap %d gate %d" % (lap + 1, k)))
                    if lap == 0 and k == 4: plan.append(("fall", None, "fall off (expect respawn at gate 4)"))
            S["plan"] = plan
        t = time.time() - S["t0"]
        if t >= S["next_t"] and S["i"] < len(S["plan"]):
            kind, g, what = S["plan"][S["i"]]
            S["L"].append("t%5.1f before %-36s %s" % (t, what, mstate(m, car)))
            if kind == "gate": drop(car, g)
            else:
                p = car.get_actor_location(); car.set_actor_location(unreal.Vector(p.x, p.y, m.get_editor_property("FallZ") - 500), False, True)
            S["i"] += 1; S["next_t"] = t + (1.2 if kind == "fall" else 0.7)
        if S["i"] >= len(S["plan"]) and t > S["next_t"] + 1.0:
            p = car.get_actor_location()
            S["L"].append("t%5.1f END %s car at (%.0f,%.0f,%.0f)" % (t, mstate(m, car), p.x, p.y, p.z)); fin()
        if t > 90: S["L"].append("timeout"); fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(_map)
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
