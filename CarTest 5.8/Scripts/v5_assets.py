# v5: placeholder game flow — pause input, finish line (victory trigger), menu game mode + menu HUD,
# and the two menu levels (L_TitleScreen, L_LevelSelect). Re-runnable.
# The in-level overlays (pause / game over / victory) live in BP_CarHUD (v2_hud.py).
import unreal, traceback, sys, importlib, os
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import gplace as gp; importlib.reload(gp)
import ghud; importlib.reload(ghud)
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v5_assets.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
gp.LOG = log
EAL, BEL = gp.EAL, gp.BEL
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
PH = "/Game/Car/Placeholders"
BP = "/Game/Car/Blueprints"
PCC = "/Script/Engine.PlayerController"
TITLE, SELECT = "/Game/Levels/L_TitleScreen", "/Game/Levels/L_LevelSelect"
# (button label, level name) — the level select list; a level's hit box is named after the level it opens
LEVELS = [("Earth Test Track", "L_EarthTestTrack"), ("Moon Test Track", "L_MoonTestTrack"),
          ("Earth Boost Charge", "L_EarthBoostCharge"), ("Moon Boost Charge", "L_MoonBoostCharge")]
WHITE = "(R=1.000000,G=1.000000,B=1.000000,A=1.000000)"
try:
    # ---------------- pause input: P / Escape / gamepad Start, works while the game is paused
    ia_path = "/Game/Car/Input/IA_Pause"
    ia = unreal.load_asset(ia_path) if EAL.does_asset_exist(ia_path) else gp.AT.create_asset("IA_Pause", "/Game/Car/Input", unreal.InputAction, unreal.InputAction_Factory())
    ia.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
    ia.set_editor_property("trigger_when_paused", True)
    log("saved IA_Pause", EAL.save_asset(ia_path, only_if_is_dirty=False))
    imc = unreal.load_asset("/Game/Car/Input/IMC_Car")
    have = [(m.get_editor_property("action").get_name(), str(m.get_editor_property("key").get_editor_property("key_name")))
            for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")]
    imc.modify()
    for kn in ("P", "Escape", "Gamepad_Special_Right"):
        if ("IA_Pause", kn) not in have:
            k = unreal.Key(); k.set_editor_property("key_name", kn); imc.map_key(ia, k); log("mapped IA_Pause", kn)
    log("saved IMC", EAL.save_asset("/Game/Car/Input/IMC_Car", only_if_is_dirty=False))

    # ---------------- car / rules variables
    car = unreal.load_asset(BP + "/BP_CarPawn")
    gp.add_vars(car, [("Won", gp.T("bool"))], "", editable=False)
    log("saved car", EAL.save_asset(BP + "/BP_CarPawn", only_if_is_dirty=False))
    rules = unreal.load_asset(PH + "/BP_LevelRules")
    gp.add_vars(rules, [("NextLevel", gp.T("name"))], "Level Rules")
    log("saved rules", EAL.save_asset(PH + "/BP_LevelRules", only_if_is_dirty=False))

    # ---------------- finish line: gate labelled FINISH; driving through it wins the level
    fp = PH + "/BP_FinishLine"
    fin = gp.new_bp("BP_FinishLine", PH)
    mi = unreal.load_asset(PH + "/MI_Placeholder_Finish") if EAL.does_asset_exist(PH + "/MI_Placeholder_Finish") else \
        gp.AT.create_asset("MI_Placeholder_Finish", PH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(mi, unreal.load_asset(PH + "/M_Placeholder"))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(1.0, 0.85, 0.1, 1))
    EAL.save_asset(PH + "/MI_Placeholder_Finish", only_if_is_dirty=False)
    for nm, y in (("PostL", -550.0), ("PostR", 550.0)):
        gp.shape_comp(fin, nm, "/Engine/BasicShapes/Cylinder", mi, unreal.Vector(0, y, 200), unreal.Vector(0.4, 0.4, 4.0))
    gp.shape_comp(fin, "Banner", "/Engine/BasicShapes/Cube", mi, unreal.Vector(0, 0, 420), unreal.Vector(0.3, 11.4, 0.8))
    black = unreal.Color(r=20, g=20, b=20, a=255)
    gp.text_comp(fin, "LabelFront", "FINISH", unreal.Vector(-18, 0, 420), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), 70.0, black)
    gp.text_comp(fin, "LabelBack", "FINISH", unreal.Vector(18, 0, 420), unreal.Rotator(), 70.0, black)
    tr = gp.add_comp(fin, unreal.BoxComponent, "Trigger")
    tr.set_editor_property("box_extent", unreal.Vector(100, 520, 250)); tr.set_editor_property("relative_location", unreal.Vector(0, 0, 250))
    gp.trigger_only(tr)
    BEL.compile_blueprint(fin)
    ed, g, n = gp.graph(fin)
    ev = ed.find_event_node("ReceiveActorBeginOverlap")
    cast = n("Utilities|Casting|CastToBP_CarPawn", 300, 0); g.exe(ev, "then", cast); g.link(ev, "OtherActor", cast, "Object")
    get = lambda nm, x, y, o=gp.CARC: gp.member(ed, g, cast, o, nm, x, y)
    put = lambda nm, x, y, o=gp.CARC: gp.member(ed, g, cast, o, nm, x, y, setter=True)
    n1 = n("Math|Boolean|NOTBoolean", 600, 250); g.link(get("OutOfLives", 450, 250), "OutOfLives", n1, "A")
    n2 = n("Math|Boolean|NOTBoolean", 600, 350); g.link(get("Won", 450, 350), "Won", n2, "A")
    an = n("Math|Boolean|ANDBoolean", 750, 300); g.link(n1, "ReturnValue", an, "A"); g.link(n2, "ReturnValue", an, "B")
    br = n("Utilities|FlowControl|Branch", 900, 0); g.exe(cast, "then", br); g.link(an, "ReturnValue", br, "Condition")
    sw = put("Won", 1100, 0); g.exe(br, "then", sw); g.val(sw, "Won", "true")
    # stop the car and take driving input away; BP_CarHUD sees Won and shows the victory screen
    mvc = get("VehicleMovementComponent", 1100, 300, gp.VEH)
    st = n("Game|Components|ChaosVehicleMovement|SetThrottleInput", 1350, 0); g.exe(sw, "then", st); g.link(mvc, "VehicleMovementComponent", st, "self"); g.val(st, "Throttle", "0.0")
    sh = n("Game|Components|ChaosVehicleMovement|SetHandbrakeInput", 1600, 0); g.exe(st, "then", sh); g.link(mvc, "VehicleMovementComponent", sh, "self"); g.val(sh, "bNewHandbrake", "true")
    dis = n("Input|DisableInput", 1850, 0, unreal.Actor); g.exe(sh, "then", dis)
    g.link(cast, gp.as_pin(g, cast), dis, "self"); g.link(n("Game|GetPlayerController", 1700, 250), "ReturnValue", dis, "PlayerController")
    gp.finish(fin, ed, fp)

    # ---------------- menu game mode + HUD (title screen and level select)
    hud = gp.new_bp("BP_MenuHUD", BP, unreal.HUD)
    gp.add_vars(hud, [("IsLevelSelect", gp.T("bool"))], "", editable=False)
    ed, g, n = gp.graph(hud, keep=())
    bp_ev = n(["AddEvent|EventBeginPlay", "AddEvent|Game|EventBeginPlay"], 0, -600)
    pc = n("HUD|GetOwningPlayerController", 0, -400)
    s1 = ed.add_set_member_variable_node("bShowMouseCursor", PCC); s1.set_node_pos(unreal.IntPoint(300, -600))
    g.exe(bp_ev, "then", s1); g.link(pc, "ReturnValue", s1, "self"); g.val(s1, "bShowMouseCursor", "true")
    s2 = ed.add_set_member_variable_node("bEnableClickEvents", PCC); s2.set_node_pos(unreal.IntPoint(600, -600))
    g.exe(s1, "then", s2); g.link(pc, "ReturnValue", s2, "self"); g.val(s2, "bEnableClickEvents", "true")
    cln = n("Game|GetCurrentLevelName", 900, -600); g.exe(s2, "then", cln)
    eq = n(ghud.STRING_EQUALS, 1100, -450); g.link(cln, "ReturnValue", eq, "A"); g.val(eq, "B", "L_LevelSelect")
    sls = g.var_set("IsLevelSelect", 1300, -600); g.exe(cln, "then", sls); g.link(eq, "ReturnValue", sls, "IsLevelSelect")
    draw = n(["AddEvent|EventReceiveDrawHUD", "AddEvent|ReceiveDrawHUD"], 0, 0)
    M = ghud.Menu(ed, g, n, draw, 200, 600)
    br = n("Utilities|FlowControl|Branch", 200, 0); g.exe(draw, "then", br); g.link(g.var_get("IsLevelSelect", 0, 200), "IsLevelSelect", br, "Condition")
    M.panel(br, "then", "SELECT LEVEL", [(lv, lb) for lb, lv in LEVELS] + [("Back", "Back")], bg_alpha=1.0)
    M.panel(br, "else", "CAR TEST", [("Play", "Play"), ("Quit", "Quit")], bg_alpha=1.0, note="placeholder title screen")
    click = n(ghud.CLICK_EVENT, 0, 3000)
    g.dump(click)
    def quit_game(node, pin):
        q = n(["Utilities|QuitGame", "Game|QuitGame"], 1500, 3400); g.exe(node, pin, q)
        g.link(n("Game|GetPlayerController", 1300, 3600), "ReturnValue", q, "SpecificPlayer")
    last, lpin = ghud.dispatch(g, n, click, [
        ("Play", lambda nd, p: ghud.open_level(g, n, nd, p, "L_LevelSelect", 600, 3300)),
        ("Quit", quit_game),
        ("Back", lambda nd, p: ghud.open_level(g, n, nd, p, "L_TitleScreen", 1600, 3300))], 300, 3000)
    ghud.open_level(g, n, last, lpin, (click, "BoxName"), 2000, 3000)   # any other box is a level name
    gp.finish(hud, ed, BP + "/BP_MenuHUD")

    gm = gp.new_bp("BP_MenuGameMode", BP, unreal.GameModeBase)
    cdo = unreal.get_default_object(gm.generated_class())
    cdo.set_editor_property("hud_class", hud.generated_class())
    try: cdo.set_editor_property("default_pawn_class", unreal.SpectatorPawn)
    except Exception as e: log("pawn class", e)
    BEL.compile_blueprint(gm); log("saved gm", EAL.save_asset(BP + "/BP_MenuGameMode", only_if_is_dirty=False))

    # ---------------- the two menu levels: empty worlds whose game mode draws the menu
    for path in (TITLE, SELECT):
        f = "D:/PersonalGameFiles/CarTest 5.8/Content" + path[len("/Game"):] + ".umap"
        if not os.path.exists(f):
            log("new level", path, LES.new_level(path))
        else:
            log("load", path, LES.load_level(path))
        ws = UES.get_editor_world().get_world_settings()
        ws.set_editor_property("default_game_mode", gm.generated_class())
        log("save", path, LES.save_current_level(), UES.get_editor_world().get_path_name())
    log("back", LES.load_level("/Game/Levels/L_EarthTestTrack"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V5_ASSETS_DONE")
