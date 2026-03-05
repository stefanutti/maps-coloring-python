from sage.all import *
from sage.graphs.graph_coloring import edge_coloring
from datetime import datetime


###########################################################################
# Return a face as a list of ordered vertices. Used to create random graphs
# Taken on the internet (http://trac.sagemath.org/ticket/6236)
###########################################################################
def faces_by_vertices(g):
    # Ensure embedding exists (older code may assume one)
    if not g.get_embedding():
        try:
            g.is_planar(set_embedding=True, set_pos=True)
        except Exception:
            g.is_planar(set_embedding=True)
    d = {}
    embedding = g.get_embedding()
    for key, val in embedding.items():  # iteritems() -> items() for Python 3
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



tmp_g = graphs.RandomTriangulation(100)  # Random triangulation on the surface of a sphere
void = tmp_g.is_planar(set_embedding = True, set_pos = True)  # Cannot calculate the dual if the graph has not been embedded
the_graph = graph_dual(tmp_g)  # The dual of a triangulation is a 3-regular planar graph
the_graph.allow_loops(False)
the_graph.allow_multiple_edges(False)
void = the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

t1 = datetime.now()
void = edge_coloring(the_graph)
t2 = datetime.now()
delta = t2 - t1
print ("time: ", delta.seconds)

the_graph.graphviz_to_file_named("aaa.dot", edge_labels = False)
