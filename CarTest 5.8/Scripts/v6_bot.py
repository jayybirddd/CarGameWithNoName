# Test autopilot for the track: each frame it traces down at points ahead of the car in a fan of directions,
# steers toward the middle of the widest run of directions that still have road under them, and lifts off when that
# run is narrow. Logs speed, gear, whether the car is over the road, falls, and distance driven. Optional globals:
# MAP, DUR (s), DRIFT_IN_CORNERS (hold the drift button when steering hard), TOP (throttle cap 0-1).
import unreal, time, math, traceback
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_bot.txt"
_map = globals().get("MAP"); _dur = globals().get("DUR", 60.0); _drift = globals().get("DRIFT_IN_CORNERS", False); _top = globals().get("TOP", 1.0)
ANGLES = list(range(-70, 71, 7)); DISTS = (450, 850, 1250)
S = {"t0": None, "last": -1, "L": [], "h": None, "done": False, "dist": 0.0, "prev": None, "falls": 0, "off": 0, "n": 0, "start": None, "maxv": 0.0, "fall_t": -9}
def fin():
    S["done"] = True
    unreal.unregister_slate_post_tick_callback(S["h"])
    S["L"].append("SUMMARY dist %.0f m  falls %d  stuck %d  frames off-road %d/%d  max %.1f km/h" % (S["dist"] / 100, S["falls"], S.get("stuck", 0), S["off"], S["n"], S["maxv"]))
    open(OUT, "w").write("\n".join(S["L"]))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
def trace(w, a, b, ignore):
    r = unreal.SystemLibrary.line_trace_single(w, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore, unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[0] if isinstance(r[0], unreal.HitResult) else r[-1]
    if r is None: return None
    t = r.to_tuple()
    return t[4] if t[0] else None   # impact point (blocking hit)
def tick(dt):
    if S["done"]: return
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not w: return
        cars = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
        if not cars: return
        a = cars[0]; mv = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
        if S["t0"] is None:
            # start on the road nearest the level's Player Start, pointed along it
            ps = a.get_actor_location(); best = None
            tt = [x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.StaticMeshActor) if x.get_actor_label() in ("TestTrack", "Track")]
            o, e = (tt[0].get_actor_bounds(False) if tt else (ps, unreal.Vector(5000, 5000, 2000)))
            for ix in range(int((o.x - e.x) // 300), int((o.x + e.x) // 300) + 1):
                for iy in range(int((o.y - e.y) // 300), int((o.y + e.y) // 300) + 1):
                    x, y = ix * 300.0, iy * 300.0
                    h = trace(w, unreal.Vector(x, y, o.z + e.z + 500), unreal.Vector(x, y, o.z - e.z - 500), [a])
                    if h is not None:
                        d = math.hypot(x - ps.x, y - ps.y)
                        if best is None or d < best[0]: best = (d, h)
            h = best[1]; runs = []
            for k in range(36):
                r = math.radians(k * 10); n_ = 0
                for s_ in range(1, 9):
                    q = trace(w, unreal.Vector(h.x + math.cos(r) * s_ * 250, h.y + math.sin(r) * s_ * 250, h.z + 600), unreal.Vector(h.x + math.cos(r) * s_ * 250, h.y + math.sin(r) * s_ * 250, h.z - 600), [a])
                    if q is None: break
                    n_ += 1
                runs.append((n_, k * 10))
            yaw0 = max(runs)[1]
            S["start"] = (unreal.Vector(h.x, h.y, h.z + 120), unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(yaw0)))
            a.set_actor_location_and_rotation(S["start"][0], S["start"][1], False, True)
            a.get_component_by_class(unreal.SkeletalMeshComponent).set_physics_linear_velocity(unreal.Vector(0, 0, 0))
            S["L"].append("start on road at (%.0f,%.0f,%.0f) yaw %d (player start was %.0f,%.0f,%.0f)" % (h.x, h.y, h.z, yaw0, ps.x, ps.y, ps.z))
            if globals().get("BOOST0") is not None: a.set_editor_property("BoostAmount", float(BOOST0))
            S["t0"] = time.time(); return
        t = time.time() - S["t0"]
        p = a.get_actor_location(); yaw = math.radians(a.get_actor_rotation().yaw)
        if S["prev"] is not None: S["dist"] += math.hypot(p.x - S["prev"].x, p.y - S["prev"].y)
        S["prev"] = p
        kmh = mv.get_forward_speed() * 0.036; S["maxv"] = max(S["maxv"], kmh)
        below = trace(w, unreal.Vector(p.x, p.y, p.z + 50), unreal.Vector(p.x, p.y, p.z - 400), [a])
        S["n"] += 1
        if below is None: S["off"] += 1
        if below is None and p.z < S["start"][0].z - 2500 and t - S["fall_t"] > 2:   # fell off: count it and put the car back at the start
            S["falls"] += 1; S["fall_t"] = t; S["L"].append("t%5.1f FELL at (%.0f,%.0f)" % (t, p.x, p.y))
            a.set_actor_location_and_rotation(S["start"][0], S["start"][1], False, True); S["prev"] = None
            a.get_component_by_class(unreal.SkeletalMeshComponent).set_physics_linear_velocity(unreal.Vector(0, 0, 0))
            return
        ok = []
        for ang in ANGLES:
            r = yaw + math.radians(ang); good = True
            for d in DISTS:
                x, y = p.x + math.cos(r) * d, p.y + math.sin(r) * d
                hit = trace(w, unreal.Vector(x, y, p.z + 700), unreal.Vector(x, y, p.z - 900), [a])
                if hit is None or abs(hit.z - p.z) > 300 + d * 0.9: good = False; break   # allow steep climbs/drops
            ok.append(good)
        runs, cur = [], []
        for ang, g_ in zip(ANGLES, ok):
            if g_: cur.append(ang)
            elif cur: runs.append(cur); cur = []
        if cur: runs.append(cur)
        if runs:
            best = max(runs, key=lambda r_: (len(r_), -abs(sum(r_) / len(r_))))
            target = sum(best) / len(best); width = len(best) * 7
            steer = max(-1.0, min(1.0, target / 30.0))
            thr = _top if width > 40 else (0.5 * _top if width > 20 else 0.25)
            # brake for corners like a player would: the sharper the turn ahead, the lower the target speed
            want = 70 if abs(target) < 8 else (50 if abs(target) < 18 else (38 if abs(target) < 30 else 28))
            brk = 0.0
            if kmh > want + 4: thr, brk = 0.0, min(1.0, (kmh - want) / 15.0)
        else:
            steer, thr, width, target, brk = 0.0, 0.0, 0, 0, 0.6
        if not runs: brk = 0.6
        mv.set_throttle_input(thr); mv.set_brake_input(brk); mv.set_steering_input(steer)
        # stuck (wedged on the edge): count it and put the car back a little way along the road it last drove
        if abs(kmh) < 2 and thr > 0: S["stuck_t"] = S.get("stuck_t", 0) + dt
        else: S["stuck_t"] = 0
        if S["stuck_t"] > 3:
            S["stuck"] = S.get("stuck", 0) + 1; S["stuck_t"] = 0; S["L"].append("t%5.1f STUCK at (%.0f,%.0f)" % (t, p.x, p.y))
            lg = S.get("good")
            if lg: a.set_actor_location_and_rotation(lg[0], lg[1], False, True); a.get_component_by_class(unreal.SkeletalMeshComponent).set_physics_linear_velocity(unreal.Vector(0, 0, 0))
        if runs and width > 40 and abs(kmh) > 15 and t - S.get("good_t", -9) > 1.5:
            S["good"] = (unreal.Vector(p.x, p.y, p.z + 60), unreal.Rotator(roll=0.0, pitch=0.0, yaw=a.get_actor_rotation().yaw)); S["good_t"] = t
        if _drift: a.set_editor_property("SteerAxis", steer)
        if _drift: a.set_editor_property("DriftHeld", abs(steer) > 0.4 and kmh > 35)
        if t - S["last"] >= 0.5:
            S["last"] = t
            S["L"].append("t%5.1f spd %5.1f gear %d pos (%6.0f,%6.0f,%5.0f) road %s width %3d target %5.1f steer %5.2f thr %.2f drift %d dtime %.2f boost %.2f" % (
                t, kmh, mv.get_current_gear(), p.x, p.y, p.z, below is not None, width, target, steer, thr, a.get_editor_property("Drifting"), a.get_editor_property("DriftTime"), a.get_editor_property("BoostAmount")))
        if t > _dur: fin()
    except Exception:
        S["L"].append(traceback.format_exc()); fin()
if _map: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(_map)
S["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
