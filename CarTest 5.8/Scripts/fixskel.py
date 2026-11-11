import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_fixskel.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
ML = unreal.MathLibrary
EAL = unreal.EditorAssetLibrary
def tstr(t):
    r = t.rotation.rotator()
    return "loc(%.2f,%.2f,%.2f) rot(p%.1f,y%.1f,r%.1f) s(%.2f)" % (t.translation.x, t.translation.y, t.translation.z, r.pitch, r.yaw, r.roll, t.scale3d.x)
try:
    mesh = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(mesh)
    bones = [str(b) for b in mod.get_all_bone_names()]
    parent = {b: str(mod.get_parent_name(b)) for b in bones}
    G = {b: mod.get_bone_transform(b, True) for b in bones}
    SCALE = G["CAR"].scale3d.x
    log("root scale", SCALE, "root", tstr(G["CAR"]))
    NG = {}
    for b in bones:
        t = G[b]
        rot = unreal.Quat() if b == "CAR" else t.rotation
        NG[b] = unreal.Transform(t.translation, rot.rotator(), unreal.Vector(1, 1, 1))
    NL = {}
    for b in bones:
        p = parent[b]
        NL[b] = NG[b] if p in ("None", "") else ML.make_relative_transform(NG[b], NG[p])
    # parents first
    order = []
    def visit(b):
        order.append(b)
        for c in bones:
            if parent[c] == b: visit(c)
    for b in bones:
        if parent[b] in ("None", ""): visit(b)
    for b in order:
        ok = mod.set_bone_transform(b, NL[b], True)
        if not ok: log("set failed", b)
    # verify
    bad = 0
    for b in bones:
        g2 = mod.get_bone_transform(b, True)
        d = (g2.translation - G[b].translation).length()
        if d > 0.05 or abs(g2.scale3d.x - 1) > 0.001:
            bad += 1; log("mismatch", b, tstr(G[b]), "->", tstr(g2))
    log("verify mismatches", bad)
    if bad == 0:
        log("commit", mod.commit_skeleton_to_skeletal_mesh())
        EAL.save_asset("/Game/Car/Mesh/SK_Car")
        EAL.save_asset("/Game/Car/Mesh/SK_Car_Skeleton")
        ref = unreal.AnimPoseExtensions.get_reference_pose(mesh.skeleton)
        for b in ["CAR", "ROOT", "MASTER-ROTATION", "DEF-BODY", "DEF-FRONT-WHEEL_L", "DEF-BACK-WHEEL_R"]:
            log("new ref", b, tstr(unreal.AnimPoseExtensions.get_bone_pose(ref, b, unreal.AnimPoseSpaces.WORLD)), "local", tstr(unreal.AnimPoseExtensions.get_bone_pose(ref, b, unreal.AnimPoseSpaces.LOCAL)))
        bb = mesh.get_bounds(); log("bounds", bb.origin, bb.box_extent)
        # rescale translation keys of the body animations
        reg = unreal.AssetRegistryHelpers.get_asset_registry()
        for ad in reg.get_assets_by_path("/Game/Car/Animations", recursive=False):
            if str(ad.asset_class_path.asset_name) != "AnimSequence": continue
            a = unreal.load_asset(str(ad.package_name))
            model = a.get_editor_property("data_model") if False else None
            ctrl = a.get_editor_property("controller")
            dm = ctrl.get_model() if hasattr(ctrl, "get_model") else a.get_data_model() if hasattr(a, "get_data_model") else None
            if dm is None:
                log("no model", ad.asset_name); continue
            ctrl.open_bracket(unreal.Text("rescale"), False)
            n = 0
            for tn in dm.get_bone_track_names():
                tr = dm.get_bone_track_by_name(tn)
                raw = tr.get_editor_property("internal_track_data")
                pos = [unreal.Vector(p.x * SCALE, p.y * SCALE, p.z * SCALE) for p in raw.get_editor_property("pos_keys")]
                rot = [unreal.Quat(q.x, q.y, q.z, q.w) for q in raw.get_editor_property("rot_keys")]
                scl = [unreal.Vector(s.x, s.y, s.z) for s in raw.get_editor_property("scale_keys")]
                if len(pos) == 0: continue
                if len(pos) != len(rot) or len(pos) != len(scl):
                    m = max(len(pos), len(rot), len(scl))
                    pos = pos + [pos[-1]] * (m - len(pos)); rot = rot + [rot[-1]] * (m - len(rot)); scl = scl + [scl[-1]] * (m - len(scl))
                ok = ctrl.set_bone_track_keys(tn, pos, rot, scl, False)
                if ok: n += 1
                else: log("key set failed", ad.asset_name, tn)
            ctrl.close_bracket(False)
            EAL.save_asset(str(ad.package_name))
            log("rescaled", ad.asset_name, n, "tracks")
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_FIXSKEL_DONE")
