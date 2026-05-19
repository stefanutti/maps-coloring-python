from __future__ import annotations
import math
import numpy as np
import pyvista as pv
from sphere.spherical_map import SphericalMap, slerp, geodesic_samples, split_face

_N_PICK_SAMPLES = 20
_PICK_THRESHOLD_PX = 14


def _dist_point_segment_2d(
    pt: tuple[float, float],
    a:  tuple[float, float],
    b:  tuple[float, float],
) -> tuple[float, float]:
    """Returns (distance, t) where t in [0,1] is the parameter along a->b."""
    ax, ay = pt[0] - a[0], pt[1] - a[1]
    bx, by = b[0] - a[0], b[1] - a[1]
    denom = bx * bx + by * by
    if denom < 1e-12:
        return math.hypot(ax, ay), 0.0
    t = max(0.0, min(1.0, (ax * bx + ay * by) / denom))
    rx, ry = ax - t * bx, ay - t * by
    return math.hypot(rx, ry), t


class InteractionController:
    IDLE           = "IDLE"
    FIRST_SELECTED = "FIRST_SELECTED"
    WAYPOINT_MODE  = "WAYPOINT_MODE"

    def __init__(self, smap: SphericalMap, renderer):
        self.smap     = smap
        self.renderer = renderer
        self.state    = self.IDLE

        self._state_p        : int | None   = None   # eid1
        self._state_t1       : float        = 0.0
        self._state_q        : int | None   = None   # eid2
        self._state_t2       : float        = 0.0
        self._state_waypoints: list[np.ndarray] = []
        self._state_fid      : int | None   = None

        self._hovered_eid    : int | None         = None
        self._hovered_t      : float | None       = None
        self._snap_pos       : np.ndarray | None  = None

        self._screen_cache   : dict[int, list[tuple[float, float]]] = {}
        self._cache_dirty    : bool = True

        self._register_callbacks()

    def _register_callbacks(self) -> None:
        plotter = self.renderer.plotter
        plotter.track_mouse_position()
        plotter.add_observer("MouseMoveEvent",       self._on_mouse_move)
        plotter.add_observer("LeftButtonPressEvent", self._on_left_click)
        plotter.add_key_event("Return",    self._on_confirm)
        plotter.add_key_event("space",     self._on_confirm)
        plotter.add_key_event("Escape",    self._on_escape)
        plotter.add_key_event("BackSpace", self._on_backspace)
        plotter.add_observer("EndInteractionEvent", self._on_camera_moved)

    def _on_camera_moved(self, *_) -> None:
        self._cache_dirty = True

    def _rebuild_screen_cache(self) -> None:
        renderer = self.renderer.plotter.renderer
        h = self.renderer.plotter.window_size[1]

        def world_to_screen(pt3d: np.ndarray) -> tuple[float, float]:
            x, y, _ = renderer.world_to_display(pt3d[0], pt3d[1], pt3d[2])
            return float(x), float(h - y)

        self._screen_cache = {}
        for eid, edge in self.smap.edges.items():
            chain = (
                [self.smap.vertices[edge.v_start]]
                + list(edge.waypoints)
                + [self.smap.vertices[edge.v_end]]
            )
            pts3d = []
            for i in range(len(chain) - 1):
                seg = geodesic_samples(chain[i], chain[i + 1], n=_N_PICK_SAMPLES)
                pts3d.extend(seg if i == 0 else seg[1:])
            self._screen_cache[eid] = [world_to_screen(p) for p in pts3d]
        self._cache_dirty = False

    def _find_edge_at_cursor(self, mx: float, my: float) -> tuple[int | None, float | None]:
        if self._cache_dirty:
            self._rebuild_screen_cache()
        best_eid, best_t, best_dist = None, None, math.inf
        for eid, screen_pts in self._screen_cache.items():
            n = len(screen_pts)
            for i in range(n - 1):
                d, t_local = _dist_point_segment_2d(
                    (mx, my), screen_pts[i], screen_pts[i + 1]
                )
                if d < best_dist:
                    best_dist = d
                    best_eid  = eid
                    best_t    = (i + t_local) / (n - 1)
        return (best_eid, best_t) if best_dist < _PICK_THRESHOLD_PX else (None, None)

    def _snap_pos_on_edge(self, eid: int, t: float) -> np.ndarray:
        e = self.smap.edges[eid]
        return slerp(self.smap.vertices[e.v_start], self.smap.vertices[e.v_end], t)

    def _face_of_edge(self, eid: int) -> int | None:
        for fid, signed_eids in self.smap.faces.items():
            if any(abs(s) == eid for s in signed_eids):
                return fid
        return None

    def _on_mouse_move(self, *_) -> None:
        mx, my = self.renderer.plotter.mouse_position
        eid, t = self._find_edge_at_cursor(mx, my)
        prev_hovered = self._hovered_eid
        prev_snap    = self._snap_pos

        if eid != prev_hovered:
            self.renderer.highlight_edge(eid, prev_hovered)
            self._hovered_eid = eid
            self._hovered_t   = t

        if eid is not None:
            new_snap = self._snap_pos_on_edge(eid, t)
            self.renderer.show_snap_vertex(new_snap, prev_snap)
            self._snap_pos = new_snap
        else:
            self.renderer.show_snap_vertex(None, prev_snap)
            self._snap_pos = None

        self.renderer.plotter.render()

    def _on_left_click(self, *_) -> None:
        if self._hovered_eid is None:
            if self.state == self.WAYPOINT_MODE:
                # pick_mouse_position() ray-casts to the sphere surface; mouse_position returns 2D pixels
                picked = self.renderer.plotter.pick_mouse_position()
                if picked is not None:
                    pt = np.array(picked, dtype=float)
                    norm = np.linalg.norm(pt)
                    if norm > 1e-9:
                        self._state_waypoints.append(pt / norm)
                        self._update_hud()
            return

        eid = self._hovered_eid
        t   = self._hovered_t

        if self.state == self.IDLE:
            fid = self._face_of_edge(eid)
            self._state_fid = fid
            self._state_p   = eid
            self._state_t1  = t
            self.state = self.FIRST_SELECTED
            self._update_hud()

        elif self.state == self.FIRST_SELECTED:
            if not any(abs(s) == eid for s in self.smap.faces[self._state_fid]):
                self._update_hud(extra="[edge belongs to different face — pick an edge of the same face]")
                return
            self._state_q  = eid
            self._state_t2 = t
            self.state = self.WAYPOINT_MODE
            self._update_hud()

    def _on_confirm(self, *_) -> None:
        if self.state != self.WAYPOINT_MODE:
            return
        fid  = self._state_fid
        eid1 = self._state_p
        t1   = self._state_t1
        eid2 = self._state_q
        t2   = self._state_t2
        wps  = self._state_waypoints if self._state_waypoints else None

        old_eids = set(self.smap.edges.keys())
        old_vids = set(self.smap.vertices.keys())

        fid1, fid2 = split_face(self.smap, fid, eid1, t1, eid2, t2, wps)

        new_eids     = list(set(self.smap.edges.keys()) - old_eids)
        new_vids     = list(set(self.smap.vertices.keys()) - old_vids)
        removed_eids = list(old_eids - set(self.smap.edges.keys()))

        self.renderer.update_after_split(
            self.smap, fid1, fid2,
            removed_fid=fid,
            removed_eids=removed_eids,
            new_eids=new_eids,
            new_vids=new_vids,
        )
        self._cache_dirty = True
        self._reset_state()

    def _on_escape(self, *_) -> None:
        self._reset_state()

    def _on_backspace(self, *_) -> None:
        if self.state == self.WAYPOINT_MODE and self._state_waypoints:
            self._state_waypoints.pop()
            self._update_hud()

    def _reset_state(self) -> None:
        self.state = self.IDLE
        self._state_p = self._state_q = self._state_fid = None
        self._state_t1 = self._state_t2 = 0.0
        self._state_waypoints = []
        self._update_hud()

    def _update_hud(self, extra: str = "") -> None:
        if self.state == self.IDLE:
            hints = "[click edge] select p"
        elif self.state == self.FIRST_SELECTED:
            hints = "[click edge same face] select q  ·  [Esc] cancel"
        else:
            wn = len(self._state_waypoints)
            hints = (
                f"[click face] add waypoint ({wn})  ·  "
                f"[Enter] confirm  ·  [Bksp] undo  ·  [Esc] cancel"
            )
        self.renderer.update_hud(self.state, extra or hints)
