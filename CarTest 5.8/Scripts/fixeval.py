import unreal, traceback, sys, importlib
sys.path.append("D:/PersonalGameFiles/CarTest/Scripts")
import ghy as gh; importlib.reload(gh)
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_fixeval.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
try:
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    g = gh.G(ag, log)
    for n in ag.list_all_nodes():
        t = str(BEL.get_node_title(n))
        if "Evaluator" in t or "Evaluate" in t or n.get_class().get_name() == "AnimGraphNode_SequenceEvaluator":
            g.dump(n)
            ok = g.val(n, "ExplicitTime", "1.0")
            log("set explicit time", t, ok)
            try:
                st = n.get_editor_property("node"); log("node seq", st.get_editor_property("sequence"))
            except Exception as e: log("err", e)
    BEL.compile_blueprint(abp)
    unreal.EditorAssetLibrary.save_asset("/Game/Car/Blueprints/ABP_CarBody")
    for nm in ("AS_TurnLeft_Add", "AS_TurnRight_Add"):
        a = unreal.load_asset("/Game/Car/Animations/" + nm)
        log(nm, a.get_editor_property("additive_anim_type"), a.get_editor_property("ref_pose_type"), a.get_editor_property("ref_frame_index"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
