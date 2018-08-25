#!/usr/bin/env python
import matplotlib.pyplot as pyplot
import networkx as nx

G=nx.MultiGraph()

G.add_edge(1,2,key="red")
G.add_edge(2,1,key="green")
G.add_edge(2,3,key="blue")
G.add_edge(3,2,key="green")

print(G.edges(data=True, keys=True))
G.remove_edge(3, 2, key="green")
print(G.edges(data=True, keys=True))

print(G.edges(data=True, keys=True))
G.remove_edge(1, 2)
print(G.edges(data=True, keys=True))

print(G.edges(1, data=True, keys=True))
