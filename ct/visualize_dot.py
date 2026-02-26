#!/usr/bin/env python3
"""
Visualize a .dot graph file with planar layout, small vertices, and colored edges.

Usage: python3 visualize_dot.py [dot_file]
Default: tttt.dot
"""

import sys
import pydot
import networkx as nx
import matplotlib.pyplot as plt


def parse_dot_file(filepath):
    """Parse a .dot file using pydot and return a networkx graph with edge colors."""
    G = nx.Graph()
    edge_colors = {}

    graphs = pydot.graph_from_dot_file(filepath)
    dot_graph = graphs[0]

    for edge in dot_graph.get_edges():
        u = int(edge.get_source())
        v = int(edge.get_destination())
        color = edge.get_color()
        if color:
            color = color.strip('"')
        else:
            color = 'black'
        G.add_edge(u, v)
        edge_colors[(u, v)] = color
        edge_colors[(v, u)] = color

    return G, edge_colors


def main():
    dot_file = sys.argv[1] if len(sys.argv) > 1 else "tttt.dot"

    print(f"Reading {dot_file} ...")
    G, edge_colors = parse_dot_file(dot_file)
    print(f"Graph: {G.number_of_nodes()} vertices, {G.number_of_edges()} edges")

    # Compute planar layout
    print("Computing planar layout ...")
    is_planar, embedding = nx.check_planarity(G)
    if not is_planar:
        print("WARNING: Graph is not planar! Falling back to spring layout.")
        pos = nx.spring_layout(G, seed=42, k=1.5, iterations=200)
    else:
        pos = nx.planar_layout(G)

    # Build edge color list in the order edges appear in G.edges()
    colors = []
    for u, v in G.edges():
        c = edge_colors.get((u, v), edge_colors.get((v, u), 'black'))
        colors.append(c)

    # Draw
    fig, ax = plt.subplots(1, 1, figsize=(16, 14))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Draw edges with colors
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=colors, width=1.2, alpha=0.85)

    # Draw vertices as small dots
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_size=15,
                           node_color='black',
                           edgecolors='#333333',
                           linewidths=0.5)

    ax.set_title(f"Planar graph: {G.number_of_nodes()} vertices, {G.number_of_edges()} edges",
                 color='black', fontsize=14, pad=15)
    ax.axis('off')

    # Legend for edge colors
    import matplotlib.patches as mpatches
    unique_colors = sorted(set(edge_colors.values()))
    legend_patches = [mpatches.Patch(color=c, label=c) for c in unique_colors]
    ax.legend(handles=legend_patches, loc='upper right',
              facecolor='white', edgecolor='gray', labelcolor='black',
              fontsize=10, title="Edge colors", title_fontsize=11)

    plt.tight_layout()

    # Save to file and show
    output_file = dot_file.rsplit('.', 1)[0] + '_planar.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Saved to {output_file}")
    plt.show()


if __name__ == '__main__':
    main()
