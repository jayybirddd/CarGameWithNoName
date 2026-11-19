# v3 PIE logger: opens MAP (if given), starts PIE, records pads / mines / lives every 0.1 s. Sends no input.
# Optional globals before exec: MAP = "/Game/Levels/...", LIVES = n (sets the car's lives at spawn), DUR = seconds.
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v3_log.txt"
_map = globals().get("MAP"); _lives = globals().get("LIVES"); _dur = globals().get("DUR", 25.0); _tp = globals().get("TELEPORT")
S = {"t0": None, "last": -1, "L": [], "h": None, "done": False, "set": False, "world": None}
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
        if S["t0"] is None:
            S["t0"] = time.time(); S["world"] = w.get_path_name()
            pads = len(unreal.GameplayStatics.get_all_actors_with_tag(w, "x")) if False else None
            S["L"].append("map %s pawn %s lives %d/%d padsCharge %s regen %.3f boost %.2f" % (w.get_path_name(), a.get_class().get_name(), a.get_editor_property("Lives"),
                          a.get_editor_property("MaxLives"), a.get_editor_property("PadsChargeMeter"), a.get_editor_property("BoostRegenPerSec"), a.get_editor_property("BoostAmount")))
        if not S["set"]:
            S["set"] = True
            if _lives is not None: a.set_editor_property("Lives", int(_lives)); S["L"].append("set lives %d" % _lives)
            if _tp is not None:   # start somewhere open: (x, y, yaw)
                a.set_actor_location_and_rotation(unreal.Vector(_tp[0], _tp[1], 120), unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(_tp[2])), False, True)
        if w.get_path_name() != S["world"]:
            S["L"].append("WORLD CHANGED -> %s (level restarted)" % w.get_path_name()); S["world"] = w.get_path_name()
        t = time.time() - S["t0"]
        if t - S["last"] >= 0.1:
            S["last"] = t
            mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            loc = a.get_actor_location()
            S["L"].append("t%5.2f spd %5.1f x %6.0f z %5.0f lives %d cd %.2f out %d pad %.2f boost %.2f fx %.2f held %d drifting %d dtime %.2f lastcharge %.2f popup %.2f yaw %.0f" % (t, mv.get_forward_speed() * 0.036, loc.x, loc.z,
                a.get_editor_property("Lives"), a.get_editor_property("HitCooldown"), a.get_editor_property("OutOfLives"), a.get_editor_property("PadBoostTimer"),
                a.get_editor_property("BoostAmount"), a.get_editor_property("BoostFX"), a.get_editor_property("BoostHeld"),
                a.get_editor_property("Drifting"), a.get_editor_property("DriftTime"), a.get_editor_property("DriftLastCharge"), a.get_editor_property("DriftPopup"), a.get_actor_rotation().yaw))
        wr_ = [x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if "CarWreck" in x.get_name()]
        if wr_ and t - S.get("wlast", -1) >= 0.2 and S.get("wn", 0) < 15:
            S["wlast"] = t; S["wn"] = S.get("wn", 0) + 1
            S["L"].append("  wreck age %.2f " % wr_[0].get_editor_property("Age") + " ".join("%s(%d,%d,%d)%s" % (c.get_name()[:7], *[round(v) for v in c.get_world_location().to_tuple()], "" if c.is_visible() else "hid")
                for c in wr_[0].get_components_by_class(unreal.BoxComponent)) + " fire %.1f" % [c for c in wr_[0].get_components_by_class(unreal.StaticMeshComponent) if "Fire" in c.get_name()][0].get_editor_property("relative_scale3d").x)
        if t > _dur: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
if _map: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(_map)
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
