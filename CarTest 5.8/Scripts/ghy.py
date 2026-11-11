# graph helper used by the build scripts
import unreal
BEL = unreal.BlueprintEditorLibrary
PL = unreal.BlueprintGraphPinLibrary
class G:
    def __init__(self, ed, log):
        self.ed, self.log = ed, log
    def n(self, name, x, y):
        node = self.ed.create_node_from_name(name, unreal.Vector2D(x, y), [])
        if node is None: self.log("!! node failed", name)
        return node
    def var_get(self, nm, x, y):
        node = self.ed.add_get_member_variable_node(nm)
        if node is not None:
            try: node.set_node_pos(unreal.IntPoint(int(x), int(y)))
            except Exception: pass
        if node is None: self.log("!! get var failed", nm)
        return node
    def var_set(self, nm, x, y):
        node = self.ed.add_set_member_variable_node(nm)
        if node is None: self.log("!! set var failed", nm)
        else:
            try: node.set_node_pos(unreal.IntPoint(int(x), int(y)))
            except Exception: pass
        return node
    @staticmethod
    def norm(s):
        s = str(s).replace(" ", "").lower()
        return s
    def pins(self, node):
        return list(BEL.list_all_pins(node)) if node else []
    def pin(self, node, name, direction=None):
        if node is None: return None
        want = self.norm(name)
        cands = []
        for p in self.pins(node):
            pn = self.norm(PL.get_pin_name(p))
            d = PL.get_pin_direction(p)
            if direction == "in" and d != unreal.EdGraphPinDirection.EGPD_INPUT: continue
            if direction == "out" and d != unreal.EdGraphPinDirection.EGPD_OUTPUT: continue
            if pn == want or pn == "b" + want or pn.lstrip("b") == want.lstrip("b"):
                cands.append(p)
        if not cands:
            self.log("!! pin not found", name, "on", BEL.get_node_title(node), [str(PL.get_pin_name(p)) for p in self.pins(node)])
            return None
        return cands[0]
    def link(self, a, an, b, bn):
        pa = self.pin(a, an, "out"); pb = self.pin(b, bn, "in")
        if pa is None or pb is None: return False
        ok = PL.try_create_connection(pa, pb)
        if not ok: self.log("!! link failed", BEL.get_node_title(a), an, "->", BEL.get_node_title(b), bn)
        return ok
    def exe(self, a, an, b, bn="execute"):
        return self.link(a, an, b, bn)
    def val(self, node, pn, v):
        p = self.pin(node, pn, "in")
        if p is None: return False
        ok = PL.set_pin_value(p, str(v))
        if not ok: self.log("!! set value failed", BEL.get_node_title(node), pn, v)
        return ok
    def dump(self, node):
        if node is None: return
        self.log("  pins of", BEL.get_node_title(node), [(str(PL.get_pin_name(p)), "in" if PL.get_pin_direction(p) == unreal.EdGraphPinDirection.EGPD_INPUT else "out") for p in self.pins(node)])
