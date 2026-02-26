from sage.graphs.graph_coloring import edge_coloring
from sage import graphs
from datetime import datetime
from sage.graphs.graph import Graph
import random


###########################################################################
# Return a face as a list of ordered vertices. Used to create random graphs
# Taken on the internet (http://trac.sagemath.org/ticket/6236)
###########################################################################
def faces_by_vertices(g):
    # Updated for Python 3 (iteritems -> items)
    d = {}
    embedding = g.get_embedding()
    for key, val in embedding.items():
        cyc = list(val)
        d[key] = dict(zip(cyc, cyc[1:] + [cyc[0]]))
    list_faces = []
    for start in d:
        while d[start]:
            face = []
            prev = start
            _, curr = d[start].popitem()
            face.append(start)
            while curr != start:
                face.append(curr)
                prev, curr = (curr, d[curr].pop(prev))
            list_faces.append(face)
    return list_faces


#################################################################################################
# Return the dual of a graph. Used to create random graphs
# Taken on the internet: to make a dual of a triangulation (http://trac.sagemath.org/ticket/6236)
#################################################################################################
def graph_dual(g):
    f = [tuple(face) for face in faces_by_vertices(g)]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]
    dual = Graph([f_edges, lambda f1, f2: set(f1).intersection([(e[1], e[0]) for e in f2])])

    return dual


# Fallback random triangulation (stellar subdivisions) if Sage's RandomTriangulation is absent
def _fallback_random_triangulation(n):
    if n < 4:
        raise ValueError("Need at least 4 vertices for a triangulation")
    # Manually create K4 (tetrahedron)
    g = Graph()
    g.add_vertices(range(4))
    g.add_edges([
        (0,1),(0,2),(0,3),
        (1,2),(1,3),
        (2,3)
    ])
    # Track faces explicitly
    faces = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    next_v = 4
    while next_v < n:
        a, b, c = random.choice(faces)
        v = next_v
        next_v += 1
        g.add_vertex(v)
        g.add_edges([(v,a), (v,b), (v,c)])
        faces.remove((a,b,c))
        faces.extend([(v,a,b), (v,b,c), (v,c,a)])
    g.is_planar(set_embedding=True, set_pos=True)
    return g

def get_triangulation(n):
    # Try fuller generators module if available
    try:
        from sage.graphs.graph_generators import graphs as graph_gens
        if hasattr(graph_gens, "RandomTriangulation"):
            g = graph_gens.RandomTriangulation(n)
            g.is_planar(set_embedding=True, set_pos=True)
            return g
    except Exception:
        pass
    # Legacy attribute check (in case original import had it)
    if hasattr(graphs, "RandomTriangulation"):
        try:
            g = graphs.RandomTriangulation(n)
            g.is_planar(set_embedding=True, set_pos=True)
            return g
        except Exception:
            pass
    return _fallback_random_triangulation(n)


for i in range(15):
    tmp_g = get_triangulation(100)  # Random triangulation on the sphere
    the_graph = graph_dual(tmp_g)   # Dual is 3-regular planar
    the_graph.allow_loops(False)
    the_graph.allow_multiple_edges(False)
    the_graph.relabel()
    t1 = datetime.now()
    edge_coloring(the_graph)
    t2 = datetime.now()
    delta = t2 - t1
    print("Execution number:", i, ", time (s):", delta.total_seconds())