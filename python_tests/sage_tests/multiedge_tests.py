#!/usr/bin/env sage

import sys
from sage.all import *
from sage.graphs.graph_plot import GraphPlot

print ("Create a graph")
G = Graph(sparse=True)
G.allow_multiple_edges(True)
G.add_edge(1,2,"blue")
G.add_edge(2,1,"green")
G.add_edge(3,1,"green")
print (G.edges())

G.set_edge_label (1, 3, "aaa")
print (G.edges())

# G.set_edge_label (1, 2, "aaa")
# print (G.edges())

print (G.edge_boundary ([1], [2]))
