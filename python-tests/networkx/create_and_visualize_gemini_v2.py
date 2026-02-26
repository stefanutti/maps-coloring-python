import networkx as nx
import matplotlib.pyplot as plt
import random


def expand_graph(G, node_to_expand):
    """
    Expands a graph by replacing a node with a triangle.
    This operation preserves 3-regularity and planarity.
    """
    if G.degree(node_to_expand) != 3:
        raise ValueError("Node to expand must have a degree of 3.")

    neighbors = list(G.neighbors(node_to_expand))
    new_node_base = max(G.nodes()) + 1
    v1, v2, v3 = new_node_base, new_node_base + 1, new_node_base + 2
    
    G.remove_node(node_to_expand)
    
    G.add_edge(v1, v2)
    G.add_edge(v2, v3)
    G.add_edge(v3, v1)
    
    G.add_edge(neighbors[0], v1)
    G.add_edge(neighbors[1], v2)
    G.add_edge(neighbors[2], v3)
    
    return G

# 1. Start with the base graph
G = nx.MultiGraph(nx.tetrahedral_graph())

# 2. Perform a smaller number of expansions for a clear visualization
num_expansions = 200 # Reduced for clarity
for _ in range(num_expansions):
    node_to_expand = random.choice(list(G.nodes()))
    G = expand_graph(G, node_to_expand)

print(f"Generated graph with {G.number_of_nodes()} nodes.")

# 3. Generate a planar layout for the graph
# This layout is specifically designed to draw planar graphs without edge crossings.
if nx.check_planarity(G)[0]:
    print("Graph is planar. Generating planar layout.")
    pos = nx.planar_layout(G)
    
    # 4. Draw the graph using the planar layout
    print("Draw it.")
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=False, node_size=1, font_size=8)
    plt.title("Planar Layout of a 3-Regular Graph")
    plt.show()
else:
    print("The generated graph is not planar, cannot create a planar layout.")