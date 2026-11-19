# Debug: drives gates 1..N-1 by drops, then watches gate 0 closely (overlaps, GateHit each tick); also checks where the
# car ends up after falling.
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_gate0_debug.txt"
S = {"t0": None, "L": [], "h": None, "done": False, "i": 0, "next_t": 1.5, "watch": None}
def fin():
    S["done"] = True; unreal.unregister_slate_post_tick_callback(S["h"])
    open(OUT, "w").write("\n".join(S["L"])); unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
def drop(car, gate, behind=600.0, speed=2000.0):
    f = gate.get_actor_forward_vector(); p = gate.get_actor_location()
    car.set_actor_location_and_rotation(unreal.Vector(p.x - f.x * behind, p.y - f.y * behind, p.z + 80), gate.get_actor_rotation(), False, True)
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
            S["gates"] = sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if "RaceGate" in a.get_class().get_name()], key=lambda g: g.get_editor_property("GateIndex"))
            g0 = S["gates"][0]
            tr = [c for c in g0.get_components_by_class(unreal.BoxComponent)][0]
            S["L"].append("gate0 label %s index %d loc %s rot %s trigger extent %s profile %s gen overlaps %s" % (g0.get_actor_label(), g0.get_editor_property("GateIndex"), g0.get_actor_location(),
                g0.get_actor_rotation(), tr.get_editor_property("box_extent"), tr.get_collision_profile_name(), tr.get_editor_property("generate_overlap_events")))
            g1 = S["gates"][1]; tr1 = [c for c in g1.get_components_by_class(unreal.BoxComponent)][0]
            S["L"].append("gate1 index %d trigger extent %s profile %s" % (g1.get_editor_property("GateIndex"), tr1.get_editor_property("box_extent"), tr1.get_collision_profile_name()))
        t = time.time() - S["t0"]
        n = len(S["gates"])
        order = list(range(1, n)) + [0]
        if t >= S["next_t"] and S["i"] < len(order):
            k = order[S["i"]]; drop(car, S["gates"][k]); S["i"] += 1; S["next_t"] = t + 0.7
            if k == 0: S["watch"] = t
        if S["watch"] is not None and t - S["watch"] < 1.2:
            ov = [a.get_actor_label() for a in car.get_overlapping_actors(None)]
            S["L"].append("t%5.2f next %d hit %d lap %d car (%.0f,%.0f,%.0f) overlapping %s" % (t, m.get_editor_property("NextGate"), m.get_editor_property("GateHit"), m.get_editor_property("Lap"),
                *car.get_actor_location().to_tuple(), ov))
        if S["watch"] is not None and 1.2 <= t - S["watch"] < 1.3 and not S.get("fell"):
            S["fell"] = True; p = car.get_actor_location(); car.set_actor_location(unreal.Vector(p.x, p.y, m.get_editor_property("FallZ") - 500), False, True)
            S["L"].append("t%5.2f dropped below FallZ; last gate %d" % (t, m.get_editor_property("LastGate")))
        if S.get("fell") and t - S["watch"] > 2.0:
            lg = S["gates"][m.get_editor_property("LastGate")].get_actor_location(); p = car.get_actor_location()
            S["L"].append("t%5.2f after fall car (%.0f,%.0f,%.0f) last gate at (%.0f,%.0f,%.0f)" % (t, p.x, p.y, p.z, lg.x, lg.y, lg.z)); fin()
        if t > 30: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(globals().get("MAP", "/Game/Levels/L_Track1"))
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
