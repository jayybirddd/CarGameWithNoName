# Helpers for placeholder menus drawn on a HUD canvas: dim background, title, and clickable buttons (HUD hit boxes).
# A button's hit-box name is what the HUD's ReceiveHitBoxClick event receives, so menus dispatch on that name.
import unreal
BEL = unreal.BlueprintEditorLibrary
BTN_W, BTN_H, BTN_GAP = 340, 58, 72

class Menu:
    def __init__(self, ed, g, n, draw_event, x, y):
        self.ed, self.g, self.n, self.ev = ed, g, n, draw_event
        self.x, self.y = x, y
        # canvas size is an int, so halve with integer division
        self.cx = n("Utilities|Operators|Divide", x, y); g.link(draw_event, "SizeX", self.cx, "A"); g.val(self.cx, "B", "2")
        self.cy = n("Utilities|Operators|Divide", x, y + 120); g.link(draw_event, "SizeY", self.cy, "A"); g.val(self.cy, "B", "2")

    def off(self, base, delta):
        self.y += 40
        a = self.n("Utilities|Operators|Add", self.x + 200, self.y); self.g.link(base, "ReturnValue", a, "A"); self.g.val(a, "B", str(int(delta)))
        return a

    def panel(self, prev, prev_pin, title, buttons, bg_alpha=0.7, title_color="(R=1.000000,G=1.000000,B=1.000000,A=1.000000)", note=None):
        """Draws a full-screen panel with a title and a column of buttons; returns the last exec node."""
        g, n = self.g, self.n
        bg = n("HUD|DrawRect", self.x + 400, self.y); g.exe(prev, prev_pin, bg)
        g.val(bg, "RectColor", "(R=0.010000,G=0.015000,B=0.030000,A=%f)" % bg_alpha)
        g.val(bg, "ScreenX", "0.0"); g.val(bg, "ScreenY", "0.0"); g.link(self.ev, "SizeX", bg, "ScreenW"); g.link(self.ev, "SizeY", bg, "ScreenH")
        t = n("HUD|DrawText", self.x + 600, self.y); g.exe(bg, "then", t)
        g.val(t, "Text", title); g.val(t, "TextColor", title_color); g.val(t, "Scale", "3.2")
        g.link(self.off(self.cx, -len(title) * 13), "ReturnValue", t, "ScreenX"); g.link(self.off(self.cy, -230), "ReturnValue", t, "ScreenY")
        cur = t
        if note:
            nt = n("HUD|DrawText", self.x + 700, self.y); g.exe(cur, "then", nt); cur = nt
            g.val(nt, "Text", note); g.val(nt, "TextColor", "(R=0.700000,G=0.750000,B=0.800000,A=1.000000)"); g.val(nt, "Scale", "1.2")
            g.link(self.off(self.cx, -len(note) * 4), "ReturnValue", nt, "ScreenX"); g.link(self.off(self.cy, -160), "ReturnValue", nt, "ScreenY")
        for i, (name, label) in enumerate(buttons):
            top = -110 + i * BTN_GAP
            rx = self.off(self.cx, -BTN_W // 2); ry = self.off(self.cy, top)
            r = n("HUD|DrawRect", self.x + 800 + i * 400, self.y); g.exe(cur, "then", r)
            g.val(r, "RectColor", "(R=0.080000,G=0.380000,B=0.750000,A=0.950000)")
            g.link(rx, "ReturnValue", r, "ScreenX"); g.link(ry, "ReturnValue", r, "ScreenY"); g.val(r, "ScreenW", str(BTN_W)); g.val(r, "ScreenH", str(BTN_H))
            tx = n("HUD|DrawText", self.x + 900 + i * 400, self.y); g.exe(r, "then", tx)
            g.val(tx, "Text", label); g.val(tx, "TextColor", "(R=1.000000,G=1.000000,B=1.000000,A=1.000000)"); g.val(tx, "Scale", "1.7")
            g.link(self.off(self.cx, -BTN_W // 2 + 24), "ReturnValue", tx, "ScreenX"); g.link(self.off(self.cy, top + 14), "ReturnValue", tx, "ScreenY")
            pos = n("Math|Vector2D|MakeVector2D", self.x + 1000 + i * 400, self.y + 200); g.link(rx, "ReturnValue", pos, "X"); g.link(ry, "ReturnValue", pos, "Y")
            hb = n("HUD|AddHitBox", self.x + 1000 + i * 400, self.y); g.exe(tx, "then", hb)
            g.link(pos, "ReturnValue", hb, "Position"); g.val(hb, "Size", "(X=%f,Y=%f)" % (BTN_W, BTN_H)); g.val(hb, "InName", name)
            g.val(hb, "bConsumesInput", "true")
            cur = hb
        self.x += 2400
        return cur

CLICK_EVENT = ["AddEvent|EventHitBoxClicked"]          # AHUD::ReceiveHitBoxClick shows up as "Event HitBoxClicked"
STRING_EQUALS = ["Utilities|String|EqualExactly(String)"]
TO_NAME = ["Utilities|String|StringToName", "Utilities|String|StringtoName"]

def name_equals(g, n, name_pin, literal, x, y):
    """Name == literal, done as an exact string compare (the wildcard Equal node resolves to the wrong type here)."""
    ts = n(["Utilities|String|ToString(Name)", "Utilities|String|ToString(name)"], x, y); g.link(name_pin[0], name_pin[1], ts, "InName")
    eq = n(STRING_EQUALS, x + 150, y); g.link(ts, "ReturnValue", eq, "A"); g.val(eq, "B", literal)
    return eq

def dispatch(g, n, click_event, cases, x, y):
    """click_event: ReceiveHitBoxClick. cases: [(box name, fn(node, pin) wiring the action)]. Returns the final else (node, pin)."""
    prev, pin = click_event, "then"
    for i, (name, action) in enumerate(cases):
        eq = name_equals(g, n, (click_event, "BoxName"), name, x + i * 500, y + 200)
        br = n("Utilities|FlowControl|Branch", x + i * 500, y); g.exe(prev, pin, br); g.link(eq, "ReturnValue", br, "Condition")
        action(br, "then")
        prev, pin = br, "else"
    return prev, pin

def open_level(g, n, prev, pin, level, x, y):
    """OpenLevel by name; `level` is a literal level name or a (node, pin) supplying a Name."""
    opl = n(["Game|OpenLevel(byName)", "Game|OpenLevel"], x, y); g.exe(prev, pin, opl)
    if isinstance(level, str): g.val(opl, "LevelName", level)
    else: g.link(level[0], level[1], opl, "LevelName")
    return opl
