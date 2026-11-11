import unreal
OUT = "D:/PersonalGameFiles/CarTest/Saved/claude_probe6.txt"
L = []
c = unreal.SkeletonModifier
for x in dir(c):
    if not x.startswith("_") and x not in dir(unreal.Object):
        L.append(x + ": " + (getattr(c, x).__doc__ or "").replace("\n", " ")[:400])
c = unreal.AnimationDataController
for x in ["set_bone_track_keys", "update_bone_track_keys", "add_bone_curve", "set_frame_rate"]:
    if hasattr(c, x): L.append("ADC." + x + ": " + (getattr(c, x).__doc__ or "").replace("\n", " ")[:500])
m = [x for x in dir(unreal.AnimDataModel) if not x.startswith("_")] if hasattr(unreal, "AnimDataModel") else []
L.append("ADM: " + " ".join(m))
with open(OUT, "w") as f: f.write("\n".join(L))
