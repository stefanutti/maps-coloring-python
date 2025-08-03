#!/usr/bin/env python
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import defaultdict

def get_edge_curves(G):
    """Calculate appropriate curve parameters for each edge based on number of parallel edges"""
    # Count edges between each pair of nodes
    edge_counts = defaultdict(int)
    edge_positions = defaultdict(int)
    edge_params = {}
    
    # First pass: count edges between each node pair
    for u, v, k in G.edges(keys=True):
        edge_counts[(min(u,v), max(u,v))] += 1
    
    # Second pass: assign curve parameters
    for u, v, k in G.edges(keys=True):
        # Ensure consistent node order for edge count lookup
        u_min, v_max = min(u,v), max(u,v)
        count = edge_counts[(u_min, v_max)]
        position = edge_positions[(u_min, v_max)]
        
        if count > 1:
            # Calculate spread of curves based on number of edges
            max_rad = 0.3 * (count / 2)  # Scale max radius with edge count
            rad = np.linspace(-max_rad, max_rad, count)[position]
            # Adjust direction based on node order
            if u != u_min:
                rad = -rad
        else:
            rad = 0
            
        edge_params[(u, v, k)] = rad
        edge_positions[(u_min, v_max)] += 1
    
    return edge_params

def draw_curved_edge(ax, pos, node1, node2, color, rad):
    connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate("",
                xy=pos[node2], xycoords='data',
                xytext=pos[node1], textcoords='data',
                arrowprops=dict(arrowstyle="-",
                            color=color,
                            connectionstyle=connectionstyle,
                            linewidth=2))

def visualize_multigraph_states():
    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle('MultiGraph Edge Removal States\nwith Separated Multiple Edges', fontsize=12, y=0.98)
    
    # State 0: Initial graph
    G0 = nx.MultiGraph()
    G0.add_edge(1, 2, key="red")
    G0.add_edge(1, 2, key="green")
    G0.add_edge(1, 2, key="brown")
    G0.add_edge(1, 2, key="blue")
    G0.add_edge(2, 3, key="blue")
    G0.add_edge(2, 3, key="green")
    
    # State 1: After removing edge (2, 3, 'green')
    G1 = G0.copy()
    G1.remove_edge(2, 3, key="green")
    
    # State 2: After removing one edge between 1 and 2, specific key
    G2 = G1.copy()
    G2.remove_edge(1, 2, key="red")

    # State 2: After removing one edge between 1 and 2
    G3 = G2.copy()
    G3.remove_edge(1, 2)

    # List of graphs and their titles
    graphs = [
        (G0, axes[0,0], "Initial Graph"),
        (G1, axes[0,1], "After removing (2, 3, 'green')"),
        (G2, axes[1,0], "After removing (1, 2, 'red')"),
        (G3, axes[1,1], "After removing one (1, 2) rendom edge")
    ]
    
    # Draw each graph
    for G, ax, title in graphs:
        pos = nx.spring_layout(G, k=1.5, iterations=50)  # Increased k for more spread
        edge_curves = get_edge_curves(G)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=400, ax=ax)
        
        # Draw edges with curves for parallel edges
        for u, v, k in G.edges(keys=True):
            color = k if k != 'white' else 'gray'
            rad = edge_curves[(u, v, k)]
            draw_curved_edge(ax, pos, u, v, color, rad)
        
        # Add labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
        ax.set_title(title, pad=10, fontsize=10)
        ax.axis('on')
        ax.grid(True)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95], h_pad=1.5, w_pad=1.5)
    
    return fig

# Create and show the visualization
fig = visualize_multigraph_states()
plt.show()