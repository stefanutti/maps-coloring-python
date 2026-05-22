# Sphere Map Explorer — Regeneration Prompt

Build a Python desktop application called "Sphere Map Explorer" using PyVista.

## What it does

An interactive tool for building a planar map on a sphere by progressively splitting
regions. The user draws new edges on the sphere to divide existing faces into two.
The underlying data model is a 3-regular planar graph embedded on the unit sphere.

## Initial state

Start with 2 vertices (north pole [0,0,1] and south pole [0,0,-1]) connected by
3 parallel edges, each passing through one of the three equatorial waypoints:

    eq0 = [1, 0, 0]
    eq1 = [-0.5, sqrt(3)/2, 0]
    eq2 = [-0.5, -sqrt(3)/2, 0]

This gives 4 faces: 3 "lune" regions + 1 implicit ocean.

## Data model

- `SphericalMap`: holds:
  - `vertices: dict[int, np.ndarray]` — unit-sphere 3D positions
  - `edges: dict[int, Edge]`
  - `faces: dict[int, list[int]]` — signed edge id lists
  - `colors: dict[int, str]` — unused for rendering but kept for future use
  - `next_vid`, `next_eid` (starts at 1, eid 0 is reserved), `next_fid` — id counters

- `Edge`: dataclass with `v_start: int`, `v_end: int`, `waypoints: list[np.ndarray]`.
  Waypoints are unit-sphere points along the arc between the two endpoint vertices.

- Face boundary: ordered list of signed edge ids. `+eid` = forward traversal (v_start
  to v_end), `-eid` = reversed (v_end to v_start). Each undirected edge appears in
  exactly two face boundaries, once per direction.

- All curves are geodesic arcs (great-circle segments), computed with spherical linear
  interpolation (slerp) between consecutive chain points (v_start → waypoints → v_end).
  Handle nearly-antipodal vectors with Rodrigues rotation to avoid division by sin(0).

## Geometry utilities

```python
def normalize(v): return v / np.linalg.norm(v)

def slerp(a, b, t):
    # standard slerp; handle dot > 0.9999 (nearly equal) and dot < -0.9999 (antipodal)

def geodesic_samples(a, b, n=30):
    return [slerp(a, b, i / (n-1)) for i in range(n)]

def _eval_edge_at_t(smap, eid, t):
    # t in [0,1] along full chain v_start -> waypoints -> v_end
    # split t into segment index + local t, then slerp within that segment
```

## Rendering (PyVista)

- Dark background `#1a1a2e`.
- A faint white wireframe unit sphere (`radius=1.0`, `theta_resolution=36`,
  `phi_resolution=36`, `style="wireframe"`, `color="#ffffff"`, `opacity=0.12`,
  `line_width=0.6`) as a reference backdrop, added first so it renders behind everything.
- Edges rendered as white tubes (`radius=0.004`), sampled as geodesic polylines
  (`n=30` samples per segment), converted to splines then `.tube()`.
  Skip zero-length tubes (degenerate edges after a split).
- Vertices rendered as white spheres (`radius=0.012`).
- **No face coloring** — faces are invisible; only edges, vertices, and the wireframe
  sphere are shown.
- HUD: top-left shows current mode + hint text (green, font_size=10, name="hud_mode");
  top-right shows "V:N  E:N  F:N" (lightblue, font_size=10, name="hud_stats").

## Interaction

### Snap vertex (hover preview)

On mouse move, find the closest edge to the cursor in 2D screen space and show a small
white sphere (`radius=0.014`, name="snap_vertex") at the corresponding 3D point on the
edge, computed via `_eval_edge_at_t` (not a naive slerp between endpoints).

**Screen-space edge cache:**
Project each edge's 3D sample points to 2D display coordinates using VTK's coordinate
transform:

```python
renderer.SetWorldPoint(x, y, z, 1.0)
renderer.WorldToDisplay()
px, py, _ = renderer.GetDisplayPoint()
```

Use **VTK display coordinates throughout** (origin at bottom-left, y increases upward).
Do NOT flip the y axis. `plotter.mouse_position` also uses VTK display coordinates, so
both are consistent for distance comparisons.

Rebuild this cache when the camera moves (mark dirty on `EndInteractionEvent`).
Find the nearest edge segment within **14 pixels** of the cursor.

### State machine

**IDLE**
- Hover shows white snap vertex.
- Left click on an edge → select point p (edge id + parameter t1).
- Show a **green** sphere (`radius=0.020`, name="select_p") at p's 3D position.
- Transition to FIRST_SELECTED.

**FIRST_SELECTED**
- Hover still shows snap vertex.
- Left click on an edge of the **same face** → select point q (edge id + t2).
- If the clicked edge belongs to a different face, show an error hint and stay in state.
- Show an **orange** sphere (`radius=0.020`, name="select_q") at q's 3D position.
- Transition to WAYPOINT_MODE.

**WAYPOINT_MODE**
- Left click on the sphere surface (not near an edge) → ray-cast to sphere surface
  via `plotter.pick_mouse_position()`, normalize the result, append to waypoints list.
- `BackSpace` → remove last waypoint.
- `Enter` or `Space` → confirm split (see Face split logic below).
- `Escape` → cancel, return to IDLE, remove green/orange markers.

**Reset (Escape or after confirmed split):**
Clear state, remove "select_p" and "select_q" actors, return to IDLE.

### Key events

Register with `plotter.add_key_event(key, callback)`. PyVista requires callbacks with
**no required arguments** (no `*args`). Use plain `def callback(self) -> None:`.

Keys: `"Return"`, `"space"` → confirm; `"Escape"` → cancel; `"BackSpace"` → undo waypoint.

### Mouse events

Register with `plotter.iren.add_observer(event_name, callback)`. These callbacks
**do** receive VTK arguments, so use `def callback(self, *_) -> None:`.

Events: `"MouseMoveEvent"`, `"LeftButtonPressEvent"`, `"EndInteractionEvent"`.

Also call `plotter.track_mouse_position()` before registering observers.

## Face split logic

Given face `fid`, edge `eid1` at parameter `t1` (point p) and edge `eid2` at parameter
`t2` (point q):

1. **Insert vertex p** on `eid1`: split into sub-edges `e1a` (v_start→p) and `e1b` (p→v_end),
   distributing existing waypoints to the correct sub-edge. Delete `eid1`.

2. **Insert vertex q** on `eid2` (if `eid1 != eid2`): same process → `e2a`, `e2b`.
   If `eid1 == eid2` (same-edge split): insert both p and q (ensuring t1 < t2),
   producing three sub-edges `e1a`, `e1m`, `e1b`.

3. **Patch adjacent faces**: any face other than `fid` that references `eid1` or `eid2`
   gets those edges replaced with the corresponding sub-edges (preserving orientation).

4. **Arc edge**: create a new edge from p to q. If the user provided waypoints, use them.
   Otherwise auto-compute: push the midpoint of p–q toward the face centroid by a factor
   of 0.35, project to sphere.

5. **Rebuild face boundaries**: split `fid` into two new faces `F1` and `F2` using the
   arc and the existing boundary segments between p and q.

6. Return `(fid1, fid2)`.

### Waypoint splitting

When splitting edge waypoints at parameter `t_split`:

```
t_w = (i + 1) / (n_waypoints + 1)   # parameter of waypoint i in [0,1]
before: t_w < t_split
after:  t_w > t_split
# waypoints coinciding with t_split are dropped from both sub-edges
```

For same-edge split at t1 then t2: split at t1 first to get (before, rest), then
split rest at `(t2 - t1) / (1 - t1)` to get (mid, after).

## Renderer update after split

`update_after_split(smap, fid1, fid2, removed_fid, removed_eids, new_eids, new_vids)`:
- Remove actors for `removed_eids`.
- Add actors for `new_eids` and `new_vids`.
- `fid1`, `fid2`, `removed_fid` are unused (no face rendering).
- Update the HUD.
- Call `plotter.render()`.

## Auto-grow mode

```
python main.py --auto N [--strategy balanced|random]
```

Repeatedly call `split_face_auto` N times before entering interactive mode.
`balanced` strategy: pick the largest face, split at t=0.5 on two non-adjacent edges.
`random` strategy: random face, random edges, random t values in [0.2, 0.8].

## File structure

```
main.py            — argparse entry point; creates SphericalMap, SphereRenderer,
                     InteractionController; calls plotter.show()
spherical_map.py   — all data model, geometry, and split logic
renderer.py        — SphereRenderer: PyVista actor management, HUD, markers
interaction.py     — InteractionController: state machine, screen cache, callbacks
```

## Dependencies

```
pyvista
numpy
```

Python 3.10+ (uses `|` union types and `match` is not used).

## Coding style

- Linear control flow; avoid break/continue/early return except for simple guard clauses.
- No comments unless the why is non-obvious.
- No type stubs or docstrings needed.
