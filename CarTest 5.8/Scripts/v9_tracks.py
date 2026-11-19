# v9: race levels L_Track1-3, one per track mesh. Each is a copy of TEST_TrackPrototype (sky + lights) with the
# track mesh swapped in at a scale that gives every road the same width relative to the car as TestTrack in
# TEST_EarthTestTrack (about 24.8 m). The road centreline is traced to place a START / FINISH gate on the straightest
# stretch, checkpoint gates at equal distances around the lap, the player start behind the line, and a BP_RaceManager.
# Re-runnable: clears what it placed (Gate_*, RaceManager, LevelRules) and builds it again. Set ONLY to e.g. [2] to
# rebuild one level.
import unreal, traceback, sys, importlib, math, os, time
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gtrack; importlib.reload(gtrack)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v9_tracks.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = "/Game/Car/Placeholders/"
PROTO = "/Game/Levels/Testing/TEST_TrackPrototype"
# (level, track mesh, scale) - scales measured by v9_width.py: road widths 8.2 / 20.4 / 40.8 m at scale 1
TRACKS = [(1, "/Game/Environment/Track/TestTrack", 3.01), (2, "/Game/Environment/Track/NewBigTrack_Flat", 1.22), (3, "/Game/Environment/Track/TestTrack_2", 0.61)]
ONLY = globals().get("ONLY")
GATE_SPACING = 12000.0     # cm of lap between gates (clamped to 6..14 gates)
LAPS = 3
try:
    for idx, mesh, scale in TRACKS:
        if ONLY and idx not in ONLY: continue
        t0 = time.time()
        path = "/Game/Levels/L_Track%d" % idx
        if not os.path.exists("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Content/Levels/L_Track%d.umap" % idx):
            log("== create", path, LES.load_level(PROTO), unreal.EditorLoadingAndSavingUtils.save_map(UES.get_editor_world(), path))
        log("== load", path, LES.load_level(path))
        w = UES.get_editor_world()
        acts = EAS.get_all_level_actors()
        for a in acts:
            lb = a.get_actor_label()
            if lb.startswith("Gate_") or lb in ("RaceManager", "LevelRules") or a.get_class().get_name() in ("BP_FinishLine_C", "BP_BoostPad_C", "BP_LandMine_C"):
                EAS.destroy_actor(a)
        tracks = [a for a in EAS.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.get_editor_property("static_mesh")
                  and "rack" in a.static_mesh_component.get_editor_property("static_mesh").get_name()]
        trk = tracks[0]
        for extra in tracks[1:]: EAS.destroy_actor(extra)
        trk.static_mesh_component.set_static_mesh(unreal.load_asset(mesh))
        trk.set_actor_location_and_rotation(unreal.Vector(0, 0, 0), unreal.Rotator(), False, True)
        trk.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        trk.set_actor_label("Track")
        ws = w.get_world_settings(); ws.set_editor_property("default_game_mode", unreal.load_asset("/Game/Car/Blueprints/BP_CarGameMode").generated_class())
        # trace the lap
        p, hx, hy, med = gtrack.find_start(w, trk, log=log)
        pts, length, closed = gtrack.walk(w, trk, p, hx, hy, log=log)
        log("lap %.0f m, %d samples, %s, road width median %.0f cm" % (length / 100, len(pts), "closed" if closed else "NOT CLOSED", sorted(q[5] for q in pts)[len(pts) // 2]))
        # start on the straightest stretch: smallest heading change over +-6 samples
        def turn(i):
            a0 = math.atan2(pts[(i - 6) % len(pts)][4], pts[(i - 6) % len(pts)][3]); a1 = math.atan2(pts[(i + 6) % len(pts)][4], pts[(i + 6) % len(pts)][3])
            d = abs((a1 - a0 + math.pi) % (2 * math.pi) - math.pi); return d
        # ...that is also flat and has no road passing overhead (crossings), so the start grid is easy to read
        def slope(i):
            a, b = pts[(i - 6) % len(pts)], pts[(i + 6) % len(pts)]
            return abs(b[2] - a[2]) / max(1.0, math.hypot(b[0] - a[0], b[1] - a[1]))
        def covered(i):
            x, y, z = pts[i][0], pts[i][1], pts[i][2]
            r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, z + 6000), unreal.Vector(x, y, z + 150), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            if isinstance(r, tuple): r = r[0] if isinstance(r[0], unreal.HitResult) else r[-1]
            return bool(r and r.to_tuple()[0])
        ranked = sorted(range(len(pts)), key=lambda i: turn(i) + 3.0 * slope(i)) if closed else [8]
        s0 = next((i for i in ranked[:80] if not covered(i) and not covered((i - 5) % len(pts))), ranked[0])
        log("start index %d: turn %.2f rad, slope %.2f" % (s0, turn(s0), slope(s0)))
        pts = pts[s0:] + pts[:s0] if closed else pts
        n_g = max(6, min(14, int(round(length / GATE_SPACING))))
        cum = [0.0]
        for i in range(1, len(pts)): cum.append(cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        gate_cls = unreal.load_asset(P + "BP_RaceGate").generated_class()
        finish_mi = unreal.load_asset(P + "MI_Placeholder_Finish")
        for k in range(n_g):
            target = cum[-1] * k / n_g
            i = min(range(len(pts)), key=lambda j: abs(cum[j] - target))
            x, y, z, gx, gy, wd = pts[i]
            yaw = math.degrees(math.atan2(gy, gx))
            g = EAS.spawn_actor_from_class(gate_cls, unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
            g.set_actor_label("Gate_%02d" % k)
            g.set_editor_property("GateIndex", k)
            half = wd / 2.0 + 200.0
            for c in g.get_components_by_class(unreal.PrimitiveComponent):
                nm = c.get_name()
                if nm.startswith("PostL"): c.set_editor_property("relative_location", unreal.Vector(0, -half, 300))
                elif nm.startswith("PostR"): c.set_editor_property("relative_location", unreal.Vector(0, half, 300))
                elif nm.startswith("Banner"): c.set_editor_property("relative_scale3d", unreal.Vector(0.3, half * 2 / 100.0 + 0.5, 1.0))
                elif nm.startswith("Trigger"): c.set_box_extent(unreal.Vector(150, half, 600), True)
                if k == 0 and nm.startswith(("PostL", "PostR", "Banner")): c.set_material(0, finish_mi)
            for t in g.get_components_by_class(unreal.TextRenderComponent):
                t.set_text(unreal.Text("START / FINISH" if k == 0 else "GATE %d" % k))
        # player start 20 m behind the line, on the road
        back = min(range(len(pts)), key=lambda j: abs((cum[j] - (cum[-1] - 2000.0)) if closed else cum[j]))
        bx, by, bz, bhx, bhy, _w = pts[back] if closed else pts[0]
        ps = [a for a in EAS.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"]
        ps = ps[0] if ps else EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(), unreal.Rotator())
        sx, sy, sz, shx, shy, _w = pts[0]
        ps.set_actor_location_and_rotation(unreal.Vector(bx, by, bz + 120), unreal.Rotator(roll=0.0, pitch=0.0, yaw=math.degrees(math.atan2(shy, shx))), False, True)
        o, e = trk.get_actor_bounds(False)
        mgr = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_RaceManager").generated_class(), unreal.Vector(sx, sy, sz + 900), unreal.Rotator())
        mgr.set_actor_label("RaceManager")
        mgr.set_editor_property("NumGates", n_g); mgr.set_editor_property("Laps", LAPS); mgr.set_editor_property("FallZ", o.z - e.z - 3000.0)
        rules = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_LevelRules").generated_class(), unreal.Vector(sx, sy, sz + 1100), unreal.Rotator())
        rules.set_actor_label("LevelRules")
        for kk, v in {"BoostRegenEnabled": True, "PadsChargeMeter": False, "StartingLives": 3, "StartingBoost": 1.0}.items(): rules.set_editor_property(kk, v)
        rules.set_editor_property("NextLevel", unreal.Name("L_Track%d" % (idx + 1) if idx < 3 else "None"))
        log("placed %d gates, start (%.0f,%.0f,%.0f) yaw %.0f, FallZ %.0f" % (n_g, bx, by, bz, math.degrees(math.atan2(shy, shx)), o.z - e.z - 3000.0), "took %.0fs" % (time.time() - t0))
        log("saved", LES.save_current_level())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V9_TRACKS_DONE")
