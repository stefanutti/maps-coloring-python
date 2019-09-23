#!/usr/bin/env python
import matplotlib.pyplot as pyplot
import networkx as nx
from networkx.algorithms.planarity import check_planarity

G = nx.MultiGraph()
# the_colored_graph.add_edge(v1, v2, "red")
G.add_edge(1, 2, key="red")
G.add_edge(1, 3, key="green")
G.add_edge(1, 4, key="blue")

G.add_edge(2, 3, key="blue")
G.add_edge(3, 4, key="red")
G.add_edge(4, 2, key="green")

print (G.edges(data=True, keys=True))


is_it_planar, embedding = check_planarity(G, counterexample=True)

print("---")
print(embedding.edges, "---", G.degree)
print("---")

nx.draw(G)
pyplot.show()
