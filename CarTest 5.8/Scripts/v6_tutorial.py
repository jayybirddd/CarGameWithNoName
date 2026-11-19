# v6: L_Tutorial — a straight run of signed stations that teach the controls, ending at a finish line.
# Made once with Save As from L_EarthBoostCharge (floor, sky, lights); later runs clear and re-place the tutorial content.
# Placeholder signs: a dark board with white text. Edit SIGNS to change the wording or spacing.
import unreal, traceback, os
OUT = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Saved/claude_v6_tutorial.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
TUT = "/Game/Levels/L_Tutorial"
SRC = "/Game/Levels/Testing/TEST_EarthBoostCharge"
P = "/Game/Car/Placeholders/"
# (distance ahead in cm, sign text). <br> breaks a line.
SIGNS = [(700, "WELCOME!<br>W / S  -  drive and brake<br>A / D  -  steer"),
         (2600, "SHIFT  -  BOOST<br>uses the blue bar,<br>which refills over time"),
         (4600, "SPACE  -  DRIFT<br>hold it while turning to slide<br>longer drifts refill more boost<br>(try it here)"),
         (8200, "BOOST PAD<br>drive over it<br>for a burst of speed"),
         (10800, "LAND MINE<br>avoid it! each hit costs a heart<br>lose all 3 and it's game over"),
         (13200, "T  -  automatic / manual gears<br>E / Q  -  shift up / down<br>P  -  pause      R  -  flip back over"),
         (15200, "RAMP<br>in the air:  W tips the nose down<br>S tips it back"),
         (19000, "FINISH<br>drive through the gate to win")]
PAD_AT = (9000, 0)
MINE_AT = (11600, 650)      # off to the side so the player can steer around it
RAMP_AT = (16600, 0)
FINISH_AT = 20500
try:
    f = "D:/PersonalGameFiles/CarGameWithNoName/CarTest 5.8/Content/Levels/L_Tutorial.umap"
    if not os.path.exists(f):
        log("load source", LES.load_level(SRC))
        log("save as", unreal.EditorLoadingAndSavingUtils.save_map(UES.get_editor_world(), TUT))
    log("load", LES.load_level(TUT), UES.get_editor_world().get_path_name())
    keep_ramp = None
    for a in EAS.get_all_level_actors():
        lb = a.get_actor_label()
        if lb == "Ramp_0": keep_ramp = a; continue
        # TestTrack: the source level may contain the race track mesh; the tutorial keeps a clear straight path
        if lb.startswith(("BoostPad_", "LandMine_", "Bump_", "Ramp_", "Tut_", "TestTrack")) or lb in ("FinishLine", "LevelRules"):
            EAS.destroy_actor(a)
    start = [a for a in EAS.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"][0]
    start.set_actor_location_and_rotation(unreal.Vector(0, 0, 92), unreal.Rotator(), False, True)
    board_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
    board_mat = unreal.load_asset(P + "MI_Placeholder_Wreck")
    for i, (x, text) in enumerate(SIGNS):
        lines = text.count("<br>") + 1
        h = 90 + lines * 75
        b = EAS.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, 750, 40 + h / 2), unreal.Rotator(roll=0.0, pitch=0.0, yaw=-20.0))
        b.set_actor_label("Tut_Board_%d" % i)
        sm = b.static_mesh_component; sm.set_static_mesh(board_mesh); sm.set_material(0, board_mat)
        b.set_actor_scale3d(unreal.Vector(0.1, 9.0, h / 100.0))
        sm.set_collision_profile_name("NoCollision")
        t = EAS.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(x - 12, 750 - 4, 40 + h / 2), unreal.Rotator(roll=0.0, pitch=0.0, yaw=160.0))
        t.set_actor_label("Tut_Sign_%d" % i)
        tr = t.text_render
        tr.set_text(unreal.Text(text))
        tr.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
        tr.set_editor_property("vertical_alignment", unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        tr.set_editor_property("world_size", 58.0)
        tr.set_editor_property("text_render_color", unreal.Color(r=255, g=255, b=255, a=255))
    pad = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_BoostPad").generated_class(), unreal.Vector(PAD_AT[0], PAD_AT[1], 0), unreal.Rotator())
    pad.set_actor_label("BoostPad_0")
    mine = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_LandMine").generated_class(), unreal.Vector(MINE_AT[0], MINE_AT[1], 0), unreal.Rotator())
    mine.set_actor_label("LandMine_0")
    if keep_ramp:
        keep_ramp.set_actor_location(unreal.Vector(RAMP_AT[0], RAMP_AT[1], keep_ramp.get_actor_location().z), False, True)
        keep_ramp.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=12.0, yaw=0.0), True)
        keep_ramp.set_actor_label("Ramp_0")
    fin = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_FinishLine").generated_class(), unreal.Vector(FINISH_AT, 0, 0), unreal.Rotator())
    fin.set_actor_label("FinishLine")
    rules = EAS.spawn_actor_from_class(unreal.load_asset(P + "BP_LevelRules").generated_class(), unreal.Vector(-400, 0, 0), unreal.Rotator())
    rules.set_actor_label("LevelRules")
    for k, v in {"BoostRegenEnabled": True, "PadsChargeMeter": False, "StartingLives": 3, "StartingBoost": 1.0}.items(): rules.set_editor_property(k, v)
    rules.set_editor_property("NextLevel", unreal.Name("L_Track1"))
    log("placed", len(SIGNS), "signs, ramp kept", keep_ramp is not None)
    log("saved", LES.save_current_level())
    ws = UES.get_editor_world().get_world_settings()
    log("gm", ws.get_editor_property("default_game_mode").get_name(), "gravity", ws.get_editor_property("global_gravity_set"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V6_TUTORIAL_DONE")
