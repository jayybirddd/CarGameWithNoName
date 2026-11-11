# v2: BP_CarHUD — boost bar + gear / AUTO-MANUAL readout. Hooked into both car game modes.
import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest 5.8/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_hud.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
HUD = "/Game/Car/Blueprints/BP_CarHUD"
CARC = "/Game/Car/Blueprints/BP_CarPawn.BP_CarPawn_C"
try:
    if EAL.does_asset_exist(HUD):
        hud = unreal.load_asset(HUD)
    else:
        f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.HUD)
        hud = AT.create_asset("BP_CarHUD", "/Game/Car/Blueprints", unreal.Blueprint, f)
    ed = unreal.BlueprintGraphEditor.get_graph_editor(BEL.find_event_graph(hud))
    ed.remove_nodes(list(ed.list_all_nodes()))
    g = gh.G(ed, log)
    def n(names, x, y, cls=None):
        if isinstance(names, str): names = [names]
        for nm in names:
            nd = ed.create_node_from_name(nm, unreal.Vector2D(x, y), [], cls) if cls else ed.create_node_from_name(nm, unreal.Vector2D(x, y), [])
            if nd is not None: return nd
        log("!! node failed", names); return None
    ev = n(["AddEvent|EventReceiveDrawHUD", "AddEvent|ReceiveDrawHUD"], 0, 0)
    g.dump(ev)
    op = n("HUD|GetOwningPawn", 0, 200)
    cast = n("Utilities|Casting|CastToBP_CarPawn", 250, 0)
    g.exe(ev, "then", cast); g.link(op, "ReturnValue", cast, "Object")
    co = [str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)) for p in g.pins(cast) if str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)).startswith("As")][0]
    def mvar(name, owner, x, y):
        nd = ed.add_get_member_variable_node(name, owner)
        if nd is None: log("!! var", name); return None
        nd.set_node_pos(unreal.IntPoint(x, y)); g.link(cast, co, nd, "self"); return nd
    boost = mvar("BoostAmount", CARC, 500, 300)
    bfx = mvar("BoostFX", CARC, 500, 400)
    auto = mvar("AutoGears", CARC, 500, 500)
    mvc = mvar("VehicleMovementComponent", "/Script/ChaosVehicles.WheeledVehiclePawn", 500, 600)
    # layout: bottom-left
    def yoff(off, x, y):
        a = n("Utilities|Operators|Subtract", x, y); g.link(ev, "SizeY", a, "A"); g.val(a, "B", str(off)); return a
    # background bar
    y_bg = yoff(90, 700, 250)
    r1 = n("HUD|DrawRect", 900, 0)
    g.exe(cast, "then", r1)
    g.val(r1, "RectColor", "(R=0.000000,G=0.000000,B=0.000000,A=0.550000)")
    g.val(r1, "ScreenX", "40.0"); g.link(y_bg, "ReturnValue", r1, "ScreenY"); g.val(r1, "ScreenW", "324.0"); g.val(r1, "ScreenH", "22.0")
    g.dump(r1)
    # fill
    fw = n("Utilities|Operators|Multiply", 900, 450); g.link(boost, "BoostAmount", fw, "A"); g.val(fw, "B", "320.0")
    y_f = yoff(88, 900, 350)
    lc = n(["Math|Color|Lerp(LinearColor)", "Math|Color|LinearColorLerp", "Math|Color|Lerp"], 900, 550)
    g.dump(lc)
    g.val(lc, "A", "(R=0.100000,G=0.700000,B=1.000000,A=0.950000)"); g.val(lc, "B", "(R=1.000000,G=0.450000,B=0.050000,A=1.000000)")
    g.link(bfx, "BoostFX", lc, "Alpha")
    r2 = n("HUD|DrawRect", 1200, 0)
    g.exe(r1, "then", r2)
    g.link(lc, "ReturnValue", r2, "RectColor")
    g.val(r2, "ScreenX", "42.0"); g.link(y_f, "ReturnValue", r2, "ScreenY"); g.link(fw, "ReturnValue", r2, "ScreenW"); g.val(r2, "ScreenH", "18.0")
    # "BOOST" label
    y_l = yoff(122, 1200, 350)
    t1 = n("HUD|DrawText", 1500, 0)
    g.exe(r2, "then", t1); g.dump(t1)
    g.val(t1, "Text", "BOOST"); g.val(t1, "TextColor", "(R=1.000000,G=1.000000,B=1.000000,A=1.000000)")
    g.val(t1, "ScreenX", "40.0"); g.link(y_l, "ReturnValue", t1, "ScreenY"); g.val(t1, "Scale", "1.3")
    # gear + mode line
    cg = n("Game|Components|ChaosVehicleMovement|GetCurrentGear", 1300, 600); g.link(mvc, "VehicleMovementComponent", cg, "self")
    gs = n("Utilities|String|ToString(Integer)", 1500, 600); g.link(cg, "ReturnValue", gs, "InInt")
    lt0 = n("Utilities|Operators|Less(<)", 1500, 700); g.link(cg, "ReturnValue", lt0, "A"); g.val(lt0, "B", "0")
    eq0 = n(["Utilities|Operators|Equal(==)", "Utilities|Operators|Equal"], 1500, 800); g.link(cg, "ReturnValue", eq0, "A"); g.val(eq0, "B", "0")
    ss1 = n(["Utilities|String|SelectString", "Math|String|SelectString"], 1700, 650)
    g.dump(ss1)
    g.val(ss1, "A", "R"); g.link(gs, "ReturnValue", ss1, "B"); g.link(lt0, "ReturnValue", ss1, "bPickA")
    ss2 = n(["Utilities|String|SelectString", "Math|String|SelectString"], 1900, 650)
    g.val(ss2, "A", "N"); g.link(ss1, "ReturnValue", ss2, "B"); g.link(eq0, "ReturnValue", ss2, "bPickA")
    ss3 = n(["Utilities|String|SelectString", "Math|String|SelectString"], 1900, 850)
    g.val(ss3, "A", "AUTO"); g.val(ss3, "B", "MANUAL  (E/Q to shift)"); g.link(auto, "AutoGears", ss3, "bPickA")
    ap = n("Utilities|String|Append", 2100, 650)
    ed.add_node_pin(ap); ed.add_node_pin(ap)
    g.val(ap, "A", "GEAR "); g.link(ss2, "ReturnValue", ap, "B"); g.val(ap, "C", "    "); g.link(ss3, "ReturnValue", ap, "D") if g.pin(ap, "D", "in") else None
    y_g = yoff(160, 1800, 350)
    t2 = n("HUD|DrawText", 2300, 0)
    g.exe(t1, "then", t2)
    g.link(ap, "ReturnValue", t2, "Text"); g.val(t2, "TextColor", "(R=1.000000,G=0.900000,B=0.400000,A=1.000000)")
    g.val(t2, "ScreenX", "40.0"); g.link(y_g, "ReturnValue", t2, "ScreenY"); g.val(t2, "Scale", "1.5")
    # ---------- lives: pixel-art hearts, top-left (up to 5 slots; slots past MaxLives are hidden)
    lives = mvar("Lives", CARC, 2400, 300); maxl = mvar("MaxLives", CARC, 2400, 400)
    P = 6.0
    ROWS = ((0, 1, 2, 1), (0, 4, 2, 1), (1, 0, 7, 2), (3, 1, 5, 1), (4, 2, 3, 1), (5, 3, 1, 1))  # (row, col, width, height) in pixels
    prev = t2
    for i in range(5):
        x0 = 40.0 + i * 52.0; y0 = 84.0   # below the controls hint lines
        gt = n("Utilities|Operators|Greater(>)", 2600 + i * 600, 300); g.link(lives, "Lives", gt, "A"); g.val(gt, "B", str(i))
        fa = n("Math|Float|SelectFloat", 2750 + i * 600, 300); g.val(fa, "A", "1.0"); g.val(fa, "B", "0.0"); g.link(gt, "ReturnValue", fa, "bPickA")
        hc = n(["Math|Color|Lerp(LinearColor)", "Math|Color|LinearColorLerp", "Math|Color|Lerp"], 2900 + i * 600, 300)
        g.val(hc, "A", "(R=0.150000,G=0.150000,B=0.150000,A=0.600000)"); g.val(hc, "B", "(R=1.000000,G=0.080000,B=0.120000,A=1.000000)"); g.link(fa, "ReturnValue", hc, "Alpha")
        gs_ = n("Utilities|Operators|Greater(>)", 2600 + i * 600, 450); g.link(maxl, "MaxLives", gs_, "A"); g.val(gs_, "B", str(i))
        sa = n("Math|Float|SelectFloat", 2750 + i * 600, 450); g.val(sa, "A", "1.0"); g.val(sa, "B", "0.0"); g.link(gs_, "ReturnValue", sa, "bPickA")
        hv = n(["Math|Color|Lerp(LinearColor)", "Math|Color|LinearColorLerp", "Math|Color|Lerp"], 3050 + i * 600, 400)
        g.val(hv, "A", "(R=0.000000,G=0.000000,B=0.000000,A=0.000000)"); g.link(hc, "ReturnValue", hv, "B"); g.link(sa, "ReturnValue", hv, "Alpha")
        for j, (row, col, w, h) in enumerate(ROWS):
            r = n("HUD|DrawRect", 2600 + i * 600 + j * 90, 0)
            g.exe(prev, "then", r); prev = r
            g.link(hv, "ReturnValue", r, "RectColor")
            g.val(r, "ScreenX", str(x0 + col * P)); g.val(r, "ScreenY", str(y0 + row * P)); g.val(r, "ScreenW", str(w * P)); g.val(r, "ScreenH", str(h * P))
    # ---------- "no recharge" hint above the boost bar
    pcm = mvar("PadsChargeMeter", CARC, 5800, 300); ool = mvar("OutOfLives", CARC, 5800, 400)
    hs = n(["Utilities|String|SelectString", "Math|String|SelectString"], 6000, 300)
    g.val(hs, "A", "NO RECHARGE  -  drive over BOOST PADS to refill"); g.val(hs, "B", ""); g.link(pcm, "PadsChargeMeter", hs, "bPickA")
    y_h = yoff(196, 6000, 450)
    t3 = n("HUD|DrawText", 6200, 0); g.exe(prev, "then", t3)
    g.link(hs, "ReturnValue", t3, "Text"); g.val(t3, "TextColor", "(R=0.400000,G=0.850000,B=1.000000,A=1.000000)")
    g.val(t3, "ScreenX", "40.0"); g.link(y_h, "ReturnValue", t3, "ScreenY"); g.val(t3, "Scale", "1.1")
    # ---------- pause / game over / victory overlays (placeholder menus; buttons are HUD hit boxes, see ghud.py)
    import ghud; importlib.reload(ghud)
    PCC = "/Script/Engine.PlayerController"
    RULESC = "/Game/Car/Placeholders/BP_LevelRules.BP_LevelRules_C"
    won = mvar("Won", CARC, 6300, 500)
    paused = n("Game|IsGamePaused", 6300, 600)
    seq = n("Utilities|FlowControl|Sequence", 6400, 0); g.exe(t3, "then", seq); ed.add_node_pin(seq); ed.add_node_pin(seq)
    M = ghud.Menu(ed, g, n, ev, 6700, 1200)
    def overlay(pin, cond, cond_pin, title, buttons, color, note=None):
        br = n("Utilities|FlowControl|Branch", M.x, 0); g.exe(seq, pin, br); g.link(cond, cond_pin, br, "Condition")
        M.panel(br, "then", title, buttons, 0.65, color, note)
    WHITE, RED, GOLD = "(R=1.000000,G=1.000000,B=1.000000,A=1.000000)", "(R=1.000000,G=0.150000,B=0.150000,A=1.000000)", "(R=1.000000,G=0.850000,B=0.150000,A=1.000000)"
    overlay("then_0", paused, "ReturnValue", "PAUSED", [("Resume", "Resume"), ("Restart", "Restart Level"), ("LevelSelect", "Level Select"), ("Title", "Title Screen")], WHITE, "P / Esc / Start resumes")
    overlay("then_1", ool, "OutOfLives", "GAME OVER", [("Restart", "Retry"), ("LevelSelect", "Level Select"), ("Title", "Title Screen")], RED)
    overlay("then_2", won, "Won", "VICTORY!", [("Next", "Next Level"), ("Restart", "Play Again"), ("LevelSelect", "Level Select"), ("Title", "Title Screen")], GOLD)
    # mouse cursor only while one of the overlays is up
    o1 = n("Math|Boolean|ORBoolean", M.x, 400); g.link(paused, "ReturnValue", o1, "A"); g.link(ool, "OutOfLives", o1, "B")
    o2 = n("Math|Boolean|ORBoolean", M.x + 150, 400); g.link(o1, "ReturnValue", o2, "A"); g.link(won, "Won", o2, "B")
    opc = n("HUD|GetOwningPlayerController", M.x, 600)
    scur = ed.add_set_member_variable_node("bShowMouseCursor", PCC); scur.set_node_pos(unreal.IntPoint(M.x + 300, 0))
    g.exe(seq, "then_3", scur); g.link(opc, "ReturnValue", scur, "self"); g.link(o2, "ReturnValue", scur, "bShowMouseCursor")
    # hit boxes only report clicks when the player controller has click events on
    bpe = n(["AddEvent|EventBeginPlay", "AddEvent|Game|EventBeginPlay"], 0, -800)
    bpc = n("HUD|GetOwningPlayerController", 0, -600)
    sclk = ed.add_set_member_variable_node("bEnableClickEvents", PCC); sclk.set_node_pos(unreal.IntPoint(300, -800))
    g.exe(bpe, "then", sclk); g.link(bpc, "ReturnValue", sclk, "self"); g.val(sclk, "bEnableClickEvents", "true")
    # ---------- button clicks
    click = n(ghud.CLICK_EVENT, 0, 4000)
    def resume(nd, pin):
        sp = n("Game|SetGamePaused", 600, 4400); g.exe(nd, pin, sp); g.val(sp, "bPaused", "false")
    def restart(nd, pin):
        cl = n("Game|GetCurrentLevelName", 1100, 4400); g.exe(nd, pin, cl)
        sn = n(ghud.TO_NAME, 1300, 4600); g.link(cl, "ReturnValue", sn, "InString")
        ghud.open_level(g, n, cl, "then", (sn, "ReturnValue"), 1500, 4400)
    def next_level(nd, pin):
        # the level's BP_LevelRules names the next level; none set (or no rules actor) -> level select
        ga = n(["Utilities|GetActorOfClass", "Actor|GetActorOfClass"], 2600, 4400); g.exe(nd, pin, ga); g.val(ga, "ActorClass", RULESC)
        rc = n("Utilities|Casting|CastToBP_LevelRules", 2850, 4400); g.exe(ga, "then", rc); g.link(ga, "ReturnValue", rc, "Object")
        nl = ed.add_get_member_variable_node("NextLevel", RULESC); nl.set_node_pos(unreal.IntPoint(2900, 4650))
        g.link(rc, [str(unreal.BlueprintGraphPinLibrary.get_pin_name(q)) for q in g.pins(rc) if str(unreal.BlueprintGraphPinLibrary.get_pin_name(q)).startswith("As")][0], nl, "self")
        eqn = ghud.name_equals(g, n, (nl, "NextLevel"), "None", 3100, 4650)
        bn = n("Utilities|FlowControl|Branch", 3100, 4400); g.exe(rc, "then", bn); g.link(eqn, "ReturnValue", bn, "Condition")
        ghud.open_level(g, n, bn, "then", "L_LevelSelect", 3350, 4300)
        ghud.open_level(g, n, bn, "else", (nl, "NextLevel"), 3350, 4500)
        ghud.open_level(g, n, rc, "CastFailed", "L_LevelSelect", 3100, 4900)
    ghud.dispatch(g, n, click, [
        ("Resume", resume), ("Restart", restart),
        ("LevelSelect", lambda nd, p: ghud.open_level(g, n, nd, p, "L_LevelSelect", 1900, 4400)),
        ("Title", lambda nd, p: ghud.open_level(g, n, nd, p, "L_TitleScreen", 2300, 4400)),
        ("Next", next_level)], 300, 4000)
    BEL.compile_blueprint(hud)
    for nd in ed.list_nodes_with_errors(): log("ERROR", BEL.get_node_title(nd))
    for nd in ed.list_nodes_with_warnings(): log("WARN", BEL.get_node_title(nd))
    log("saved hud", EAL.save_asset(HUD, only_if_is_dirty=False))
    for gm in ("/Game/Car/Blueprints/BP_CarGameMode", "/Game/Car/Blueprints/BP_CarGameMode_Moon"):
        b = unreal.load_asset(gm)
        cdo = unreal.get_default_object(b.generated_class())
        cdo.set_editor_property("hud_class", hud.generated_class())
        BEL.compile_blueprint(b); EAL.save_asset(gm)
        log("hud set", gm, cdo.get_editor_property("hud_class"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_V2_HUD_DONE")
