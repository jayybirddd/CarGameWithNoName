# Passive PIE logger for the Moon map test: records every 0.1 s while real keys are pressed. Sends no input itself.
import unreal, time, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_moon_drive_log.txt"
DUR = 32.0
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
        mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
        mesh = a.get_component_by_class(unreal.SkeletalMeshComponent)
        ai = mesh.get_anim_instance()
        if S["t0"] is None:
            S["t0"] = time.time()
            ws = w.get_world_settings(); pc = unreal.GameplayStatics.get_player_controller(w, 0)
            try: hud = pc.get_hud().get_class().get_name()
            except Exception as e: hud = "? %s" % e
            S["L"].append("map %s pawn %s AirStabilize %.2f gravity override %s %.1f hud %s" % (w.get_path_name(), a.get_class().get_name(), a.get_editor_property("AirStabilize"),
                          ws.get_editor_property("global_gravity_set"), ws.get_editor_property("global_gravity_z"), hud))
        t = time.time() - S["t0"]
        if t - S["last"] >= 0.1:
            S["last"] = t
            loc = a.get_actor_location(); r = a.get_actor_rotation()
            av = mesh.get_physics_angular_velocity_in_degrees()
            lav = unreal.MathLibrary.inverse_transform_direction(a.get_actor_transform(), av)
            b = ai.get_editor_property("AntBend") if ai else unreal.Vector()
            S["L"].append("t%5.2f spd %5.1f z %6.0f x %6.0f pitch %6.1f pitchRate %6.1f air %d pAxis %5.2f gear %d tgt %d auto %d boost %.2f held %d boosting %d fx %.2f ant %.1f %.1f" % (
                t, mv.get_forward_speed() * 0.036, loc.z, loc.x, r.pitch, lav.y, a.get_editor_property("InAir"), a.get_editor_property("PitchAxis"),
                mv.get_current_gear(), mv.get_target_gear(), mv.get_use_auto_gears(), a.get_editor_property("BoostAmount"), a.get_editor_property("BoostHeld"),
                a.get_editor_property("Boosting"), a.get_editor_property("BoostFX"), b.x, b.y))
        if t > DUR: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
