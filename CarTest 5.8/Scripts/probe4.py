import unreal, re
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe4.txt"
L = []
car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
g = unreal.BlueprintEditorLibrary.find_event_graph(car)
ed = unreal.BlueprintGraphEditor.get_graph_editor(g)
names = list(ed.list_available_nodes([]))
L.append("total %d" % len(names))
pat = re.compile(r"(IA_|Mapping Context|Enhanced Input Local|Get Controller|Cast To PlayerController|BeginPlay|Event Tick|Print String|Add Local Rotation|Set Relative Rotation|FInterp|Forward Speed|Set Throttle|Set Steering|Set Brake|Set Handbrake|Set Actor Location And|Physics Linear|Physics Angular|Make Rotator|Break Rotator|Get Actor Rotation|Get Actor Location|Set Active|Select Float|Make Literal|Format Text|Current Gear|Teleport|Delta Seconds|Get World Delta|Sequence|Flip Flop|Branch|Clamp|Abs|Multiply|Map Range)", re.I)
for n in names:
    if pat.search(n): L.append(n)
for n in ed.list_all_nodes():
    L.append("existing: %s %s" % (n.get_class().get_name(), unreal.BlueprintEditorLibrary.get_node_title(n)))
with open(OUT, "w") as f: f.write("\n".join(L))
