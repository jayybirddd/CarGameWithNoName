import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_build3.txt"
L = []
def p(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
def setp(obj, name, val):
    try: obj.set_editor_property(name, val); return True
    except Exception as e: p("  !set", name, e); return False
try:
    imc = unreal.load_asset("/Game/Car/Input/IMC_Car")
    dkm = imc.get_editor_property("default_key_mappings")
    p("dkm type", type(dkm).__name__, [x for x in dir(dkm) if not x.startswith("_")][:40])
    maps = list(dkm.get_editor_property("mappings"))
    p("count", len(maps))
    negs = {("IA_Throttle","S"),("IA_Throttle","Down"),("IA_Throttle","Gamepad_LeftTriggerAxis"),("IA_Steer","A"),("IA_Steer","Left")}
    for m in maps:
        an = m.get_editor_property("action").get_name(); kn = str(m.get_editor_property("key").get_editor_property("key_name"))
        if (an, kn) in negs:
            m.set_editor_property("modifiers", [unreal.InputModifierNegate()])
    dkm.set_editor_property("mappings", maps)
    imc.set_editor_property("default_key_mappings", dkm)
    for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings"):
        p("map", m.get_editor_property("action").get_name(), m.get_editor_property("key").get_editor_property("key_name"), [type(x).__name__ for x in m.get_editor_property("modifiers")])
    EAL.save_asset("/Game/Car/Input/IMC_Car")
except Exception:
    p(traceback.format_exc())
try:
    car_path = "/Game/Car/Blueprints/BP_CarPawn"
    car = unreal.load_asset(car_path)
    comps = {}
    for h in SDS.k2_gather_subobject_data_for_blueprint(car):
        d = SDS.k2_find_subobject_data_from_handle(h)
        comps[str(SDL.get_variable_name(d))] = (h, SDL.get_object(d))
    mv = comps["VehicleMovementComponent"][1]
    skm = comps["Mesh"][1]
    p("mesh asset", skm.get_editor_property("skeletal_mesh_asset"), "collision", skm.get_collision_profile_name(), "sim", skm.is_simulating_physics() if hasattr(skm,"is_simulating_physics") else "?")
    try:
        bi = skm.get_editor_property("body_instance"); p("body sim", bi.get_editor_property("simulate_physics"))
    except Exception as e: p("bi err", e)
    df = mv.get_editor_property("differential_setup")
    cur = df.get_editor_property("differential_type")
    p("diff enum", type(cur), cur, [x for x in dir(type(cur)) if x.isupper()])
    for n in dir(type(cur)):
        if "ALL" in n and "WHEEL" in n:
            setp(df, "differential_type", getattr(type(cur), n))
    setp(df, "front_rear_split", 0.35)
    setp(mv, "differential_setup", df)
    st = mv.get_editor_property("steering_setup")
    p("steer", st, [x for x in dir(st) if not x.startswith("_")][:30])
    p("engine", mv.get_editor_property("engine_setup"))
    p("trans", mv.get_editor_property("transmission_setup"))
    p("diff", mv.get_editor_property("differential_setup"))
    p("wheels", [ (w.get_editor_property("bone_name"), w.get_editor_property("wheel_class")) for w in mv.get_editor_property("wheel_setups")])
    p("mass", mv.get_editor_property("mass"), "com", mv.get_editor_property("center_of_mass_override"), mv.get_editor_property("enable_center_of_mass_override"))
    for nm, tp in [("CameraYaw", "real"), ("UsingHoodCam", "bool")]:
        if nm not in [str(x) for x in BEL.list_member_variable_names(car)]:
            try: BEL.add_member_variable(car, nm, BEL.get_basic_type_by_name(tp))
            except Exception as e: p("var err", nm, e)
    p("vars", [str(x) for x in BEL.list_member_variable_names(car)])
    BEL.compile_blueprint(car); EAL.save_asset(car_path)
    gm_path = "/Game/Car/Blueprints/BP_CarGameMode"
    AT = unreal.AssetToolsHelpers.get_asset_tools()
    if not EAL.does_asset_exist(gm_path):
        f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.GameModeBase)
        gm = AT.create_asset("BP_CarGameMode", "/Game/Car/Blueprints", unreal.Blueprint, f)
    gm = unreal.load_asset(gm_path)
    gcdo = unreal.get_default_object(gm.generated_class())
    setp(gcdo, "default_pawn_class", car.generated_class())
    BEL.compile_blueprint(gm); EAL.save_asset(gm_path)
    p("gm pawn", gcdo.get_editor_property("default_pawn_class"))
    gms = unreal.get_default_object(unreal.GameMapsSettings)
    p("gms", [x for x in dir(gms) if not x.startswith("_") and ("game" in x.lower() or "map" in x.lower())])
except Exception:
    p(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_BUILD3_DONE")
