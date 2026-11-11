import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_find_types.txt"
L = []
try:
    for nm in dir(unreal):
        low = nm.lower()
        if any(k in low for k in ("animdynamic", "springcontroller", "animgraphnode_spring", "niagara", "modifybone", "graphnode_transformbone")):
            L.append(nm)
    for c in ("BlueprintGraphEditor", "BlueprintEditorLibrary", "ChaosWheeledVehicleMovementComponent", "MaterialEditingLibrary"):
        if hasattr(unreal, c):
            L.append(c + " api: " + ", ".join(x for x in dir(getattr(unreal, c)) if not x.startswith("_")))
        else:
            L.append(c + " MISSING")
except Exception:
    L.append(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
unreal.log("CLAUDE_FIND_TYPES_DONE")
