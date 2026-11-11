# Helpers for building placeholder Blueprints (shapes + labels + triggers) and their graphs from Python.
import unreal, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import ghy as gh; importlib.reload(gh)
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
PL = unreal.BlueprintGraphPinLibrary
CARC = "/Game/Car/Blueprints/BP_CarPawn.BP_CarPawn_C"
VEH = "/Script/ChaosVehicles.WheeledVehiclePawn"
LOG = print
def T(name): return BEL.get_basic_type_by_name(name)

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
        except Exception as e: LOG("!! default", bp.get_name(), k, e)

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

def new_bp(name, folder, parent=unreal.Actor):
    path = folder + "/" + name
    if EAL.does_asset_exist(path): return unreal.load_asset(path)
    f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", parent)
    return AT.create_asset(name, folder, unreal.Blueprint, f)

def graph(bp, keep=("Event BeginPlay", "Event ActorBeginOverlap", "Event Tick")):
    """Clears the event graph (keeping the stock event nodes) and returns (editor, helper, node-maker)."""
    ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(bp))
    ed.remove_nodes([nd for nd in ed.list_all_nodes() if str(BEL.get_node_title(nd)).splitlines()[0] not in keep])
    g = gh.G(ed, LOG)
    def n(names, x, y, cls=None):
        if isinstance(names, str): names = [names]
        for nm in names:
            nd = ed.create_node_from_name(nm, unreal.Vector2D(x, y), [], cls) if cls else ed.create_node_from_name(nm, unreal.Vector2D(x, y), [])
            if nd is not None: return nd
        LOG("!! node failed", names); return None
    return ed, g, n

def as_pin(g, node):
    return [str(PL.get_pin_name(p)) for p in g.pins(node) if str(PL.get_pin_name(p)).startswith("As")][0]

def member(ed, g, cast, owner, name, x, y, setter=False):
    nd = ed.add_set_member_variable_node(name, owner) if setter else ed.add_get_member_variable_node(name, owner)
    if nd is None: LOG("!! member", name); return None
    nd.set_node_pos(unreal.IntPoint(x, y)); g.link(cast, as_pin(g, cast), nd, "self"); return nd

def finish(bp, ed, path):
    BEL.compile_blueprint(bp)
    for nd in ed.list_nodes_with_errors(): LOG("ERROR", bp.get_name(), BEL.get_node_title(nd))
    for nd in ed.list_nodes_with_warnings(): LOG("WARN", bp.get_name(), BEL.get_node_title(nd))
    LOG("saved", path, EAL.save_asset(path, only_if_is_dirty=False))
