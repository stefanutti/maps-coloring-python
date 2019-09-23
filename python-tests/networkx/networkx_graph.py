#!/usr/bin/env python
import matplotlib.pyplot as pyplot
import networkx as nx
from networkx.algorithms.planarity import check_planarity

########################
# Add a vertex to a face
########################
def remove_edge_with_specific_color(graph, u, v, color):
    print ("-------")
    multiple_edges = graph.get_edge_data(u, v)
    print (multiple_edges)
    print ("-------")
    key = [edge for edge in multiple_edges if edge['color'] == color]
    graph.remove_edge(u, v, key=key)

    return

G = nx.MultiGraph()
# the_colored_graph.add_edge(v1, v2, "red")
G.add_edge(1, 2, key="blue")
G.add_edge(2, 1, key="red")
G.add_edge(2, 3, key="red")
G.add_edge(4, 2, key="green")
G.add_edge(2, 4, key="blue")

print (G.edges(data=True, keys=True))

G.remove_edge(2, 4, key="blue")

print (G.edges(data=True, keys=True))

# Does not work G[1][2]['red']="aaa"

print (G.edges(data=True, keys=True))

expected, aaa = check_planarity(G)
print("---")
print(expected, aaa)
print("---")

nx.draw(G)
pyplot.show()
