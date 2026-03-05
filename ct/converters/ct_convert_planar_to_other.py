###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# Convert planar embedding to other graph files: dot, etc.
#
# History:
# - 19/Mar/2018 - Creation data
#
# TODOs:
# - Fix docstring for each function
#
# Done:
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
# 4CT: Import stuffs
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######

import argparse
import sys
import logging
import json

import networkx as nx

from networkx.readwrite.edgelist import write_edgelist
from networkx.drawing.nx_pydot import write_dot


def export_graph(graph_to_export, name_of_file_without_extension):
    """
    Export the graph to file (.dot and .edgelist)

    Parameters
    ----------
        graph_to_export: The graph to export
        name_of_file_without_extension: The name of the file (without extension)
    """

    # Possibilities: adjlist, dot, edgelist, gexf, gml, graphml, multiline_adjlist, pajek, yaml
    write_dot(graph_to_export, name_of_file_without_extension + ".dot")
    logger.info("File saved: %s", name_of_file_without_extension + ".dot")

    write_edgelist(graph_to_export, name_of_file_without_extension + ".edgelist")
    logger.info("File saved: %s", name_of_file_without_extension + ".edgelist")

    return


#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
# 4CT # MAIN: Convert
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######
#######

# Set logging facilities: LEVEL XXX
#
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)

###############
# Read options:
###############
parser = argparse.ArgumentParser(description='args')
parser.add_argument("-p", "--planar", help="Load a .planar file (planar embedding) (no loops of multiple edges permitted)", required=True)
parser.add_argument("-o", "--output", help="Save a .dot and .edgelist file (networkx). Specify the name without extension", required=True)
args = parser.parse_args()

# Open the file
logger.info("BEGIN: Load the planar graph: %s", args.planar)
with open(args.planar, 'r') as fp:
    g_faces = json.load(fp)
logger.info("END: Load the planar graph: %s", args.planar)

# Cast back to tuples. json.dump write the "list of list of tuples" as "list of list of list"
#
# Original: [[(3,2),(3,5)],[(2,4),(1,3),(1,3)], ... ,[(1,2),(3,4),(6,7)]]
# Saved as: [[[3,2],[3,5]],[[2,4],[1,3],[1,3]], ... ,[[1,2],[3,4],[6,7]]]
g_faces = [[tuple(edge) for edge in face] for face in g_faces]

# Create the graph from the list of faces (flat them)
logger.info("BEGIN: all duplicated edges (each edge is listed many times in a planar representation)")
i = 0
flattened_egdes = [edge for face in g_faces for edge in face]
for edge in flattened_egdes:
    i += 1
    if not (i % 1000):
        logger.info("Removing duplicated edges. Counter: %s", i)
    reverse_edge = (edge[1], edge[0])
    if reverse_edge in flattened_egdes:
        flattened_egdes.remove(reverse_edge)
logger.info("END: Remove all duplicated edges")

# Create an empty graph
the_graph = nx.MultiGraph()

logger.info("BEGIN: Create the graph")
i = 0
for edge_to_add in flattened_egdes:
    the_graph.add_edge(edge_to_add[0], edge_to_add[1])
    i += 1
    if not (i % 1000):
        logger.info("Adding edges. Counter: %s", i)
logger.info("END: Create the graph")

# Export
logger.info("BEGIN: Export the graph")
export_graph(the_graph, args.output)
logger.info("END: Export the graph")
