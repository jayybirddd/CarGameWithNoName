# Lists the open map's actors with bounds, and the collision settings of the boost pad's components.
import unreal, traceback
OUT = "D:/PersonalGameFiles/CarTest 5.8/Saved/claude_v3_probe_track.txt"
L = []
def log(*a): L.append(" ".join(str(x) for x in a))
try:
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        o, e = a.get_actor_bounds(False)
        log(a.get_actor_label(), a.get_class().get_name(), "center (%.0f,%.0f,%.0f) ext (%.0f,%.0f,%.0f)" % (o.x, o.y, o.z, e.x, e.y, e.z))
        if a.get_actor_label() == "BoostPad_0":
            for c in a.get_components_by_class(unreal.PrimitiveComponent):
                log("   comp", c.get_name(), c.get_collision_profile_name(), c.get_collision_enabled(), "overlap", c.get_editor_property("generate_overlap_events"))
except Exception:
    log(traceback.format_exc())
with open(OUT, "w") as f: f.write("\n".join(L))
