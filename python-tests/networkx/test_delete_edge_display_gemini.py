#!/usr/bin/env python
import matplotlib.pyplot as plt
import networkx as nx

# Create a MultiGraph instance
G = nx.MultiGraph()

# Add edges with keys to distinguish them
G.add_edge(1, 2, key="red")
G.add_edge(2, 1, key="green")
G.add_edge(1, 2, key="white")
G.add_edge(2, 3, key="blue")
G.add_edge(3, 2, key="green")

# Print all edges with their attributes and keys
print("0) Edges before removal:\n", G.edges(data=False, keys=True))

# Draw the initial graph
plt.figure(0)
nx.draw(G, with_labels=True, node_color='skyblue', node_size=700, font_size=16, font_weight='bold')
plt.title("0) Initial Graph")


# Remove a specific edge based on its key
G.remove_edge(3, 2, key="green")
print("1) Edges after removing edge (3, 2, 'green'):\n", G.edges(data=False, keys=True))

# Draw the graph after the first removal
plt.figure(1)
nx.draw(G, with_labels=True, node_color='lightgreen', node_size=700, font_size=16, font_weight='bold')
plt.title("1) After removing (3, 2, 'green')")


# Remove one of the edges between 1 and 2
G.remove_edge(1, 2)  # Removes an arbitrary edge
print("2) Edges after removing one edge, arbitrarily chosen, between (1, 2):\n", G.edges(data=False, keys=True))

# Draw the graph after the second removal
plt.figure(2)
nx.draw(G, with_labels=True, node_color='lightcoral', node_size=700, font_size=16, font_weight='bold')
plt.title("2) After removing one (1, 2) edge")

# Print remaining edges connected to node 1
print("3) Edges connected to node 1:\n", G.edges(1, data=False, keys=True))

#Draw the final graph
plt.figure(3)
nx.draw(G, with_labels=True, node_color='yellow', node_size=700, font_size=16, font_weight='bold')
plt.title("3) Final Graph")

plt.show()