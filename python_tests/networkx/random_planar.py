# pip install networkx

import random
import networkx as nx


def random_cubic_planar(n_vertices: int, seed: int | None = None) -> nx.Graph:
    """
    Generate a random 3-regular planar (cubic planar) simple graph with n_vertices
    by taking the dual of a random spherical triangulation built via face-splitting
    (an Apollonian-style process).

    n_vertices must be an even integer >= 4.
    The distribution is not uniform over all cubic planar graphs, but the result
    is always planar, simple, connected, and 3-regular.
    """
    if n_vertices < 4 or n_vertices % 2 != 0:
        raise ValueError("n_vertices must be an even integer >= 4.")

    rng = random.Random(seed)
    target_faces = n_vertices  # faces of primal == vertices of dual

    # start with a K4 triangulation on the sphere: 4 triangular faces, no boundary
    Gp = nx.Graph()
    Gp.add_nodes_from(range(4))
    for i in range(4):
        for j in range(i + 1, 4):
            Gp.add_edge(i, j)
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]

    next_v = 4
    # each face split replaces 1 face with 3 faces → +2 faces per step
    while len(faces) < target_faces:
        i = rng.randrange(len(faces))
        a, b, c = faces.pop(i)
        v = next_v
        next_v += 1
        Gp.add_node(v)
        Gp.add_edges_from([(v, a), (v, b), (v, c)])
        faces.extend([(a, b, v), (b, c, v), (c, a, v)])

    # build the dual: one node per face; edges between faces that share a primal edge
    edge_to_faces: dict[tuple[int, int], list[int]] = {}
    for fid, (a, b, c) in enumerate(faces):
        for u, w in [(a, b), (b, c), (c, a)]:
            e = tuple(sorted((u, w)))
            edge_to_faces.setdefault(e, []).append(fid)

    H = nx.Graph()
    H.add_nodes_from(range(len(faces)))
    for inc in edge_to_faces.values():
        if len(inc) != 2:
            # should not happen on a closed triangulation
            raise RuntimeError("construction error: a primal edge has != 2 incident faces")
        f, g = inc
        if f != g:
            H.add_edge(f, g)

    # quick safety checks (optional)
    if not nx.check_planarity(H)[0]:
        raise RuntimeError("dual is not planar (unexpected)")
    if any(deg != 3 for _, deg in H.degree()):
        raise RuntimeError("dual is not 3-regular (unexpected)")

    return H

# example usage:
if __name__ == "__main__":
    G = random_cubic_planar(n_vertices=20, seed=42)
    print(G.number_of_nodes(), "vertices,", G.number_of_edges(), "edges")
    # write to graphml/edgelist if you like:
    # nx.write_graphml(G, "cubic_planar.graphml")
    # nx.write_edgelist(G, "cubic_planar.edgelist")
    # draw (large graphs will look dense):
    import matplotlib.pyplot as plt
    pos = nx.planar_layout(G)
    nx.draw(G, pos, node_size=10, width=0.5)
    plt.show()
