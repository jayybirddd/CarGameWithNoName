import unreal
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe5.txt"
car = unreal.load_asset("/Game/Car/Blueprints/BP_CarPawn")
g = unreal.BlueprintEditorLibrary.find_event_graph(car)
ed = unreal.BlueprintGraphEditor.get_graph_editor(g)
names = list(ed.list_available_nodes([]))
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(names))
