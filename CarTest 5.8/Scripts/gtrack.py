# Track helpers: follow a road mesh's centreline with traces (editor or game world) and return points with heading
# and road width. Used to measure tracks and to lay out race gates.
# A "crossing" runs from a road point both ways along a direction until the surface stops or jumps by more than DZ
# between samples (a wall or edge); the shortest crossing over several directions is straight across the road.
import unreal, math, random
STEP = 400.0          # cm between centreline samples
SCAN = 80.0           # cm between samples along a crossing
DZ = 110.0            # max height change between neighbouring crossing samples (~54 deg) before it counts as the edge

def _hits(w, actor, x, y, z0, z1):
    r = unreal.SystemLibrary.line_trace_multi(w, unreal.Vector(x, y, z0), unreal.Vector(x, y, z1), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if isinstance(r, tuple): r = r[-1] if isinstance(r[-1], list) else r[0]
    return [h.to_tuple()[4].z for h in (r or []) if h.to_tuple()[9] == actor]

def road_z(w, actor, x, y, zref, reach=600.0):
    """Road height at (x, y) nearest to zref (within reach), or None."""
    zs = _hits(w, actor, x, y, zref + reach, zref - reach)
    return min(zs, key=lambda z: abs(z - zref)) if zs else None

def _half(w, actor, x, y, z, ang, sgn, cap=6000.0):
    d, zp = 0.0, z
    ca, sa = math.cos(ang) * sgn, math.sin(ang) * sgn
    while d < cap:
        q = road_z(w, actor, x + ca * (d + SCAN), y + sa * (d + SCAN), zp, 250.0)
        if q is None or abs(q - zp) > DZ: break
        d += SCAN; zp = q
    return d

def crossing(w, actor, x, y, z, angles):
    """Shortest crossing through (x, y, z) among `angles` (radians): (width, angle, mid_x, mid_y)."""
    best = None
    for a in angles:
        l, r = _half(w, actor, x, y, z, a, -1), _half(w, actor, x, y, z, a, 1)
        if best is None or l + r < best[0]:
            off = (r - l) / 2.0
            best = (l + r, a, x + math.cos(a) * off, y + math.sin(a) * off)
    return best

def find_start(w, actor, seed=7, log=None):
    """A centred road point on a typical-width stretch, and the heading along the road there."""
    o, e = actor.get_actor_bounds(False)
    rnd = random.Random(seed)
    samples = []
    tries = 0
    while len(samples) < 24 and tries < 4000:
        tries += 1
        x, y = o.x + rnd.uniform(-e.x, e.x), o.y + rnd.uniform(-e.y, e.y)
        zs = _hits(w, actor, x, y, o.z + e.z + 500, o.z - e.z - 500)
        if not zs: continue
        z = max(zs)
        c = crossing(w, actor, x, y, z, [math.radians(k * 15) for k in range(12)])
        if c[0] >= 300: samples.append((c, z))
    widths = sorted(s[0][0] for s in samples)
    med = widths[len(widths) // 2]
    c, z = min(samples, key=lambda s: abs(s[0][0] - med))
    mz = road_z(w, actor, c[2], c[3], z, 300.0) or z
    hdg = c[1] + math.pi / 2
    if log: log("start: median width %.0f, picked width %.0f at (%.0f, %.0f, %.0f)" % (med, c[0], c[2], c[3], mz))
    return unreal.Vector(c[2], c[3], mz), math.cos(hdg), math.sin(hdg), med

def walk(w, actor, p, hx, hy, max_steps=6000, log=None):
    """Follows the road centreline from p along (hx, hy). Returns ([(x, y, z, hx, hy, width)], lap length, closed)."""
    pts = []
    x, y, z = p.x, p.y, p.z
    travelled = 0.0
    for it in range(max_steps):
        perp = math.atan2(hy, hx) + math.pi / 2
        c = crossing(w, actor, x, y, z, [perp + math.radians(d) for d in (-30, -20, -10, 0, 10, 20, 30)])
        x, y = c[2], c[3]
        z = road_z(w, actor, x, y, z, 300.0) or z
        nh = c[1] - math.pi / 2
        nhx, nhy = math.cos(nh), math.sin(nh)
        if nhx * hx + nhy * hy < 0: nhx, nhy = -nhx, -nhy      # keep going the same way
        hx, hy = hx * 0.5 + nhx * 0.5, hy * 0.5 + nhy * 0.5
        n = math.hypot(hx, hy); hx, hy = hx / n, hy / n
        pts.append((x, y, z, hx, hy, c[0]))
        nxt = None
        for da in (0, 6, -6, 12, -12, 20, -20, 30, -30, 45, -45):
            a = math.atan2(hy, hx) + math.radians(da)
            cx, cy = x + math.cos(a) * STEP, y + math.sin(a) * STEP
            q = road_z(w, actor, cx, cy, z, STEP * 1.2)
            if q is not None:
                nxt = (cx, cy, q); break
        if nxt is None:
            if log: log("walk: lost the road at step", it, "(%.0f, %.0f, %.0f)" % (x, y, z))
            return pts, travelled, False
        travelled += math.hypot(nxt[0] - x, nxt[1] - y)
        x, y, z = nxt
        if travelled > STEP * 40 and math.hypot(x - p.x, y - p.y) < STEP * 1.6 and abs(z - p.z) < 400:
            return pts, travelled, True
    return pts, travelled, False
