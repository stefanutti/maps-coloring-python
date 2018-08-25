import networkx as nx

def change_color(g, u, v, old_color, new_color):
    g.remove_edge(u, v, key=old_color)
    g.add_edge(u, v, key=new_color)


G = nx.MultiGraph()

G.add_edge(1, 2, key="red")
G.add_edge(2, 1, key="blue")
G.add_edge(3, 2, key="blue")

print(G.edges(data=True, keys=True))
change_color(G, 2, 1, "blue", "green")
print(G.edges(data=True, keys=True))

