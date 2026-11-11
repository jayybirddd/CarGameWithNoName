import unreal
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v2_doc.txt"
G = unreal.BlueprintGraphEditor
with open(OUT, "w") as f:
    for nm in ("add_call_function_node", "create_node_from_name", "retarget_node_class", "list_nodes_of_class"):
        f.write("== %s\n%s\n" % (nm, getattr(G, nm).__doc__))
