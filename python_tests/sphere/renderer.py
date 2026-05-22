from __future__ import annotations
import numpy as np
import pyvista as pv
from sphere.spherical_map import (
    SphericalMap, slerp, geodesic_samples, _face_vertex_positions,
)

_N_SAMPLES = 30   # points per geodesic segment


def _edge_polyline(smap: SphericalMap, eid: int) -> np.ndarray:
    """3D points along the full edge path (v_start + waypoints + v_end)."""
    e = smap.edges[eid]
    chain = [smap.vertices[e.v_start]] + list(e.waypoints) + [smap.vertices[e.v_end]]
    pts = []
    for i in range(len(chain) - 1):
        seg = geodesic_samples(chain[i], chain[i + 1], n=_N_SAMPLES)
        pts.extend(seg if i == 0 else seg[1:])
    return np.array(pts)


def _face_poly_data(smap: SphericalMap, fid: int) -> pv.PolyData:
    """PolyData mesh for a filled face (fan triangulation from centroid)."""
    boundary_pts: list[np.ndarray] = []
    for signed_eid in smap.faces[fid]:
        eid = abs(signed_eid)
        e = smap.edges[eid]
        chain = [smap.vertices[e.v_start]] + list(e.waypoints) + [smap.vertices[e.v_end]]
        if signed_eid < 0:
            chain = list(reversed(chain))
        seg_pts = []
        for i in range(len(chain) - 1):
            seg = geodesic_samples(chain[i], chain[i + 1], n=_N_SAMPLES)
            seg_pts.extend(seg if i == 0 else seg[1:])
        boundary_pts.extend(seg_pts[:-1])   # avoid duplicate at junction

    pts_arr = np.array(boundary_pts)
    c = pts_arr.mean(axis=0)
    c = c / np.linalg.norm(c)   # project centroid to sphere
    n = len(boundary_pts)
    all_pts = np.vstack([pts_arr, c.reshape(1, 3)])
    c_idx = n
    faces_conn = []
    for i in range(n):
        faces_conn += [3, c_idx, i, (i + 1) % n]
    return pv.PolyData(all_pts, np.array(faces_conn))


def _edge_mesh(smap: SphericalMap, eid: int) -> pv.PolyData:
    pts = _edge_polyline(smap, eid)
    return pv.Spline(pts, n_points=len(pts))


class SphereRenderer:
    def __init__(self, smap: SphericalMap):
        self.smap = smap
        self.plotter = pv.Plotter()
        self.plotter.set_background("#1a1a2e")

        self._face_actors:   dict[int, pv.Actor] = {}
        self._edge_actors:   dict[int, pv.Actor] = {}
        self._vertex_actors: dict[int, pv.Actor] = {}

        self._build_all(smap)
        self._update_hud()

    def _build_all(self, smap: SphericalMap) -> None:
        self._add_sphere_shell()
        for eid in smap.edges:
            self._add_edge_actor(eid)
        for vid in smap.vertices:
            self._add_vertex_actor(vid)

    def _add_sphere_shell(self) -> None:
        shell = pv.Sphere(radius=1.0, theta_resolution=36, phi_resolution=36)
        self.plotter.add_mesh(
            shell, style="wireframe", color="#ffffff", opacity=0.12,
            line_width=0.6, name="sphere_shell",
        )

    def _add_face_actor(self, fid: int) -> None:
        mesh = _face_poly_data(self.smap, fid)
        color = self.smap.colors[fid]
        actor = self.plotter.add_mesh(
            mesh, color=color, opacity=0.75,
            show_edges=False, name=f"face_{fid}",
        )
        self._face_actors[fid] = actor

    def _add_edge_actor(self, eid: int, color: str = "white") -> None:
        mesh = _edge_mesh(self.smap, eid)
        tube = mesh.tube(radius=0.004)
        if tube.n_points == 0:
            # Degenerate zero-length edge (e.g. same-edge split arc); skip rendering.
            return
        actor = self.plotter.add_mesh(tube, color=color, name=f"edge_{eid}")
        self._edge_actors[eid] = actor

    def _add_vertex_actor(self, vid: int, color: str = "white") -> None:
        pos = self.smap.vertices[vid]
        sphere = pv.Sphere(radius=0.012, center=pos)
        actor = self.plotter.add_mesh(sphere, color=color, name=f"vert_{vid}")
        self._vertex_actors[vid] = actor

    def highlight_edge(self, eid: int | None, prev_eid: int | None = None) -> None:
        if prev_eid is not None and prev_eid in self._edge_actors:
            self.plotter.remove_actor(self._edge_actors[prev_eid])
            self._add_edge_actor(prev_eid, color="white")
        if eid is not None and eid in self._edge_actors:
            self.plotter.remove_actor(self._edge_actors[eid])
            self._add_edge_actor(eid, color="yellow")

    def show_snap_vertex(self, pos: np.ndarray | None, prev_pos: np.ndarray | None = None) -> None:
        if prev_pos is not None:
            self.plotter.remove_actor("snap_vertex")
        if pos is not None:
            sphere = pv.Sphere(radius=0.014, center=pos)
            self.plotter.add_mesh(sphere, color="white", name="snap_vertex")

    def show_selection_marker(self, name: str, pos: np.ndarray, color: str) -> None:
        self.plotter.remove_actor(name)
        sphere = pv.Sphere(radius=0.020, center=pos)
        self.plotter.add_mesh(sphere, color=color, name=name)

    def clear_selection_markers(self) -> None:
        self.plotter.remove_actor("select_p")
        self.plotter.remove_actor("select_q")

    def update_after_split(
        self,
        smap: SphericalMap,
        _fid1: int = 0,
        _fid2: int = 0,
        removed_fid: int | None = None,
        removed_eids: list[int] | None = None,
        new_eids: list[int] | None = None,
        new_vids: list[int] | None = None,
    ) -> None:
        del removed_fid
        self.smap = smap
        for eid in (removed_eids or []):
            if eid in self._edge_actors:
                self.plotter.remove_actor(self._edge_actors.pop(eid))
        for eid in (new_eids or []):
            if eid in smap.edges:
                self._add_edge_actor(eid)
        for vid in (new_vids or []):
            if vid in smap.vertices:
                self._add_vertex_actor(vid)
        self._update_hud()
        self.plotter.render()

    def _update_hud(self, mode: str = "IDLE", extra: str = "") -> None:
        V = len(self.smap.vertices)
        E = len(self.smap.edges)
        F = len(self.smap.faces)
        self.plotter.add_text(
            f"MODE: {mode}\n{extra}",
            position="upper_left", font_size=10,
            color="lightgreen", name="hud_mode",
        )
        self.plotter.add_text(
            f"V:{V}  E:{E}  F:{F}",
            position="upper_right", font_size=10,
            color="lightblue", name="hud_stats",
        )

    def update_hud(self, mode: str, extra: str = "") -> None:
        self._update_hud(mode, extra)
        self.plotter.render()
