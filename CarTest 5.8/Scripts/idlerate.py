import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_idlerate.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
BEL = unreal.BlueprintEditorLibrary
try:
    abp = unreal.load_asset("/Game/Car/Blueprints/ABP_CarBody")
    ag = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, "AnimGraph")
    for n in ag.list_all_nodes():
        t = str(BEL.get_node_title(n))
        if "AS_Idle" in t:
            st = n.get_editor_property("node")
            before = st.export_text()
            log("before", before[:400])
            try:
                st.set_editor_property("play_rate", 0.7)
            except Exception as e:
                log("set_editor_property failed", e, "-> import_text", st.import_text("(PlayRate=0.700000)"))
            n.set_editor_property("node", st)
            log("after", n.get_editor_property("node").export_text()[:400])
            log("pos", n.get_editor_property("node_pos_x") if False else "")
    BEL.compile_blueprint(abp)
    unreal.EditorAssetLibrary.save_asset("/Game/Car/Blueprints/ABP_CarBody")
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([abp])
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
