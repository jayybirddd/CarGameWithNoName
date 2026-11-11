import unreal, traceback, re
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_abp1.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
try:
    path = "/Game/Car/Blueprints/ABP_CarBody"
    if not EAL.does_asset_exist(path):
        f = unreal.AnimBlueprintFactory()
        f.set_editor_property("target_skeleton", unreal.load_asset("/Game/Car/Mesh/SK_Car_Skeleton"))
        f.set_editor_property("parent_class", unreal.VehicleAnimationInstance)
        try: f.set_editor_property("preview_skeletal_mesh", unreal.load_asset("/Game/Car/Mesh/SK_Car"))
        except Exception as e: log("preview err", e)
        abp = AT.create_asset("ABP_CarBody", "/Game/Car/Blueprints", unreal.AnimBlueprint, f)
    abp = unreal.load_asset(path)
    log("abp", abp, "parent", BEL.get_blueprint_parent_class(abp) if hasattr(BEL, "get_blueprint_parent_class") else "?")
    log("graphs", [str(g.get_name()) for g in BEL.list_graphs(abp)])
    for gname in ["AnimGraph", "EventGraph"]:
        try:
            ed = unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp, gname)
            names = list(ed.list_available_nodes([]))
            log("##", gname, len(names))
            pat = re.compile(r"(Sequence|Blend|Additive|Wheel|Vehicle|State|Slot|Layered|Evaluator|Pose|Update|TryGetPawnOwner|OwningActor|Getcomponentbyclass|GetSteering|GetThrottle|GetBrake|ForwardSpeed|FInterpTo|Clamp|Absolute|SelectInt|SelectFloat|Max\(|Min\(|Greater|Less|Multiply|Divide|BooleanAND|ANDBoolean|NOTBoolean)", re.I)
            for n in names:
                if gname == "AnimGraph" or pat.search(n):
                    if not re.search(r"(Rig|Niagara|Material|PCG|Chooser|MovieScene|Water|Audio|Metasound|Widget|Optimus|Dataflow|Struct\|)", n):
                        log(n)
            for nd in ed.list_all_nodes():
                log("existing", nd.get_class().get_name(), BEL.get_node_title(nd))
        except Exception:
            log(traceback.format_exc())
except Exception:
    log(traceback.format_exc())
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L))
unreal.log("CLAUDE_ABP1_DONE")
