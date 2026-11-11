# v3: placeholder level objects (boost pad, land mine, level rules) + the car variables they use.
# Placeholders are basic engine shapes with their name written on them; swap the meshes later.
# Re-runnable: rebuilds the three Blueprints' graphs and keeps existing components/variables.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v3_assets.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
CAR = "/Game/Car/Blueprints/BP_CarPawn"
CARC = "/Game/Car/Blueprints/BP_CarPawn.BP_CarPawn_C"
VEH = "/Script/ChaosVehicles.WheeledVehiclePawn"
DIR = "/Game/Car/Placeholders"
R, Bo, I = BEL.get_basic_type_by_name("real"), BEL.get_basic_type_by_name("bool"), BEL.get_basic_type_by_name("int")

def add_vars(bp, spec, category, editable=True):
    have = [str(x) for x in BEL.list_member_variable_names(bp)]
    for nm, tp in spec:
        if nm not in have: BEL.add_member_variable(bp, nm, tp)
        if editable:
            BEL.set_blueprint_variable_instance_editable(bp, nm, True)
            BEL.set_blueprint_variable_category(bp, nm, category)
    BEL.compile_blueprint(bp)

def set_defaults(bp, d):
    cdo = unreal.get_default_object(bp.generated_class())
    for k, v in d.items():
        try: cdo.set_editor_property(k, v)
        except Exception as e: log("!! default", bp.get_name(), k, e)

def comps(bp):
    out = {}
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        d = SDS.k2_find_subobject_data_from_handle(h)
        out[str(SDL.get_variable_name(d))] = (h, SDL.get_object(d))
    return out

def add_comp(bp, cls, name, parent_name="DefaultSceneRoot"):
    c = comps(bp)
    if name in c: return c[name][1]
    prm = unreal.AddNewSubobjectParams(parent_handle=c[parent_name][0], new_class=cls, blueprint_context=bp)
    h, fail = SDS.add_new_subobject(prm)
    SDS.rename_subobject_member_variable(bp, h, name)
    return comps(bp)[name][1]

def text_comp(bp, name, text, loc, rot, size, color):
    t = add_comp(bp, unreal.TextRenderComponent, name)
    try: t.set_editor_property("text", text)
    except Exception: t.set_editor_property("text", unreal.Text(text))
    t.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    t.set_editor_property("vertical_alignment", unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    t.set_editor_property("world_size", size)
    t.set_editor_property("text_render_color", color)
    t.set_editor_property("relative_location", loc); t.set_editor_property("relative_rotation", rot)
    t.set_collision_profile_name("NoCollision")
    return t

def shape_comp(bp, name, mesh, mat, loc, scale):
    m = add_comp(bp, unreal.StaticMeshComponent, name)
    m.set_editor_property("static_mesh", unreal.load_asset(mesh))
    m.set_editor_property("override_materials", [mat])
    m.set_editor_property("relative_location", loc); m.set_editor_property("relative_scale3d", scale)
    m.set_collision_profile_name("NoCollision"); m.set_editor_property("generate_overlap_events", False)
    return m

def trigger_only(c):
    # overlap the car and nothing else: with a stock profile the wheel traces can treat the trigger's top as ground
    c.set_collision_profile_name("Custom")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
    c.set_collision_object_type(unreal.CollisionChannel.ECC_WORLD_DYNAMIC)
    c.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
    for ch in (unreal.CollisionChannel.ECC_PAWN, unreal.CollisionChannel.ECC_VEHICLE):
        c.set_collision_response_to_channel(ch, unreal.CollisionResponseType.ECR_OVERLAP)
    c.set_editor_property("generate_overlap_events", True)
    log("trigger", c.get_name(), c.get_collision_profile_name(), [str(c.get_collision_response_to_channel(ch)).split(".")[-1] for ch in
        (unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionChannel.ECC_WORLD_DYNAMIC, unreal.CollisionChannel.ECC_PAWN, unreal.CollisionChannel.ECC_VEHICLE)])

def new_bp(name, parent=unreal.Actor):
    path = DIR + "/" + name
    if EAL.does_asset_exist(path): return unreal.load_asset(path)
    f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", parent)
    return AT.create_asset(name, DIR, unreal.Blueprint, f)

def placeholder_mi(name, color):
    path = DIR + "/" + name
    mi = unreal.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, unreal.load_asset(DIR + "/M_Placeholder"))
    MEL.set_material_instance_vector_parameter_value(mi, "Color", color)
    EAL.save_asset(path, only_if_is_dirty=False)
    return mi

def graph(bp):
    ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(bp))
    keep = ("Event BeginPlay", "Event ActorBeginOverlap", "Event Tick")
    ed.remove_nodes([nd for nd in ed.list_all_nodes() if str(BEL.get_node_title(nd)).splitlines()[0] not in keep])
    g = gh.G(ed, log)
    def n(names, x, y, cls=None):
        if isinstance(names, str): names = [names]
        for nm in names:
            nd = ed.create_node_from_name(nm, unreal.Vector2D(x, y), [], cls) if cls else ed.create_node_from_name(nm, unreal.Vector2D(x, y), [])
            if nd is not None: return nd
        log("!! node failed", names); return None
    return ed, g, n

def car_cast(ed, g, n, ev):
    cast = n("Utilities|Casting|CastToBP_CarPawn", 300, 0)
    g.exe(ev, "then", cast); g.link(ev, "OtherActor", cast, "Object")
    co = [str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)) for p in g.pins(cast) if str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)).startswith("As")][0]
    def get(name, x, y, owner=CARC):
        nd = ed.add_get_member_variable_node(name, owner)
        if nd is None: log("!! car get", name); return None
        nd.set_node_pos(unreal.IntPoint(x, y)); g.link(cast, co, nd, "self"); return nd
    def put(name, x, y, owner=CARC):
        nd = ed.add_set_member_variable_node(name, owner)
        if nd is None: log("!! car set", name); return None
        nd.set_node_pos(unreal.IntPoint(x, y)); g.link(cast, co, nd, "self"); return nd
    return cast, get, put

def finish(bp, ed, path):
    BEL.compile_blueprint(bp)
    for nd in ed.list_nodes_with_errors(): log("ERROR", bp.get_name(), BEL.get_node_title(nd))
    for nd in ed.list_nodes_with_warnings(): log("WARN", bp.get_name(), BEL.get_node_title(nd))
    log("saved", path, EAL.save_asset(path, only_if_is_dirty=False))

try:
    # ---------------- car variables used by pads / mines / rules
    car = unreal.load_asset(CAR)
    add_vars(car, [("Lives", I), ("MaxLives", I), ("PadAccel", R), ("PadsChargeMeter", Bo)], "Car Tuning")
    add_vars(car, [("HitCooldown", R), ("PadBoostTimer", R), ("OutOfLives", Bo)], "", editable=False)
    set_defaults(car, {"Lives": 3, "MaxLives": 3, "PadAccel": 900.0, "PadsChargeMeter": False})
    mesh = comps(car)["Mesh"][1]
    log("car mesh overlap events was", mesh.get_editor_property("generate_overlap_events"))
    mesh.set_editor_property("generate_overlap_events", True)
    BEL.compile_blueprint(car); log("saved car", EAL.save_asset(CAR, only_if_is_dirty=False))

    # ---------------- placeholder material: flat colour, a little self-lit so it reads in any lighting
    if not EAL.does_asset_exist(DIR): EAL.make_directory(DIR)
    mp = DIR + "/M_Placeholder"
    m = unreal.load_asset(mp) if EAL.does_asset_exist(mp) else AT.create_asset("M_Placeholder", DIR, unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(m)
    col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, 0)
    col.set_editor_property("parameter_name", "Color"); col.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1))
    k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 200); k.set_editor_property("r", 0.35)
    em = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 150)
    MEL.connect_material_expressions(col, "", em, "A"); MEL.connect_material_expressions(k, "", em, "B")
    MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_asset(mp, only_if_is_dirty=False)
    mi_pad = placeholder_mi("MI_Placeholder_BoostPad", unreal.LinearColor(0.0, 0.75, 1.0, 1))
    mi_mine = placeholder_mi("MI_Placeholder_Mine", unreal.LinearColor(0.9, 0.05, 0.03, 1))
    mi_rules = placeholder_mi("MI_Placeholder_Rules", unreal.LinearColor(0.6, 0.2, 0.9, 1))
    WHITE = unreal.Color(r=255, g=255, b=255, a=255)
    FLAT = unreal.Rotator(roll=0.0, pitch=90.0, yaw=180.0)   # lying on top, readable from a car coming from -X
    FACE = unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0)    # upright sign facing -X

    # ---------------- level rules: one per level; the car copies these at BeginPlay (no actor = defaults)
    rp = DIR + "/BP_LevelRules"
    rules = new_bp("BP_LevelRules")
    add_vars(rules, [("BoostRegenEnabled", Bo), ("PadsChargeMeter", Bo), ("StartingLives", I), ("StartingBoost", R)], "Level Rules")
    set_defaults(rules, {"BoostRegenEnabled": True, "PadsChargeMeter": False, "StartingLives": 3, "StartingBoost": 1.0})
    shape_comp(rules, "Marker", "/Engine/BasicShapes/Cube", mi_rules, unreal.Vector(0, 0, 50), unreal.Vector(0.6, 0.6, 0.6)).set_editor_property("hidden_in_game", True)
    text_comp(rules, "Label", "LEVEL RULES", unreal.Vector(0, 0, 130), FACE, 40.0, WHITE).set_editor_property("hidden_in_game", True)
    BEL.compile_blueprint(rules); log("saved", rp, EAL.save_asset(rp, only_if_is_dirty=False))

    # ---------------- boost pad: flat slab; speeds the car up for a moment, or (by level rule) refills the boost meter
    pp = DIR + "/BP_BoostPad"
    pad = new_bp("BP_BoostPad")
    add_vars(pad, [("BoostTime", R), ("ChargeAmount", R)], "Boost Pad")
    set_defaults(pad, {"BoostTime": 1.5, "ChargeAmount": 0.34})
    shape_comp(pad, "Shape", "/Engine/BasicShapes/Cube", mi_pad, unreal.Vector(0, 0, 1), unreal.Vector(4.0, 3.0, 0.03))
    text_comp(pad, "Label", "BOOST PAD", unreal.Vector(0, 0, 4), FLAT, 70.0, WHITE)
    trig = add_comp(pad, unreal.BoxComponent, "Trigger")
    trig.set_editor_property("box_extent", unreal.Vector(200, 150, 60)); trig.set_editor_property("relative_location", unreal.Vector(0, 0, 60))
    trigger_only(trig)
    BEL.compile_blueprint(pad)
    ed, g, n = graph(pad)
    ev = ed.find_event_node("ReceiveActorBeginOverlap"); g.dump(ev)
    cast, get, put = car_cast(ed, g, n, ev)
    br = n("Utilities|FlowControl|Branch", 600, 0)
    g.exe(cast, "then", br); g.link(get("PadsChargeMeter", 450, 200), "PadsChargeMeter", br, "Condition")
    # charge mode: meter += ChargeAmount (capped at full)
    ad = n("Utilities|Operators|Add", 800, 300); g.link(get("BoostAmount", 650, 300), "BoostAmount", ad, "A"); g.link(g.var_get("ChargeAmount", 650, 400), "ChargeAmount", ad, "B")
    mn = n("Math|Float|Min(Float)", 950, 300); g.link(ad, "ReturnValue", mn, "A"); g.val(mn, "B", "1.0")
    sb = put("BoostAmount", 1100, -100); g.exe(br, "then", sb); g.link(mn, "ReturnValue", sb, "BoostAmount")
    # speed mode: start / refresh the car's pad-boost timer
    st = put("PadBoostTimer", 1100, 150); g.exe(br, "else", st); g.link(g.var_get("BoostTime", 950, 450), "BoostTime", st, "PadBoostTimer")
    finish(pad, ed, pp)

    # ---------------- land mine: squat cylinder; throws the car up, costs a life, then is gone (level restart brings it back)
    mpth = DIR + "/BP_LandMine"
    mine = new_bp("BP_LandMine")
    add_vars(mine, [("LaunchHeight", R), ("HitCooldown", R)], "Land Mine")
    set_defaults(mine, {"LaunchHeight": 400.0, "HitCooldown": 1.5})
    shape_comp(mine, "Shape", "/Engine/BasicShapes/Cylinder", mi_mine, unreal.Vector(0, 0, 8), unreal.Vector(1.2, 1.2, 0.16))
    text_comp(mine, "Label", "LAND MINE", unreal.Vector(0, 0, 18), FLAT, 32.0, WHITE)
    text_comp(mine, "Sign", "LAND MINE", unreal.Vector(0, 0, 70), FACE, 36.0, unreal.Color(r=255, g=80, b=60, a=255))
    sp = add_comp(mine, unreal.SphereComponent, "Trigger")
    sp.set_editor_property("sphere_radius", 110.0); sp.set_editor_property("relative_location", unreal.Vector(0, 0, 40))
    trigger_only(sp)
    BEL.compile_blueprint(mine)
    ed, g, n = graph(mine)
    ev = ed.find_event_node("ReceiveActorBeginOverlap")
    cast, get, put = car_cast(ed, g, n, ev)
    # ignore hits while the car is still recovering from the last one (and once it's out of lives)
    cd = get("HitCooldown", 450, 200)
    le = n(["Utilities|Operators|LessEqual(<=)", "Utilities|Operators|LessEqual"], 600, 200); g.link(cd, "HitCooldown", le, "A"); g.val(le, "B", "0.0")
    nl = n("Math|Boolean|NOTBoolean", 600, 300); g.link(get("OutOfLives", 450, 300), "OutOfLives", nl, "A")
    an = n("Math|Boolean|ANDBoolean", 750, 250); g.link(le, "ReturnValue", an, "A"); g.link(nl, "ReturnValue", an, "B")
    br = n("Utilities|FlowControl|Branch", 900, 0); g.exe(cast, "then", br); g.link(an, "ReturnValue", br, "Condition")
    lv = get("Lives", 900, 300)
    sbt = n("Utilities|Operators|Subtract", 1050, 300); g.link(lv, "Lives", sbt, "A"); g.val(sbt, "B", "1")
    mx = n(["Math|Integer|Max", "Math|Integer|Max(Integer)"], 1200, 300); g.link(sbt, "ReturnValue", mx, "A"); g.val(mx, "B", "0")
    sl = put("Lives", 1300, 0); g.exe(br, "then", sl); g.link(mx, "ReturnValue", sl, "Lives")
    sc = put("HitCooldown", 1550, 0); g.exe(sl, "then", sc); g.link(g.var_get("HitCooldown", 1400, 250), "HitCooldown", sc, "HitCooldown")
    # launch speed for the same height under any gravity: v = sqrt(2 * |g| * h)
    mvc = get("VehicleMovementComponent", 1300, 500, VEH)
    gz = n(["Components|Movement|GetGravityZ", "Movement|GetGravityZ"], 1500, 500, unreal.MovementComponent); g.link(mvc, "VehicleMovementComponent", gz, "self")
    ab = n("Math|Float|Absolute(Float)", 1650, 500); g.link(gz, "ReturnValue", ab, "A")
    m2 = n("Utilities|Operators|Multiply", 1800, 500); g.link(ab, "ReturnValue", m2, "A"); g.link(g.var_get("LaunchHeight", 1650, 600), "LaunchHeight", m2, "B")
    m3 = n("Utilities|Operators|Multiply", 1950, 500); g.link(m2, "ReturnValue", m3, "A"); g.val(m3, "B", "2.0")
    sq = n("Math|Float|Sqrt", 2100, 500); g.link(m3, "ReturnValue", sq, "A")
    rx = n("Math|Random|RandomFloatinRange", 2100, 650); g.val(rx, "Min", "-150.0"); g.val(rx, "Max", "150.0")
    ry = n("Math|Random|RandomFloatinRange", 2100, 750); g.val(ry, "Min", "-150.0"); g.val(ry, "Max", "150.0")
    iv = n("Math|Vector|MakeVector", 2300, 550); g.link(rx, "ReturnValue", iv, "X"); g.link(ry, "ReturnValue", iv, "Y"); g.link(sq, "ReturnValue", iv, "Z")
    meshg = get("Mesh", 1800, 250, VEH)
    imp = n("Physics|AddImpulse", 1850, 0)
    g.exe(sc, "then", imp); g.link(meshg, "Mesh", imp, "self"); g.link(iv, "ReturnValue", imp, "Impulse"); g.val(imp, "bVelChange", "true")
    # random tumble so every hit looks a bit different
    ta = n("Math|Random|RandomFloatinRange", 2300, 750); g.val(ta, "Min", "-120.0"); g.val(ta, "Max", "120.0")
    tb = n("Math|Random|RandomFloatinRange", 2300, 850); g.val(tb, "Min", "-160.0"); g.val(tb, "Max", "160.0")
    tv = n("Math|Vector|MakeVector", 2500, 750); g.link(ta, "ReturnValue", tv, "X"); g.link(tb, "ReturnValue", tv, "Y"); g.val(tv, "Z", "0.0")
    ai = n(["Physics|AddAngularImpulseinDegrees", "Physics|AddAngularImpulseInDegrees"], 2150, 0)
    g.exe(imp, "then", ai); g.link(meshg, "Mesh", ai, "self"); g.link(tv, "ReturnValue", ai, "Impulse"); g.val(ai, "bVelChange", "true")
    da = n(["Actor|DestroyActor", "Utilities|DestroyActor", "Game|DestroyActor", "DestroyActor"], 2450, 0, unreal.Actor); g.exe(ai, "then", da)
    g.dump(imp); g.dump(ai); g.dump(gz)
    finish(mine, ed, mpth)
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V3_ASSETS_DONE")
