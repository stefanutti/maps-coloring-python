###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# Convert GML graph files to planar embedding (json).
#
# History:
# - 24/Feb/2026 - Creation date
#
# TODOs:
# - Fix docstring for each function
#
# Done:
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

import argparse
import sys
import logging
import json

import networkx as nx

try:
    from ct.ct_graph_utils import check_graph_planarity_3_regularity_no_loops
    from ct.ct_graph_utils import faces_by_vertices
except ModuleNotFoundError:
    from ct_graph_utils import check_graph_planarity_3_regularity_no_loops
    from ct_graph_utils import faces_by_vertices


def gml_to_planar(gml_filename):
    """
    Load a GML file and convert it to the planar representation (faces as edge tuples).

    Parameters
    ----------
        gml_filename: The GML file to load

    Returns
    -------
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Load the graph from the GML file: %s", gml_filename)

    # NetworkX's read_gml is very strict and rejects valid GML files with
    # non-ASCII characters or non-standard attributes (e.g. _pos).
    # Use a simple custom parser that extracts just nodes (id) and edges (source, target).
    import re

    with open(gml_filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract node IDs
    node_ids = [int(m) for m in re.findall(r'node\s*\[\s*id\s+(\d+)', content)]

    # Extract edges (source and target may be on separate lines, with other attributes in between)
    edges = [(int(s), int(t)) for s, t in re.findall(r'edge\s*\[.*?source\s+(\d+).*?target\s+(\d+)', content, re.DOTALL)]

    # Build the graph
    the_graph = nx.MultiGraph()
    the_graph.add_nodes_from(node_ids)
    the_graph.add_edges_from(edges)

    # Ensure nodes are integers (GML may store them as strings)
    mapping = {}
    for node in the_graph.nodes():
        if not isinstance(node, int):
            try:
                mapping[node] = int(node)
            except (ValueError, TypeError):
                pass
    if mapping:
        the_graph = nx.relabel_nodes(the_graph, mapping)

    logger.info("Graph loaded: %s vertices, %s edges", the_graph.order(), the_graph.size())

    # Check planarity and 3-regularity
    check_graph_planarity_3_regularity_no_loops(the_graph)

    # Get the faces representation of the graph using faces_by_vertices
    temp_faces_by_vertices = faces_by_vertices(the_graph)

    # Convert vertex faces to edge faces (like Sage's faces() output)
    # faces() returns [(v1, v2), (v2, v3), ...] for each face
    g_faces = []
    for face in temp_faces_by_vertices:
        edge_face = []
        for i in range(len(face)):
            edge_face.append((face[i], face[(i + 1) % len(face)]))
        g_faces.append(edge_face)

    # Sort faces by length (smaller faces first)
    g_faces.sort(key=len)

    logger.info("END: Converted to planar representation with %s faces", len(g_faces))

    return g_faces


#######
# MAIN
#######

# Set logging facilities
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)

###############
# Read options:
###############
parser = argparse.ArgumentParser(description='Convert GML graph files to planar embedding (json)')
parser.add_argument("-g", "--gml", help="Load a .gml file", required=True)
parser.add_argument("-o", "--output", help="Save the planar embedding as a .planar file (json)", required=True)
args = parser.parse_args()

# Convert
g_faces = gml_to_planar(args.gml)

# Save the planar representation
logger.info("BEGIN: Save the planar embedding: %s", args.output)
with open(args.output, 'w') as fp:
    json.dump(g_faces, fp)
logger.info("END: Save the planar embedding: %s", args.output)

logger.info("Done. Faces: %s", len(g_faces))
