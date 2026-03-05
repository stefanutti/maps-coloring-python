import pygraphviz as pgv
import networkx as nx
import matplotlib.pyplot as plt

Gtmp = pgv.AGraph('file.dot')
G = nx.Graph(Gtmp)
nx.draw(G)
plt.show()
