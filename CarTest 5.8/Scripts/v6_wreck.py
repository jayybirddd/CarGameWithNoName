# v6/v7: BP_CarWreck - spawned where the car was when it runs out of lives: a quick fireball + flash, and the car's
# pieces flying apart with physics. Each piece slot (Body, WheelFL/FR/RL/RR, Antenna) is an invisible physics box
# carrying a copy of the separated car model (CAR_separated) with every bone hidden except that piece's own.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gplace as gp; importlib.reload(gp)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_wreck.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
gp.LOG = log
EAL, BEL = gp.EAL, gp.BEL
PH = "/Game/Car/Placeholders"
FIREBALL_TIME, FLASH_TIME = 0.4, 0.7
try:
    sk = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    b = sk.get_bounds(); o, e = b.origin, b.box_extent
    log("car bounds", o, e)
    mi_path = PH + "/MI_Placeholder_Wreck"
    mi = unreal.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else gp.AT.create_asset("MI_Placeholder_Wreck", PH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(mi, unreal.load_asset(PH + "/M_Placeholder"))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(0.12, 0.12, 0.13, 1))
    EAL.save_asset(mi_path, only_if_is_dirty=False)
    wp = PH + "/BP_CarWreck"
    wr = gp.new_bp("BP_CarWreck", PH)
    gp.add_vars(wr, [("Age", gp.T("real"))], "", editable=False)
    # pieces: (slot, box centre, box half-size, bones shown) in car space (X forward, Y right). Box centres come from
    # the separated car's bone positions; the boxes don't overlap so the pieces don't shove each other apart on spawn.
    PIECES = [("Body", unreal.Vector(9, 0, 78), unreal.Vector(140, 68, 26), ["DEF-BODY"]),
              ("Antenna", unreal.Vector(-115, -59, 117), unreal.Vector(4, 4, 9), ["DEF-BASE-ANTENNAE", "DEF-ANTENAE0-001", "DEF-ANTENAE0-002", "DEF-ANTENAE0-003", "DEF-ANTENAE0-004"]),
              ("WheelFL", unreal.Vector(98, -59, 23), unreal.Vector(23, 11, 23), ["DEF-FRONT-WHEEL_L"]),
              ("WheelFR", unreal.Vector(98, 59, 23), unreal.Vector(23, 11, 23), ["DEF-FRONT-WHEEL_R"]),
              ("WheelRL", unreal.Vector(-70, -59, 23), unreal.Vector(23, 11, 23), ["DEF-BACK-WHEEL_L"]),
              ("WheelRR", unreal.Vector(-70, 59, 23), unreal.Vector(23, 11, 23), ["DEF-BACK-WHEEL_R"])]
    ALL_BONES = [b_ for p_ in PIECES for b_ in p_[3]]
    SEP = unreal.load_asset("/Game/Car/SeparatedCar/CAR_separated")
    SEP_YAW = -90.0   # the separated model faces +Y; turn it to face +X like the driving car
    # replace the old placeholder shape slots (static meshes) with box slots
    have = gp.comps(wr)
    root_h = [h for h in gp.SDS.k2_gather_subobject_data_for_blueprint(wr)][0]
    for nm, *_r in PIECES:
        if nm in have and not isinstance(have[nm][1], unreal.BoxComponent):
            log("remove old slot", nm, gp.SDS.delete_subobject(root_h, have[nm][0], wr))
    for nm, centre, half, bones in PIECES:
        bx = gp.add_comp(wr, unreal.BoxComponent, nm)
        bx.set_editor_property("box_extent", half); bx.set_editor_property("relative_location", centre)
        bx.set_collision_profile_name("PhysicsActor"); bx.set_editor_property("hidden_in_game", True)
        sk = gp.add_comp(wr, unreal.SkeletalMeshComponent, nm + "Mesh", nm)
        sk.set_editor_property("skeletal_mesh_asset", SEP) if hasattr(sk, "skeletal_mesh_asset") else sk.set_editor_property("skeletal_mesh", SEP)
        # undo the box offset so the model's origin sits on the actor origin, as on the driving car
        sk.set_editor_property("relative_location", unreal.Vector(-centre.x, -centre.y, -centre.z))
        sk.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=SEP_YAW))
        sk.set_collision_profile_name("NoCollision")
    fire = gp.shape_comp(wr, "Fireball", "/Engine/BasicShapes/Sphere", unreal.load_asset("/Game/Car/FX/M_BoostFlame"), unreal.Vector(o.x, o.y, o.z), unreal.Vector(0.5, 0.5, 0.5))
    fire.set_editor_property("cast_shadow", False)
    lt = gp.add_comp(wr, unreal.PointLightComponent, "Flash")
    lt.set_editor_property("relative_location", unreal.Vector(o.x, o.y, o.z + 80)); lt.set_editor_property("intensity", 80000.0)
    lt.set_editor_property("light_color", unreal.Color(r=255, g=140, b=40, a=255)); lt.set_editor_property("attenuation_radius", 2500.0)
    BEL.compile_blueprint(wr)
    ed, g, n = gp.graph(wr)
    # BeginPlay: pieces start moving with the car, then get kicked up and outward with a random spin
    bp_ev = ed.find_event_node("ReceiveBeginPlay")
    pp = n("Game|GetPlayerPawn", 0, 300)
    vel = n(["Utilities|Transformation|GetVelocity", "Transformation|GetVelocity", "Physics|GetVelocity"], 200, 300); g.link(pp, "ReturnValue", vel, "self")
    prev, pin = bp_ev, "then"
    # each copy of the model shows only its own piece
    for i, (nm, _c, _h, bones) in enumerate(PIECES):
        for j, bn in enumerate([b_ for b_ in ALL_BONES if b_ not in bones]):
            hb = n(["Components|SkinnedMesh|HideBonebyName", "Components|SkinnedMesh|HideBoneByName", "Mesh|HideBonebyName", "Components|SkeletalMesh|HideBonebyName", "Rendering|Components|SkinnedMesh|HideBonebyName"], 400 + j * 220, -1200 - i * 400, unreal.SkinnedMeshComponent)
            g.exe(prev, pin, hb); g.link(g.var_get(nm + "Mesh", 300 + j * 220, -1000 - i * 400), nm + "Mesh", hb, "self"); g.val(hb, "BoneName", bn); g.val(hb, "PhysBodyOption", "PBO_None")
            if i == 0 and j == 0: g.dump(hb)
            prev, pin = hb, "then"
    for i, (nm, *_rest) in enumerate(PIECES):
        x0 = 400 + i * 1100
        comp = g.var_get(nm, x0, 250)
        ss = n("Physics|SetSimulatePhysics", x0, 0); g.exe(prev, pin, ss); g.link(comp, nm, ss, "self"); g.val(ss, "bSimulate", "true")
        sv = n(["Physics|SetPhysicsLinearVelocity", "Physics|SetPhysicsLinearVelocity(Component)"], x0 + 250, 0); g.exe(ss, "then", sv); g.link(comp, nm, sv, "self"); g.link(vel, "ReturnValue", sv, "NewVel")
        rr = [n("Math|Random|RandomFloatinRange", x0 + 300, 350 + k * 100) for k in range(6)]
        for r_, lo, hi in zip(rr, (-350, -350, 450, -400, -400, -400), (350, 350, 900, 400, 400, 400)):
            g.val(r_, "Min", str(lo)); g.val(r_, "Max", str(hi))
        iv = n("Math|Vector|MakeVector", x0 + 500, 350); [g.link(rr[k], "ReturnValue", iv, a) for k, a in enumerate("XYZ")]
        av = n("Math|Vector|MakeVector", x0 + 500, 550); [g.link(rr[k + 3], "ReturnValue", av, a) for k, a in enumerate("XYZ")]
        ai = n("Physics|AddImpulse", x0 + 500, 0); g.exe(sv, "then", ai); g.link(comp, nm, ai, "self"); g.link(iv, "ReturnValue", ai, "Impulse"); g.val(ai, "bVelChange", "true")
        aa = n(["Physics|AddAngularImpulseinDegrees", "Physics|AddAngularImpulseInDegrees"], x0 + 750, 0); g.exe(ai, "then", aa); g.link(comp, nm, aa, "self"); g.link(av, "ReturnValue", aa, "Impulse"); g.val(aa, "bVelChange", "true")
        prev, pin = aa, "then"
    # Tick: fireball grows and vanishes, flash fades
    tk = ed.find_event_node("ReceiveTick")
    ag = g.var_get("Age", 0, 1600)
    ad = n("Utilities|Operators|Add", 200, 1600); g.link(ag, "Age", ad, "A"); g.link(tk, "DeltaSeconds", ad, "B")
    sa = g.var_set("Age", 400, 1300); g.exe(tk, "then", sa); g.link(ad, "ReturnValue", sa, "Age")
    A = (sa, "Output_Get")
    sc = n("Utilities|Operators|Multiply", 600, 1600); g.link(*A, sc, "A"); g.val(sc, "B", "14.0")
    sc2 = n("Utilities|Operators|Add", 750, 1600); g.link(sc, "ReturnValue", sc2, "A"); g.val(sc2, "B", "0.5")
    sv3 = n("Math|Vector|MakeVector", 900, 1600); [g.link(sc2, "ReturnValue", sv3, a) for a in "XYZ"]
    srs = n("Transformation|SetRelativeScale3D", 700, 1300); g.exe(sa, "then", srs); g.link(g.var_get("Fireball", 550, 1450), "Fireball", srs, "self"); g.link(sv3, "ReturnValue", srs, "NewScale3D")
    lt_ = n("Utilities|Operators|Less(<)", 1000, 1700); g.link(*A, lt_, "A"); g.val(lt_, "B", str(FIREBALL_TIME))
    vis = n("Rendering|SetVisibility", 1000, 1300); g.exe(srs, "then", vis); g.link(g.var_get("Fireball", 850, 1450), "Fireball", vis, "self"); g.link(lt_, "ReturnValue", vis, "bNewVisibility")
    li = n(["Math|Float|MapRangeClamped", "Math|Float|MapRangeClamped(Float)"], 1400, 1700); g.link(*A, li, "Value")
    g.val(li, "InRangeA", "0.0"); g.val(li, "InRangeB", str(FLASH_TIME)); g.val(li, "OutRangeA", "80000.0"); g.val(li, "OutRangeB", "0.0")
    si = n(["Rendering|Lighting|SetIntensity", "Rendering|Components|Light|SetIntensity"], 1300, 1300); g.exe(vis, "then", si)
    g.link(g.var_get("Flash", 1150, 1450), "Flash", si, "self"); g.link(li, "ReturnValue", si, "NewIntensity")
    g.dump(vis)
    gp.finish(wr, ed, wp)
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V6_WRECK_DONE")
