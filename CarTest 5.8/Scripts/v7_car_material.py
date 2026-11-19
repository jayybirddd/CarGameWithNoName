# Gives the driving car the same material as the separated car (the wreck), so it doesn't change colour when it explodes.
# Set on BP_CarPawn's Mesh component as a material override; the Moon car inherits it. SK_Car itself is left untouched.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gplace as gp; importlib.reload(gp)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v7_car_material.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
gp.LOG = log
try:
    sep = unreal.load_asset("/Game/Car/SeparatedCar/CAR_separated")
    sk = unreal.load_asset("/Game/Car/Mesh/SK_Car")
    sep_mats = [m.get_editor_property("material_interface") for m in sep.get_editor_property("materials")]
    car_slots = sk.get_editor_property("materials")
    log("separated materials", [m.get_path_name() if m else None for m in sep_mats])
    log("SK_Car slots", [(str(s.get_editor_property("material_slot_name")), s.get_editor_property("material_interface").get_path_name() if s.get_editor_property("material_interface") else None) for s in car_slots])
    car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
    mesh = gp.comps(car)["Mesh"][1]
    log("override before", [m.get_path_name() if m else None for m in mesh.get_editor_property("override_materials")])
    mesh.set_editor_property("override_materials", [sep_mats[0]] * len(car_slots))
    gp.BEL.compile_blueprint(car)
    log("saved car", gp.EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn", only_if_is_dirty=False))
    moon = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn_Moon")
    gp.BEL.compile_blueprint(moon)
    log("moon mesh overrides", [m.get_path_name() if m else None for m in gp.comps(moon)["Mesh"][1].get_editor_property("override_materials")])
    log("saved moon", gp.EAL.save_asset("/Game/Car/Blueprints/BP_CarPawn_Moon", only_if_is_dirty=False))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
