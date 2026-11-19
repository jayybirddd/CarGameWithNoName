# v6: track tuning — slower, less powerful, grippier car, plus the drift / ground-stick tuning variables.
# Re-runnable. The Moon car's transmission/engine copy is synced afterwards by v2_moon_setup.py (MODE = "APPLY").
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Scripts")
import gplace as gp; importlib.reload(gp)
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_handling.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
gp.LOG = log
EAL, BEL = gp.EAL, gp.BEL
BP = "/Game/Car/Blueprints/"
# --- tuning
MAX_TORQUE = 110.0                                  # was 420
GEARS = [2.4, 1.8, 1.45, 1.2, 1.03, 0.9]            # was 3.6 .. 0.9
FINAL_RATIO = 9.5                                   # was 3.4 -> top speed ~72 km/h at 7000 rpm (was ~200)
COM = unreal.Vector(10.0, 0.0, -15.0)               # was z 30: lower = harder to tip over the track edge
DOWNFORCE = 0.6                                     # was 0.3
FRONT_GRIP, REAR_GRIP, CORNERING = 3.6, 3.4, 1600.0  # were 3.0 / 2.8 / 1000
CAR_VARS = {"BoostAccel": 420.0, "PadAccel": 600.0,            # were 650 / 900, scaled to the lower top speed
            "RearGrip": REAR_GRIP, "DriftRearGrip": 2.2, "DriftYawAssist": 60.0, "DriftYawGain": 4.0, "DriftPush": 550.0, "DriftMinSpeed": 18.0,
            "DriftChargePerSec": 0.12, "DriftMaxTime": 4.0, "DriftMinTime": 0.35, "GroundStick": 500.0}
MOON_VARS = {"GroundStick": 0.0}                    # keep the Moon car floaty
try:
    car = unreal.load_asset(BP + "BP_CarPawn")
    R = gp.T("real")
    gp.add_vars(car, [(k, R) for k in ("RearGrip", "DriftRearGrip", "DriftYawAssist", "DriftYawGain", "DriftPush", "DriftMinSpeed", "DriftChargePerSec", "DriftMaxTime", "DriftMinTime", "GroundStick")], "Car Tuning")
    gp.add_vars(car, [("DriftTime", R), ("DriftPopup", R), ("DriftLastCharge", R), ("Drifting", gp.T("bool")), ("GameOverReady", gp.T("bool"))], "", editable=False)
    gp.add_vars(car, [("DriftHeld", gp.T("bool")), ("SteerAxis", R)], "Debug")   # instance-editable so test scripts can drive them
    mv = gp.comps(car)["VehicleMovementComponent"][1]
    tr = mv.get_editor_property("transmission_setup")
    tr.set_editor_property("forward_gear_ratios", GEARS); tr.set_editor_property("final_ratio", FINAL_RATIO)
    mv.set_editor_property("transmission_setup", tr)
    eng = mv.get_editor_property("engine_setup"); eng.set_editor_property("max_torque", MAX_TORQUE); mv.set_editor_property("engine_setup", eng)
    mv.set_editor_property("center_of_mass_override", COM)
    mv.set_editor_property("downforce_coefficient", DOWNFORCE)
    BEL.compile_blueprint(car)
    gp.set_defaults(car, CAR_VARS)
    BEL.compile_blueprint(car)
    log("saved car", EAL.save_asset(BP + "BP_CarPawn", only_if_is_dirty=False))
    log("trans", mv.get_editor_property("transmission_setup").export_text())
    for w, grip in (("BP_Wheel_Front", FRONT_GRIP), ("BP_Wheel_Rear", REAR_GRIP), ("BP_Wheel_Front_Moon", FRONT_GRIP), ("BP_Wheel_Rear_Moon", REAR_GRIP)):
        wb = unreal.load_asset(BP + w); cdo = unreal.get_default_object(wb.generated_class())
        cdo.set_editor_property("friction_force_multiplier", grip); cdo.set_editor_property("cornering_stiffness", CORNERING)
        BEL.compile_blueprint(wb); log("saved", w, EAL.save_asset(BP + w, only_if_is_dirty=False), cdo.get_editor_property("friction_force_multiplier"))
    moon = unreal.load_asset(BP + "BP_CarPawn_Moon")
    BEL.compile_blueprint(moon)
    gp.set_defaults(moon, MOON_VARS)
    BEL.compile_blueprint(moon)
    log("saved moon", EAL.save_asset(BP + "BP_CarPawn_Moon", only_if_is_dirty=False))
    log("check", {k: unreal.get_default_object(car.generated_class()).get_editor_property(k) for k in CAR_VARS},
        "moon GroundStick", unreal.get_default_object(moon.generated_class()).get_editor_property("GroundStick"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V6_HANDLING_DONE")
