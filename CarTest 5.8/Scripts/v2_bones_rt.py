import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_bones_rt.txt"
S = {"t0": None, "h": None, "done": False, "L": [], "n": 0}
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
        mesh = a.get_editor_property("mesh")
        mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
        mv.set_throttle_input(1.0 if t > 1.5 else 0.0)
        if S["n"] == 0:
            for b in ("DEF-BASE-ANTENNAE", "DEF-ANTENAE0-001", "DEF-ANTENAE0-002", "DEF-ANTENAE0-003", "DEF-ANTENAE0-004", "CTRL-ANTENAE", "TGT-ANTENAE0-002"):
                S["L"].append("parent %s <- %s" % (b, mesh.get_parent_bone(b)))
            S["L"].append("vis tick option %s urO %s" % (mesh.get_editor_property("visibility_based_anim_tick_option"), mesh.get_editor_property("enable_update_rate_optimizations")))
        S["n"] += 1
        if S["n"] % 15 == 0:
            ai = mesh.get_anim_instance()
            r = ai.get_editor_property("AntennaRot")
            parts = ["t%.2f rot(p%.1f r%.1f)" % (t, r.pitch, r.roll)]
            for b in ("DEF-ANTENAE0-001", "DEF-ANTENAE0-002", "DEF-ANTENAE0-004"):
                tr = mesh.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT)
                rr = tr.rotation.rotator()
                parts.append("%s loc(%.1f,%.1f,%.1f) rot(p%.1f y%.1f r%.1f)" % (b[-3:], tr.translation.x, tr.translation.y, tr.translation.z, rr.pitch, rr.yaw, rr.roll))
            S["L"].append(" ".join(parts))
        if t > 5.0: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
