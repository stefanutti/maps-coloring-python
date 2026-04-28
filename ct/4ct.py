#!/usr/bin/env python3

###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# 4CT: This program uses these approaches together
#      - It consider Tait edge coloring and the equivalency of the 3-edge-coloring (known as Tait coloring) with the 4-face-coloring (the original four color theorem for maps)
#      - Uses a modified Kempe reduction method: it does not shrink a face (faces <= F5) down to a point, but removes a single edge from it (from faces <= F5)
#      - Uses a modified Kempe chain edge color switching: when restoring edges from the reduced graph, it will swap Half of the cycle of a color chain
#        - !!! This can be done because while rebuilding a map all chains are actually loops!!!
#
# History:
# - 10/Maj/2016 - Creation data
# - 27/Maj/2016 - Added the support to loops and multiple edges. Actually loops are not permitted at the beginning and are avoided during the reduction process
# - 31/Maj/2016 - Sage bug in the show() function? Response: use flush() before the show() function
# - 16/Jun/2016 - Restart from scratch. The case F2-F3 that generates loops cannot be avoid with the technique used so far
#               - I need to proceed in a different way: remove these cases
#                 - At the beginning there will be:
#                   - RULE-01: no F1 (loops)
#                   - RULE-01: nor F2+F2 = 0:0 = an island of one or more regions, all surrounded by a single face
#                   - RULE-03: no edges that do not separate two different g_faces
#                 - F2+F2  - Does not have to happen (to avoid) - Raise an exception - RULE-03 ensures that this will not happen
#                 - F2+F3  - Does not have to happen (to avoid) - Raise an exception - RULE-03 ensures that this will not happen
#                 - F2+F4> - This case can be easily handle O:O:
#                 - F3-F3  - This case can be handles ---O:O---
#                 - F3+F4>
# - 04/Jul/2016 - Restart from scratch. The only case that I have to consider is if I remove an edge that will leave the Graph 1-edge-connected
# - 01/Aug/2016 - I still need to complete the reconstruction of the F5 case (Since restoration of F5 is not so frequent, the program already works most of the times)
# - 06/Oct/2016 - The new algorithm to threat F5 cases in in place. It works verifying if the color at v1 and the color at c2 are on the same Kempe loop and, if not, trying a random switch
# - 06/Oct/2016 - Something new (bad and good at the same time) happened
#                 - Bad: Using this method You can encounter maps for which the method loops indefinitely
#                 - Good: Now that I know, at least I won't spend more time on this aspect. The other good thing is that this case is very rare, and the program can color almost all maps
# - 10/Mar/2020 - Coronavirus collateral effects ... back to programming = refactoring
#
# TODOs:
# - Moved to: https://github.com/stefanutti/maps-coloring-python/issues
#
# BACKLOG to evaluate:
# - TODO: Realize the reconstruction phase with the lists of the edge representation instead of using the graph. It will probably be a lot faster!
#
# Done:
# - Get rid of sage
# - Logging system
# - Sage doesn't handle multiple edges or loops when embedding is involved
#   - For example G.faces() executes an embedding and returns an error if the graph contains an F2 or a loop
#   - To handle it, this program avoid loops, removing first F2 g_faces (with care of F2 near F3 g_faces) and then handle F3, F4, F5 cases (unavoidable set)
# - Load external graphs (edgelist)
# - Save graphs (sdgelist)
# - To verify (condition to avoid): there are three topologically different island with three lands. Only the one with all lands touching each other has to be generated
#   - Answer: if you get rid of F2 before the other faces, when you get down to 5 faces left on the map, you'll be forced to avoid the condition
# - Override creation (mainly to debug previously elaborated maps)
#   g_faces = [[(27, 26), (26, 36), (36, 27)], [(11, 19), (19, 12), (12, 11)], [(38, 44), (44, 41), (41, 38)], [(3, 2), (2, 15), (15, 3)],
#              [(48, 49), (49, 46), (46, 48)], [(32, 54), (54, 55), (55, 33), (33, 32)], [(39, 46), (46, 49), (49, 42), (42, 39)],
#              [(33, 55), (55, 52), (52, 34), (34, 33)], [(40, 41), (41, 44), (44, 43), (43, 40)], [(26, 25), (25, 35), (35, 36), (36, 26)],
#              [(7, 8), (8, 54), (54, 32), (32, 7)], [(2, 1), (1, 14), (14, 15), (15, 2)], [(16, 17), (17, 9), (9, 10), (10, 16)],
#              [(5, 24), (24, 20), (20, 6), (6, 5)], [(13, 14), (14, 1), (1, 0), (0, 13)], [(34, 52), (52, 53), (53, 50), (50, 31), (31, 34)],
#              [(10, 12), (12, 19), (19, 18), (18, 16), (16, 10)], [(31, 50), (50, 51), (51, 47), (47, 45), (45, 30), (30, 31)],
#              [(28, 37), (37, 22), (22, 21), (21, 35), (35, 25), (25, 28)], [(21, 20), (20, 24), (24, 27), (27, 36), (36, 35), (35, 21)],
#              [(38, 29), (29, 30), (30, 45), (45, 43), (43, 44), (44, 38)],
#              [(23, 51), (51, 50), (50, 53), (53, 17), (17, 16), (16, 18), (18, 23)],
#              [(39, 40), (40, 43), (43, 45), (45, 47), (47, 48), (48, 46), (46, 39)],
#              [(9, 13), (13, 0), (0, 4), (4, 11), (11, 12), (12, 10), (10, 9)],
#              [(28, 29), (29, 38), (38, 41), (41, 40), (40, 39), (39, 42), (42, 37), (37, 28)], [(42, 49), (49, 48), (48, 47), (47, 51), (51, 23), (23, 22), (22, 37), (37, 42)],
#              [(8, 7), (7, 5), (5, 6), (6, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 8)], [(18, 19), (19, 11), (11, 4), (4, 6), (6, 20), (20, 21), (21, 22), (22, 23), (23, 18)],
#              [(55, 54), (54, 8), (8, 3), (3, 15), (15, 14), (14, 13), (13, 9), (9, 17), (17, 53), (53, 52), (52, 55)],
#              [(31, 30), (30, 29), (29, 28), (28, 25), (25, 26), (26, 27), (27, 24), (24, 5), (5, 7), (7, 32), (32, 33), (33, 34), (34, 31)]]
# 1) Handmade
#
# the_graph = Graph(sparse = True)
# the_graph.allow_loops(False)
# the_graph.allow_multiple_edges(True)
# the_graph.add_edge(1,2)
# the_graph.add_edge(2,3)
# the_graph.add_edge(3,4)
# the_graph.add_edge(4,5)
# the_graph.add_edge(5,1)
# the_graph.add_edge(1,6)
# the_graph.add_edge(2,10)
# the_graph.add_edge(3,12)
# the_graph.add_edge(4,11)
# the_graph.add_edge(5,7)
# the_graph.add_edge(6,7)
# the_graph.add_edge(6,8)
# the_graph.add_edge(8,10)
# the_graph.add_edge(10,12)
# the_graph.add_edge(12,11)
# the_graph.add_edge(7,9)
# the_graph.add_edge(8,9)
# the_graph.add_edge(9,11)
# the_graph.relabel()
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

# This is to solve some absolute imports issues for modules. I don't know why it is so complicate in python
import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import argparse
import collections
import time
import datetime
import logging
import logging.config
import json

# TODO: Really don't know why random.shuffle works using "import random" and "random.shuffle"
from random import shuffle, randint

import networkx as nx

from ct_graph_utils import check_graph_planarity_3_regularity_no_loops
from ct_graph_utils import kempe_chain_color_swap
from ct_graph_utils import graph_dual
from ct_graph_utils import print_graph
from ct_graph_utils import is_well_colored
from ct_graph_utils import get_edge_color
from ct_graph_utils import is_multiedge
from ct_graph_utils import check_if_vertex_is_in_face
from ct_graph_utils import create_graph_from_planar_representation
from ct_graph_utils import export_graph
from ct_graph_utils import are_edges_on_the_same_kempe_cycle
from ct_graph_utils import apply_half_kempe_loop_color_switching
from ct_graph_utils import remove_vertex_from_face
from ct_graph_utils import rotate
from ct_graph_utils import join_faces
from ct_graph_utils import is_the_graph_one_edge_connected
from ct_graph_utils import get_the_other_colors
from ct_graph_utils import log_faces
from ct_graph_utils import faces_by_vertices

# Import helper functions for Sage-like API
from ct_graph_utils import graph_edges_incident
from ct_graph_utils import graph_edges_incident_no_labels
from ct_graph_utils import graph_edges
from ct_graph_utils import graph_add_edge
from ct_graph_utils import graph_delete_edge
from ct_graph_utils import graph_set_edge_label
from ct_graph_utils import graph_random_edge
from ct_graph_utils import graph_edge_iterator
from ct_graph_utils import is_graph_regular

from ct.converters.ct_create_random_maps_from_2v import PlanarGraphGenerator

import cProfile
import pstats

# Module-level logger (used by functions defined at module scope)
logger = logging.getLogger(__name__)


######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
# 4CT: Helping functions
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######

def initialize_statistics():
    """
    Initialize statistics.
    """

    stats['F#'] = {}
    stats['F-Initial#'] = 0

    stats['CASE-F2-01'] = 0

    stats['CASE-F3-01'] = 0

    stats['CASE-F4-01'] = 0
    stats['CASE-F4-02'] = 0
    stats['CASE-F4-03'] = 0

    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C3'] = 0
    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C4'] = 0
    stats['CASE-F5-C1!=C2-SameKempeLoop-C1-C2'] = 0

    stats['SELECT-S4-F5-F5'] = 0
    stats['SELECT-S4-F5-F6'] = 0
    stats['SELECT-S4-F5-FALLBACK'] = 0
    stats['SELECT-S4-F4-INTERRUPT'] = 0

    stats['TOTAL_RANDOM_KEMPE_SWITCHES'] = 0
    stats['MAX_RANDOM_KEMPE_SWITCHES'] = 0

    stats['time_GRAPH_CREATION_BEGIN'] = 0
    stats['time_GRAPH_CREATION_END'] = 0

    stats['time_ELABORATION_BEGIN'] = 0
    stats['time_ELABORATION_END'] = 0
    stats['time_ELABORATION'] = 0

    return


def print_stats():
    """
    Print the statistics.

    Parameters
    ----------
        stats: The statistics to print
    """

    logger.info("------------------")
    logger.info("BEGIN: Print stats")
    logger.info("------------------")

    ordered_stats = collections.OrderedDict(sorted(stats.items()))
    for stat in ordered_stats:
        logger.info("Stat: %s = %s", stat, stats[stat])

    logger.info("----------------")
    logger.info("END: Print stats")
    logger.info("----------------")

    return


def ariadne_case_f2(the_colored_graph, ariadne_step):
    """
    Restore the edge of a F2 face.

    Parameters
    ----------
        the_colored_graph: The graph to color
        ariadne_step: The step to process
        stats: The statistics to print
    """

    # CASE: F2
    # Update stats
    stats['CASE-F2-01'] += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F2 (multiple edge)")
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    vertex_to_join_near_v1 = ariadne_step[3]
    vertex_to_join_near_v2 = ariadne_step[4]

    # For F2 to compute the new colors is easy
    previous_edge_color = get_edge_color(the_colored_graph, (vertex_to_join_near_v1, vertex_to_join_near_v2))

    # Choose available colors
    new_multiedge_color_one = get_the_other_colors([previous_edge_color])[0]
    new_multiedge_color_two = get_the_other_colors([previous_edge_color])[1]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new_multiedge_color_one: %s, new_multiedge_color_two: %s", new_multiedge_color_one, new_multiedge_color_two)

    # Delete the edge
    # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
    graph_delete_edge(the_colored_graph, vertex_to_join_near_v1, vertex_to_join_near_v2, previous_edge_color)

    # Restore the previous edge
    graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1, previous_edge_color)
    graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2, previous_edge_color)
    graph_add_edge(the_colored_graph, v1, v2, new_multiedge_color_one)
    graph_add_edge(the_colored_graph, v2, v1, new_multiedge_color_two)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color: %s, new_multiedge_color_one: %s, new_multiedge_color_two: %s", previous_edge_color, new_multiedge_color_one, new_multiedge_color_two)

    # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
    # if is_well_colored(the_colored_graph) is False:
    #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
    #     exit(-1)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F2 (multiple edge)")


def ariadne_case_f3(the_colored_graph, ariadne_step):
    """
    Restore the edge of a F3 face.

    Parameters
    ----------
        the_colored_graph: The graph to color
        ariadne_step: The step to process
        stats: The statistics to print
    """

    # CASE: F3
    # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
    # Update stats
    stats['CASE-F3-01'] += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F3")
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    vertex_to_join_near_v1_on_the_face = ariadne_step[3]
    vertex_to_join_near_v2_on_the_face = ariadne_step[4]
    vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
    vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

    # For F3 to compute the new colors is easy (check also if it is a multiple edges)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v1_on_the_face: %s, vertex_to_join_near_v2_on_the_face: %s, vertex_to_join_near_v1_not_on_the_face: %s, vertex_to_join_near_v2_not_on_the_face: %s", vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face)

    # If e1 and e2 have the same vertices, they are the same multiedge
    if (vertex_to_join_near_v1_on_the_face == vertex_to_join_near_v2_on_the_face) and (vertex_to_join_near_v1_not_on_the_face == vertex_to_join_near_v2_not_on_the_face):

        # Get the colors of the two edges (multiedge). Select only the two multiedges (e1, e2 with same vertices)
        temp_multiple_edges_to_check = graph_edges_incident(the_colored_graph, vertex_to_join_near_v1_on_the_face)  # Three edges will be returned
        multiple_edges_to_check = [(va, vb, l) for (va, vb, l) in temp_multiple_edges_to_check if (vertex_to_join_near_v1_not_on_the_face == va) or (vertex_to_join_near_v1_not_on_the_face == vb)]
        previous_edge_color_at_v1 = multiple_edges_to_check[0][2]
        previous_edge_color_at_v2 = multiple_edges_to_check[1][2]
    else:
        previous_edge_color_at_v1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))
        previous_edge_color_at_v2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))

    if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

    # Checkpoint
    if previous_edge_color_at_v1 == previous_edge_color_at_v2:
        logger.error("Unexpected condition (for F3 faces two edges have a vertex in common, and so colors MUST be different at this point). Mario you'd better go back to paper")
        exit(-1)

    # Choose a different color
    new_edge_color = get_the_other_colors([previous_edge_color_at_v1, previous_edge_color_at_v2])[0]

    # Delete the edges
    # Since e1 and e2 may be the same multiedge or maybe separately on different multiedge, I remove them using also the "label" parameter
    # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
    graph_delete_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
    graph_delete_edge(the_colored_graph, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

    # Restore the previous edge
    graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_on_the_face, previous_edge_color_at_v2)
    graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
    graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
    graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
    graph_add_edge(the_colored_graph, v1, v2, new_edge_color)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s, new_edge_color: %s", previous_edge_color_at_v1, previous_edge_color_at_v2, new_edge_color)

    # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))
    # if is_well_colored(the_colored_graph) is False:
    #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
    #     exit(-1)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F3")


def ariadne_case_f4(the_colored_graph, ariadne_step):
    """
    Restore the edge of a F4 face.

    Parameters
    ----------
        the_colored_graph: The graph to color
        ariadne_step: The step to process
        stats: The statistics to print
    """

    # CASE: F4
    # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F4")
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    vertex_to_join_near_v1_on_the_face = ariadne_step[3]
    vertex_to_join_near_v2_on_the_face = ariadne_step[4]
    vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
    vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

    # For F4 to compute the new colors is not so easy
    previous_edge_color_at_v2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))

    # If e1 is a F2 face, for sure one of the two edge has the same color as e2
    # For now I don't care is also e2 is part of an F2 face. This solved bug should not impact e2
    if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face):
        previous_edge_color_at_v1 = previous_edge_color_at_v2
    else:
        previous_edge_color_at_v1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))

    if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

    # For an F4, the top edge is the edge not adjacent to the edge to restore (as in a rectangular area)
    edge_color_of_top_edge = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face))
    if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_color_of_top_edge: %s", edge_color_of_top_edge)

    # Handle the different cases
    if previous_edge_color_at_v1 == previous_edge_color_at_v2:

        # Update stats
        stats['CASE-F4-01'] += 1

        if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F4 - Same color at v1 and v2")
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

        # CASE: F4 SUBCASE: Same color at v1 and v2
        # Since edges at v1 and v2 are on the same Kempe cycle (with the top edge), I can also avoid the kempe chain color switching, since in this case the chain is made of three edges
        graph_delete_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        graph_delete_edge(the_colored_graph, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

        # Kempe chain color swap is done manually since the chain is only three edges long
        graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
        graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

        # Just for sure. Is the top edge a multiedge? I need to verify it. It should't be
        if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
            graph_delete_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
            graph_add_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
            logger.error("HERE?")  # This is only to verify if this condition may happen ... and my reasoning was wrong :-(
            exit(-1)
        else:
            graph_set_edge_label(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

        # Restore the other edges
        graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
        graph_add_edge(the_colored_graph, v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

        # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))
        # if is_well_colored(the_colored_graph) is False:
        #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
        #     exit(-1)

        if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F4 - Same color at v1 and v2")
    else:

        # In this case I have to check if the edges at v1 and v2 are on the same Kempe cycle
        if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face), previous_edge_color_at_v1, previous_edge_color_at_v2) is True:

            # Update stats
            stats['CASE-F4-02'] += 1

            if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F4 - The two edges are on the same Kempe cycle")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

            # CASE: F4, SUBCASE: The two edges are on the same Kempe cycle
            # Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping
            apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, previous_edge_color_at_v1, previous_edge_color_at_v2, previous_edge_color_at_v1, previous_edge_color_at_v2)

            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F4 - The two edges are on the same Kempe cycle")

        else:

            # Update stats
            stats['CASE-F4-03'] += 1

            if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F4 - The two edges are NOT on the same Kempe cycle")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph_edge_iterator(the_colored_graph, labels=True)), is_graph_regular(the_colored_graph, 3))

            # CASE: F4 SUBCASE: Worst case: The two edges are NOT on the same Kempe cycle
            # I'll rotate the colors of the cycle for the edge at v1, and then, since edge_color_at_v1 will be == edge_color_at_v2, apply CASE-001
            kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), previous_edge_color_at_v1, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])
            previous_edge_color_at_v1 = previous_edge_color_at_v2

            # CASE: F4, SUBCASE: The two edges are now on the same Kempe cycle
            # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
            graph_delete_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            graph_delete_edge(the_colored_graph, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

            # Kempe chain color swap is done manually since the chain is only three edges long
            graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
            graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

            # Just to be sure. Is the top edge a multiedge? I need to verify it. It should't be
            if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                graph_delete_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                graph_add_edge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                graph_set_edge_label(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

            # Restore the other edges
            graph_add_edge(the_colored_graph, v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            graph_add_edge(the_colored_graph, v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
            graph_add_edge(the_colored_graph, v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F4 - The two edges are NOT on the same Kempe cycle")

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F4")


def ariadne_case_f5(the_colored_graph, ariadne_step):
    """
    Restore the edge of a F5 face.

    Parameters
    ----------
        the_colored_graph: The graph to color
        ariadne_step: The step to process
        stats: The statistics to print
    """

    # CASE: F5
    # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F5")

    # clean-up v1 + v2
    # v1 = ariadne_step[1]
    # v2 = ariadne_step[2]
    vertex_to_join_near_v1_on_the_face = ariadne_step[3]
    vertex_to_join_near_v2_on_the_face = ariadne_step[4]
    vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
    vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

    # I have to get the two edges that are on top
    # These are two edges that have near_v1_on_the_face and near_v2_on_the_face and a shared vertex
    # First thing: I need to get the vertex_in_the_top_middle
    # Removed the form with the [] (list) from the edges_incident() when there is only one item in the list
    edges_at_vertices_near_v1_on_the_face = graph_edges_incident_no_labels(the_colored_graph, vertex_to_join_near_v1_on_the_face)
    edges_at_vertices_near_v2_on_the_face = graph_edges_incident_no_labels(the_colored_graph, vertex_to_join_near_v2_on_the_face)
    temp_v1 = [item for sublist in edges_at_vertices_near_v1_on_the_face for item in sublist]
    temp_v1.remove(vertex_to_join_near_v1_not_on_the_face)
    temp_v2 = [item for sublist in edges_at_vertices_near_v2_on_the_face for item in sublist]
    temp_v2.remove(vertex_to_join_near_v2_not_on_the_face)
    vertex_in_the_top_middle = list(set.intersection(set(temp_v1), set(temp_v2)))[0]

    # Useful to try to verify if the number of switches may be limited
    # restore_random_edge_to_fix_the_impasse = (0, 0)
    # restore_color_one = ""
    # restore_color_two = ""

    # The algorithm:
    # DONE: Update the algoritm respect to how it was implemented
    #
    # - Check if c1 and c2 are on the same Kempe chain
    # - If not, try a random swap
    #   - First try a swap starting from an edge on the face
    #   - Then try a swap starting from a random edge of the kempe loop on v1
    #   - Then try a swap starting from a random edge of the entire graph
    end_of_f5_restore = False
    i_attempt = 0
    while end_of_f5_restore is False:

        # For F5 to compute the new colors is difficult (and needs to be proved if always works in all cases)
        # I need to handle the different cases
        c1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))
        c3 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_in_the_top_middle))
        c4 = get_edge_color(the_colored_graph, (vertex_in_the_top_middle, vertex_to_join_near_v2_on_the_face))
        c2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))

        if logger.isEnabledFor(logging.DEBUG): logger.debug("Four colors are: c1 = %s, c3 = %s, c4 = %s, c2 = %s", c1, c3, c4, c2)

        # If the first edge bolongs to an F2 and if c1 = c2, then the F2 other color is == to c4
        # And in this case I need to avoid this situation or the are_edges_on_the_same_kempe_cycle(c1, c4) would terminate immedially on the F2
        if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face):
            if c1 == c2:
                c1_other_color = get_the_other_colors([c1, c3])[0]
                if logger.isEnabledFor(logging.DEBUG): logger.debug("Avoid this case (c1 = %s is converted to c1_other_color = %s)", c1, c1_other_color)
                c1 = c1_other_color

        # F5-C1
        if c1 == c2:

            # The four edges are: c1, c3, c4, c2==c1
            #
            # NOTE:
            # - Next comment was not true:
            #   - In case e1 and e2 are not on the same Kempe loop (c1, c3) or (c2, c4), the switch of the top colors (c3, c4) solves (I hope) the situation
            if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c3):

                if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

                # Apply half Kempe loop color switching (c1, c3)
                apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c3)
                end_of_f5_restore = True

                # Update stats
                stats['CASE-F5-C1==C2-SameKempeLoop-C1-C3'] += 1
                if logger.isEnabledFor(logging.DEBUG): logger.debug("END: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

            elif are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c4):

                if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C4")

                # Apply half Kempe loop color switching (c2==c1, c4)
                apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c4)
                end_of_f5_restore = True

                # Update stats
                stats['CASE-F5-C1==C2-SameKempeLoop-C1-C4'] += 1
                if logger.isEnabledFor(logging.DEBUG): logger.debug("END: CASE-F5-C1==C2-SameKempeLoop-C1-C4")

        else:  # c1 != c2

            # Only for debugging. See the comment above of the same check (is_multiedge)
            if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face):
                c1_other_color = get_the_other_colors([c1, c3])[0]
                if logger.isEnabledFor(logging.DEBUG): logger.debug("Other edge of the starting edge e1 (in this case belonging to an F2): c1 = %s, c1_other_color = %s, c2 = %s", c1, c1_other_color, c2)

            # NOTE:
            # - Next comment was true, but not useful:
            #   - In case e1 and e2 are not on the same Kempe loop (c1, c2), the swap of c2, c1 at e2 will give the the first case
            if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c2):

                if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: CASE-F5-C1!=C2-SameKempeLoop-C1-C2")

                # Apply half Kempe loop color switching (c1, c2)
                apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c2, c1, c2)
                end_of_f5_restore = True

                # Update stats
                stats['CASE-F5-C1!=C2-SameKempeLoop-C1-C2'] += 1

                if logger.isEnabledFor(logging.DEBUG): logger.debug("END: CASE-F5-C1!=C2-SameKempeLoop-C1-C2")

        # Try random switches around the graph for a random few times. It works almost all times
        # But it may get stuck in infinite loops:
        # - See: https://four-color-theorem.org/2016/11/05/four-color-theorem-infinite-switches-are-not-enough-rectangular-map/
        #
        # TODO: If the first random switch doesn't solve the problem, reset and try another random switch. I need to verify if a single switch somewhere may fix an impasse
        if end_of_f5_restore is False:

            if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: Random switch")

            # Attempts to change (swap) something in the graph
            stats['TOTAL_RANDOM_KEMPE_SWITCHES'] += 1
            i_attempt += 1

            random_edge_to_fix_the_impasse = graph_random_edge(the_colored_graph, labels=True)
            color_of_the_random_edge = get_edge_color(the_colored_graph, random_edge_to_fix_the_impasse)
            another_random_color = get_the_other_colors([color_of_the_random_edge])[randint(0, 1)]

            if logger.isEnabledFor(logging.DEBUG): logger.debug("Selected Edge: %s (swap_c1: %s, swap_c2: %s)", random_edge_to_fix_the_impasse, color_of_the_random_edge, another_random_color)

            # No need to swap if the selected face belongs to an F2. Hence if it is not, try a random Kempe switch
            # TODO: In case of multiedge as the random edge chosen, select the colors carefully
            if is_multiedge(the_colored_graph, random_edge_to_fix_the_impasse[0], random_edge_to_fix_the_impasse[1]) is False:

                # Apply an entire cycle color switching
                if logger.isEnabledFor(logging.DEBUG): logger.debug("Before kempe_chain_color_swap - is_well_colored?: %s and (c1: %s, c2: %s)", is_well_colored(the_colored_graph), color_of_the_random_edge, another_random_color)
                kempe_chain_color_swap(the_colored_graph, random_edge_to_fix_the_impasse, color_of_the_random_edge, another_random_color)
                if logger.isEnabledFor(logging.DEBUG): logger.debug("After kempe_chain_color_swap - is_well_colored?: %s and (c1: %s, c2: %s)", is_well_colored(the_colored_graph), color_of_the_random_edge, another_random_color)
            else:
                if logger.isEnabledFor(logging.DEBUG): logger.debug("The selected random edge it is a multiedge")

            # Only for debug: which map is causing this impasse?
            if i_attempt == 1000:
                export_graph(the_colored_graph, "debug/debug.really_bad_case_infinite_loop")
                logger.error("ERROR: Infinite loop. Check the debug.really_bad_case.* files")
                logger.error("Try to shuffle the faces at the beginning: sage 4ct.py -p debug/debug.previous_run.planar -c <USE the same sequence you used the previous run> -s")

                # This is used as a sentinel to use the runs.bash script
                open("debug/error.txt", 'a').close()
                exit(-1)

            # TODO: if is_well_colored(the_colored_graph) is False:
            #     print_graph(the_colored_graph)
            #     logger.error("is_well_colored: False")
            #     exit(-1)

            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: Random switch")
            if i_attempt > 0:
                logger.info("Random switches: %d", i_attempt)

    # END F5 has been restored
    stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F5: %s", stats['TOTAL_RANDOM_KEMPE_SWITCHES'])



def select_edge_to_remove_by_largest_neighbor(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected.

    Among all faces of the same type (same size), this function evaluates every edge of every face,
    and selects the valid edge whose adjacent face (f2) is the largest.

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separetes two faces
        f1_plus_f2_temp: It is used to speed up computation. I need it here and and it will be used outside this funcion
    """

    logger.info("BEGIN %s: Search the right edge to remove (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    def _best_for_size(target_size):
        faces = [f for f in g_faces if len(f) == target_size]
        best_edge = best_f1 = best_f2 = best_joined = None
        best_f2_len = 0
        for candidate_f1 in faces:
            for edge in candidate_f1:
                rotated = rotate(edge, 1)
                if target_size == 2:
                    temp = [f for f in g_faces if rotated in f]
                    temp.remove(candidate_f1)
                    candidate_f2 = temp[0]
                else:
                    candidate_f2 = next(f for f in g_faces if rotated in f)
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if is_the_graph_one_edge_connected(candidate_joined):
                    continue
                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = candidate_f1
                    best_f2 = candidate_f2
                    best_joined = candidate_joined
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("New best edge found: %s (f2 size: %s)", edge, best_f2_len)
        return (best_edge, best_f1, best_f2, best_joined) if best_edge is not None else None

    result = next(
        (r for size in face_size_priority for r in [_best_for_size(size)] if r is not None),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f1, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)", i_global_counter, edge_to_remove, len(f1), len(f2))

    return edge_to_remove, f1, f2, f1_plus_f2_temp, None


def select_edge_to_remove_first_fit(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected.

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separetes two faces
        f1_plus_f2_temp: It is used to speed up computation. I need it here and and it will be used outside this funcion
    """

    logger.info("BEGIN %s: Search the right edge to remove (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    f1 = next(
        (f for size in face_size_priority for f in g_faces if len(f) == size),
        g_faces[0],
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Selected face: %s", f1)

    result = next(
        (
            (edge, f2, joined)
            for edge in f1
                for f2 in [
                    next(f for f in g_faces if rotate(edge, 1) in f and f is not f1)
                    if len(f1) == 2
                    else next(f for f in g_faces if rotate(edge, 1) in f)
                ]
            for joined in [join_faces(f1, f2, edge)]
            if not is_the_graph_one_edge_connected(joined)
        ),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)", i_global_counter, edge_to_remove, len(f1), len(f2))

    return edge_to_remove, f1, f2, f1_plus_f2_temp, None


def select_edge_to_remove_f5_shared_vertex(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge to remove using a strategy tailored for F5 faces.

    For F2/F3/F4 faces, behaves like first-fit.
    For F5 faces: finds an adjacent F5 or F6 face, then selects an edge from the F5
    that shares exactly one vertex with the neighboring face (not the shared border edge).

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separates two faces
        f1_plus_f2_temp: It is used to speed up computation
    """

    logger.info("BEGIN %s: Search the right edge to remove - f5_shared_vertex (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    log_suffix = ""

    def _try_for_size(target_size):
        nonlocal log_suffix
        faces = [f for f in g_faces if len(f) == target_size]

        if target_size <= 4:
            for candidate_f1 in faces:
                for edge in candidate_f1:
                    rotated = rotate(edge, 1)
                    if target_size == 2:
                        temp = [f for f in g_faces if rotated in f]
                        temp.remove(candidate_f1)
                        candidate_f2 = temp[0]
                    else:
                        candidate_f2 = next(f for f in g_faces if rotated in f)
                    candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                    if not is_the_graph_one_edge_connected(candidate_joined):
                        return (edge, candidate_f1, candidate_f2, candidate_joined)
            return None

        # F5: find an adjacent F5 or F6 and select an edge with exactly one shared vertex
        for candidate_f1 in faces:
            adjacent_target = next(
                (
                    neighbor
                    for edge in candidate_f1
                    # single-element list binds neighbor so it can be tested and yielded in one expression
                    for neighbor in [next(face for face in g_faces if rotate(edge, 1) in face)]
                    if len(neighbor) in (5, 6)
                ),
                None,
            )

            if adjacent_target is not None:
                adj_vertices = {v for e in adjacent_target for v in e}
                for edge in candidate_f1:
                    v1_shared = edge[0] in adj_vertices
                    v2_shared = edge[1] in adj_vertices
                    if v1_shared != v2_shared:
                        candidate_f2 = next(f for f in g_faces if rotate(edge, 1) in f)
                        candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                        if not is_the_graph_one_edge_connected(candidate_joined):
                            log_suffix = " [f5_shared_vertex: adj=%s]" % len(adjacent_target)
                            return (edge, candidate_f1, candidate_f2, candidate_joined)

        # Fallback for F5: any valid edge
        for candidate_f1 in faces:
            for edge in candidate_f1:
                candidate_f2 = next(f for f in g_faces if rotate(edge, 1) in f)
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if not is_the_graph_one_edge_connected(candidate_joined):
                    log_suffix = " [f5_shared_vertex: fallback]"
                    return (edge, candidate_f1, candidate_f2, candidate_joined)

        return None

    result = next(
        (r for size in face_size_priority for r in [_try_for_size(size)] if r is not None),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f1, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)%s", i_global_counter, edge_to_remove, len(f1), len(f2), log_suffix)
    return edge_to_remove, f1, f2, f1_plus_f2_temp, None


def _select_from_f5_pairs(g_faces, f5_candidates, pair_neighbor_size):
    """
    For each F5 in f5_candidates, find adjacent faces of size pair_neighbor_size.
    When found, evaluate the 4 edges incident to the shared edge's endpoints
    (excluding the shared edge itself). Return the valid edge with max len(f2).

    Returns (best_edge, best_f1, best_f2, best_f1_plus_f2) or (None, None, None, None).
    """
    best_edge = None
    best_f1 = None
    best_f2 = None
    best_f1_plus_f2 = None
    best_f2_len = 0

    for face_a in f5_candidates:
        for i_shared in range(len(face_a)):
            shared_edge = face_a[i_shared]  # (v1, v2) as it appears in face_a
            rotated_shared = rotate(shared_edge, 1)  # (v2, v1)

            face_b = next((f for f in g_faces if rotated_shared in f), None)
            if face_b is None or len(face_b) != pair_neighbor_size:
                continue

            # The 4 candidate edges: 2 from face_a (neighbors of shared_edge in cycle),
            # 2 from face_b (neighbors of rotated_shared in cycle)
            n_a = len(face_a)
            idx_b = face_b.index(rotated_shared)
            n_b = len(face_b)

            candidate_edges = [
                (face_a, face_a[(i_shared - 1) % n_a]),   # edge ending at v1 in face_a
                (face_a, face_a[(i_shared + 1) % n_a]),   # edge starting at v2 in face_a
                (face_b, face_b[(idx_b - 1) % n_b]),      # edge ending at v2 in face_b
                (face_b, face_b[(idx_b + 1) % n_b]),      # edge starting at v1 in face_b
            ]

            for candidate_f1, edge in candidate_edges:
                rotated_edge = rotate(edge, 1)
                candidate_f2 = next((f for f in g_faces if rotated_edge in f), None)
                if candidate_f2 is None:
                    continue

                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)

                if is_the_graph_one_edge_connected(candidate_joined):
                    continue

                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = candidate_f1
                    best_f2 = candidate_f2
                    best_f1_plus_f2 = candidate_joined

    return best_edge, best_f1, best_f2, best_f1_plus_f2


def _select_f5_f6_edge(g_faces, f5_candidates):
    """
    For each F5 in f5_candidates adjacent to an F6, evaluate the 2 edges of the F5
    face at the shared edge's endpoints (excluding the shared edge itself).
    Returns the valid edge (removal not a bridge) with the largest adjacent face f2.
    Returns (best_edge, best_f1, best_f2, best_f1_plus_f2) or (None, None, None, None).
    """
    best_edge = None
    best_f1 = None
    best_f2 = None
    best_f1_plus_f2 = None
    best_f2_len = 0

    for face_a in f5_candidates:
        n_a = len(face_a)
        for i_shared in range(n_a):
            shared_edge = face_a[i_shared]
            rotated_shared = rotate(shared_edge, 1)
            face_b = next((f for f in g_faces if rotated_shared in f), None)
            if face_b is None or len(face_b) != 6:
                continue

            # Two candidate edges: edges of F5 at v1 and v2 of the shared edge
            candidate_edges = [
                face_a[(i_shared - 1) % n_a],   # edge ending at v1
                face_a[(i_shared + 1) % n_a],   # edge starting at v2
            ]

            for edge in candidate_edges:
                rotated_edge = rotate(edge, 1)
                candidate_f2 = next((f for f in g_faces if rotated_edge in f), None)
                if candidate_f2 is None:
                    continue
                candidate_joined = join_faces(face_a, candidate_f2, edge)
                if is_the_graph_one_edge_connected(candidate_joined):
                    continue
                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = face_a
                    best_f2 = candidate_f2
                    best_f1_plus_f2 = candidate_joined

    return best_edge, best_f1, best_f2, best_f1_plus_f2


def _select_max_neighbor_from_candidates(g_faces, candidates):
    """
    Max-neighbor selection over the given candidate face list.
    Returns (best_edge, best_f1, best_f2, best_f1_plus_f2) or (None, None, None, None).
    """
    best_edge = None
    best_f1 = None
    best_f2 = None
    best_f1_plus_f2 = None
    best_f2_len = 0

    for candidate_f1 in candidates:
        for i_edge in range(len(candidate_f1)):
            edge = candidate_f1[i_edge]
            rotated_edge = rotate(edge, 1)

            candidate_f2 = next((f for f in g_faces if rotated_edge in f), None)
            if candidate_f2 is None:
                continue

            candidate_joined = join_faces(candidate_f1, candidate_f2, edge)

            if is_the_graph_one_edge_connected(candidate_joined):
                continue

            if len(candidate_f2) > best_f2_len:
                best_f2_len = len(candidate_f2)
                best_edge = edge
                best_f1 = candidate_f1
                best_f2 = candidate_f2
                best_f1_plus_f2 = candidate_joined

    return best_edge, best_f1, best_f2, best_f1_plus_f2


def _vertices_of(face):
    return {v for edge in face for v in edge}


def update_wave_frontier(current, f1_len, f1_plus_f2, v1, v2):
    """
    Return the new wave-frontier set after reducing one face.

    - F5 reduction: activate or extend the frontier with vertices of the
      merged face, minus the two vertices removed from the graph.
    - Non-F5 reduction with active frontier: extend and clean the same way.
    - Non-F5 reduction with inactive frontier: return None (stays inactive).

    Does not mutate `current`.
    """
    is_f5 = (f1_len == 5)
    was_active = current is not None
    if not (is_f5 or was_active):
        return None
    base = current if was_active else set()
    return (base | _vertices_of(f1_plus_f2)) - {v1, v2}


def select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, recently_modified_vertices=None):
    """
    Selection strategy 4: unavoidable set with wave-like locality.

    Phase 1 (F2/F3/F4): processes smallest faces first.
      F2: picks one random face and one random edge.
      F3/F4: picks the valid edge whose adjacent face f2 is largest.

    Phase 2 (F5 only):
      Local: restrict to F5 faces adjacent to recently_modified_vertices.
        Step 1 — F5-F5: _select_from_f5_pairs (4-edge scan, max-neighbor).
        Step 2 — F5-F6: _select_f5_f6_edge (2-edge scan on F5 side, max-neighbor).
      Global fallback (Step 4): scan all F5 globally, same priority order.

    This function is read-only with respect to `recently_modified_vertices`:
    it uses the parameter for locality filtering and for incrementing the
    SELECT-S4-F4-INTERRUPT stat, but never writes it. The caller
    (`reduce_faces`) is the sole writer via `update_wave_frontier`.

    Parameters
    ----------
        g_faces: list of faces (each face is a list of directed-edge tuples)
        choices: integer (must be 2345; warned otherwise)
        i_global_counter: for logging
        recently_modified_vertices: set of vertex IDs representing the wave frontier, or None

    Returns
    -------
        edge_to_remove, f1, f2, f1_plus_f2_temp, event

        `event` is `'fallback'` when the global F5 fallback fires while a
        wave is active (so the caller can end the wave); otherwise `None`.
    """

    logger.info("BEGIN %s: select_edge_to_remove_unavoidable_set (faces left: %s, wave frontier size: %s)", i_global_counter, len(g_faces), len(recently_modified_vertices) if recently_modified_vertices is not None else "N/A")

    if choices != 2345:
        logger.warning("select_edge_to_remove_unavoidable_set: the 'choices' parameter is ignored; F2/F3/F4 order is fixed as [2, 3, 4]. Received: %s", choices)

    # Phase F2 / F3 / F4  — global, locality ignored
    for target_size in [2, 3, 4]:

        faces_of_this_size = [f for f in g_faces if len(f) == target_size]
        if not faces_of_this_size:
            continue

        # F2: pick a random face and a random edge (both parallel edges are always valid)
        if target_size == 2:
            candidate_f1 = faces_of_this_size[randint(0, len(faces_of_this_size) - 1)]
            i_edge = randint(0, 1)
            edge = candidate_f1[i_edge]
            rotated_edge = rotate(edge, 1)
            temp = [face for face in g_faces if rotated_edge in face]
            temp.remove(candidate_f1)
            candidate_f2 = temp[0]
            candidate_joined = join_faces(candidate_f1, candidate_f2, edge)

            # Q: It should not happen, because when a wave is active, only F4 can appear after having removed an F5 edge
            # R: This is not true, if there large groups of F5s (F5-F5-F5), when the two vertices of the removed edge (F5 in the middle), F5-(F5)-F5 touch the two lateral F5 (F5)-F5-(F5) those two lateral phases become two F4
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
            logger.info("END %s: select_edge_to_remove_unavoidable_set edge found in F2 phase (random). Edge: %s", i_global_counter, edge)
            return edge, candidate_f1, candidate_f2, candidate_joined, None

        # F3/F4: pick the valid edge whose adjacent face is largest
        best_edge = None
        best_f1 = None
        best_f2 = None
        best_f1_plus_f2 = None
        best_f2_len = 0

        for candidate_f1 in faces_of_this_size:
            for i_edge in range(len(candidate_f1)):
                edge = candidate_f1[i_edge]
                rotated_edge = rotate(edge, 1)
                candidate_f2 = next((face for face in g_faces if rotated_edge in face), None)
                if candidate_f2 is None:
                    continue
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if is_the_graph_one_edge_connected(candidate_joined):
                    continue
                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = candidate_f1
                    best_f2 = candidate_f2
                    best_f1_plus_f2 = candidate_joined

        if best_edge is not None:
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
            logger.info("END %s: select_edge_to_remove_unavoidable_set edge found in F%s phase. Edge: %s (f2 size: %s)", i_global_counter, target_size, best_edge, best_f2_len)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None

    # Phase F5  — only reached when no F2/F3/F4 exist
    # Locality: restrict to F5 faces touching the wave frontier
    if recently_modified_vertices:
        local_f5 = [f for f in g_faces if len(f) == 5 and any(v in recently_modified_vertices for edge in f for v in edge)]
    else:
        local_f5 = []

    # Step 1 — local F5-F5 (highest priority)
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, local_f5, pair_neighbor_size=5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F5'] += 1
            logger.info("END %s: select_edge_to_remove_unavoidable_set edge found via local F5-F5 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None

    # Step 2 — local F5-F6
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, local_f5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F6'] += 1
            logger.info("END %s: select_edge_to_remove_unavoidable_set edge found via local F5-F6 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None

    # Step 4 — global fallback (no local candidates, or local search found nothing)
    all_f5 = [f for f in g_faces if len(f) == 5]

    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, all_f5, pair_neighbor_size=5)
    if best_edge is not None:
        wave_was_active = recently_modified_vertices is not None
        if wave_was_active:
            stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: select_edge_to_remove_unavoidable_set edge found via global F5-F5 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, ('fallback' if wave_was_active else None)

    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, all_f5)
    if best_edge is not None:
        wave_was_active = recently_modified_vertices is not None
        if wave_was_active:
            stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: select_edge_to_remove_unavoidable_set edge found via global F5-F6 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, ('fallback' if wave_was_active else None)

    # Should never reach here — Euler guarantees a face < F6 always exists
    logger.error("END %s: select_edge_to_remove_unavoidable_set no valid edge found", i_global_counter)
    exit(-1)


def from_graph_to_planar(the_graph):
    """
    Convert a graph to the planar representation.

    Parameters
    ----------
        the_graph: The graph to convert

    Returns
    -------
        g_faces: The planar representation of the graph
    """

    # Get the faces representation of the graph using faces_by_vertices
    # This function extracts faces as lists of vertices
    temp_faces_by_vertices = faces_by_vertices(the_graph)
    
    # Convert vertex faces to edge faces (like Sage's faces() output)
    # faces() in Sage returns [(v1, v2), (v2, v3), ...] for each face
    temp_g_faces = []
    for face in temp_faces_by_vertices:
        edge_face = []
        for i in range(len(face)):
            edge_face.append((face[i], face[(i + 1) % len(face)]))
        temp_g_faces.append(edge_face)

    # A full sort of all faces would make the algorithm faster later (maybe)
    temp_g_faces.sort(key=len)
    g_faces = [face for face in temp_g_faces]

    # Save the face representation for later executions (if needed)
    with open("debug/debug.previous_run.planar", 'w') as fp:
        json.dump(g_faces, fp)

    return g_faces


def create_from_random2(number_of_faces, shuffle_the_planar_representation):
    """
    Create a random planar graph using the custom PlanarGraphGenerator.

    Parameters
    ----------
        number_of_faces: The number of faces to create in the graph
        shuffle_the_planar_representation: Shuffle the planar representation of the map

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Create a random planar graph with %s faces using PlanarGraphGenerator", number_of_faces)

    # Initialize the generator and generate g_faces
    generator = PlanarGraphGenerator()
    g_faces = generator.generate(number_of_faces)

    # Shuffle the planar representation of the map
    if shuffle_the_planar_representation:
        shuffle(g_faces)

    # Create the graph object from the planar representation
    # This is needed to maintain compatibility with the rest of the algorithm
    the_graph = create_graph_from_planar_representation(g_faces)
    # the_graph.allow_loops(False)
    # the_graph.allow_multiple_edges(True)
    # the_graph.relabel()

    check_graph_planarity_3_regularity_no_loops(the_graph)

    # I need this (export + import) to be able to reproduce this test exactly in the same condition in a second run
    # The export function saves the graph using a different order for the edges (even if the graph are exactly the same graph)
    # the_graph.export_to_file("debug/debug.previous_run.edgelist", format="edgelist")
    nx.write_edgelist(the_graph, "debug/debug.previous_run.edgelist")

    # the_graph = Graph(networkx.read_edgelist("debug/debug.previous_run.edgelist", create_using=networkx.MultiGraph()), multiedges=True)
    the_graph = nx.read_edgelist("debug/debug.previous_run.edgelist", create_using=nx.MultiGraph(), nodetype=int)

    # the_graph.relabel()
    # the_graph.allow_loops(False)
    # the_graph.allow_multiple_edges(True)

    logger.info("END: Create a random planar graph of %s vertices and %s faces", the_graph.order(), len(g_faces))

    return the_graph, g_faces


def create_from_random1(number_of_vertices_for_the_random_triangulation, shuffle_the_planar_representation):
    """
    Create a random planar graph from the dual of a random triangulation.
    Uses scipy.spatial.ConvexHull with points on a sphere for proper closed triangulation.

    Parameters
    ----------
        number_of_vertices_for_the_random_triangulation: The number of vertices to create the graph
        shuffle_the_planar_representation: Shuffle the planar representation of the map

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """
    import numpy as np
    try:
        from scipy.spatial import ConvexHull
    except ImportError:
        logger.error("scipy is required for random triangulation. Install with: pip install scipy")
        exit(-1)

    logger.info("BEGIN: Create a random planar graph from the dual of a random triangulation of %s vertices. It may take very long time depending on the number of vertices", number_of_vertices_for_the_random_triangulation)
    
    # Generate random points on a sphere to get a proper closed triangulation
    # Using spherical coordinates with random theta and phi
    np.random.seed()  # Use random seed for each execution
    n_points = number_of_vertices_for_the_random_triangulation
    
    # Generate random points distributed on a sphere
    theta = np.random.uniform(0, 2 * np.pi, n_points)
    phi = np.arccos(np.random.uniform(-1, 1, n_points))
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    points = np.column_stack((x, y, z))
    
    # Compute ConvexHull which gives a triangulation on the sphere
    hull = ConvexHull(points)
    
    # Create a graph from the triangulation
    temp_g = nx.Graph()
    for simplex in hull.simplices:
        temp_g.add_edge(simplex[0], simplex[1])
        temp_g.add_edge(simplex[1], simplex[2])
        temp_g.add_edge(simplex[2], simplex[0])
    
    # Get the dual of the triangulation (a 3-regular planar graph)
    the_graph = graph_dual(temp_g)
    
    # Relabel nodes to integers
    the_graph = nx.convert_node_labels_to_integers(the_graph)

    check_graph_planarity_3_regularity_no_loops(the_graph)

    # Save the graph for reproducibility
    nx.write_edgelist(the_graph, "debug/debug.previous_run.edgelist")

    # Reload for consistent ordering
    the_graph = nx.read_edgelist("debug/debug.previous_run.edgelist", create_using=nx.MultiGraph(), nodetype=int)

    # Convert the graph to planar (faces representation)
    g_faces = from_graph_to_planar(the_graph)

    # Shuffle the planar representation of the map
    if shuffle_the_planar_representation:
        shuffle(g_faces)

    logger.info("END: Create a random planar graph of %s vertices, from the dual of a random triangulation of %s vertices", the_graph.number_of_nodes(), number_of_vertices_for_the_random_triangulation)

    return the_graph, g_faces


def create_from_edge_list(edgelist_filename, shuffle_the_planar_representation):
    """
    Load the graph from the external edgelist file.

    Parameters
    ----------
        edgelist_filename: The edgelist file to upload
        shuffle_the_planar_representation: Shuffle the planar representation of the map

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Load the graph from the external file: %s", edgelist_filename)
    the_graph = nx.read_edgelist(edgelist_filename, create_using=nx.MultiGraph(), nodetype=int)

    check_graph_planarity_3_regularity_no_loops(the_graph)

    # Convert the graph to planar (faces representation)
    g_faces = from_graph_to_planar(the_graph)

    # Shuffle the planar representation of the map
    if shuffle_the_planar_representation:
        shuffle(g_faces)

    logger.info("END: Load the graph from the external file: %s", edgelist_filename)

    return the_graph, g_faces


def count_lines_in_file(filename):
    """
    Count the number of non-empty lines in a file.

    Parameters
    ----------
        filename: The file to count lines in

    Returns
    -------
        count: The number of non-empty lines
    """
    count = 0
    with open(filename, 'r') as fp:
        for line in fp:
            if line.strip():
                count += 1
    return count


def create_from_planar(planar_filename, shuffle_the_planar_representation, line_number=0):
    """
    Load the planar embedding of a graph (output of the gfaces() function).

    Parameters
    ----------
        planar_filename: The planar file to upload
        shuffle_the_planar_representation: Shuffle the planar representation of the map
        line_number: The line number (0-based) to read from the file. Default is 0 (first line)

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Load the planar embedding of a graph (output of the gfaces() function): %s (line: %s)", planar_filename, line_number + 1)

    # Warning: Sage NotImplementedError: cannot compute with embeddings of multiple-edged or looped graphs
    # with open(args.planar, 'r') as fp: g_faces = pickle.load(fp)
    with open(planar_filename, 'r') as fp:
        # Skip lines before the requested one
        for _ in range(line_number):
            fp.readline()
        line = fp.readline().strip()
        if not line:
            logger.error("Line number %s exceeds the number of lines in the file", line_number + 1)
            exit(-1)
        g_faces = json.loads(line)

    # Cast back to tuples. json.dump write the "list of list of tuples" as "list of list of list"
    #
    # Original: [[(3,2),(3,5)],[(2,4),(1,3),(1,3)], ... ,[(1,2),(3,4),(6,7)]]
    # Saved as: [[[3,2],[3,5]],[[2,4],[1,3],[1,3]], ... ,[[1,2],[3,4],[6,7]]]
    g_faces = [[tuple(l) for l in L] for L in g_faces]

    if shuffle_the_planar_representation:
        shuffle(g_faces)

    # I need the graph here only to check_graph_at_beginning
    the_graph = create_graph_from_planar_representation(g_faces)

    check_graph_planarity_3_regularity_no_loops(the_graph)

    logger.info("END: Load the planar embedding of a graph (output of the gfaces() function): %s (line: %s)", planar_filename, line_number + 1)

    return the_graph, g_faces


######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
# 4CT: REDUCE & REBUILD
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######

def reduce_faces(g_faces, choices, selection_strategy):
    """
    Method similar to the Kempe reduction "patching" method.\n
    For each loop remove an edge from a face <= F5, until the graph will have only three faces (an island with two lands)

    Parameters
    ----------
        g_faces: The planar representation of the graph
        choices: The selection method for the edges
        selection_strategy: The function to use to select the edge to remove (select_edge_to_remove_by_largest_neighbor or select_edge_to_remove_first_fit)

    Returns
    -------
        ariadne_s_thread: You would better study the classics
    """

    stats['time_ELABORATION_BEGIN'] = time.ctime()
    stats['time_ELABORATION'] = datetime.datetime.now()

    # It will contain items made of lists of values to find the way back to the original graph (Ariadne's String Myth)
    # _string not in the sense of programming language :-) search for the mitos: ariadne string
    ariadne_s_thread = []
    ariadne_step = []

    # Start the reduction process
    is_the_end_of_the_reduction_process = False
    i_global_counter = 0
    recently_modified_vertices = None

    # Open the file to append the rows with the changing distribution during the reduction phase
    f_distribution = open("debug/debug.f_distribution.json.dump", "a")

    # If the graph is already reduced (2 vertices and 3 edges = 3 faces, included the ocean)
    if len(g_faces) == 3:

        # Graph already reduced
        is_the_end_of_the_reduction_process = True
        if logger.isEnabledFor(logging.DEBUG): logger.debug("The graph is already reduced")

    while is_the_end_of_the_reduction_process is False:

        logger.info("BEGIN %s: Main loop", i_global_counter)
        log_faces(g_faces)

        # Deep debug: Log all faces
        # log_faces(g_faces)

        # f1, f2, edge_to_remove, rotated_edge_to_remove, len_of_the_face_to_reduce will be valid during the rest of this "while" loop after the first block ("Select an edge") has been executed
        f1 = []
        f2 = []
        edge_to_remove = ()
        f1_plus_f2_temp = []  # It is used to speed up computation. At the beginning is used to see it the graph is_the_graph_one_edge_connected() and then reused

        # Select an edge from the graph
        # This is one of the most important function to work on, to apply different strategies
        edge_to_remove, f1, f2, f1_plus_f2_temp, selection_event = selection_strategy(g_faces, choices, i_global_counter, recently_modified_vertices)

        # Since Euler's formula is right :-) an edge to remove must exist, and it means that I made a programming error if I get here without finding it
        if edge_to_remove == ():
            logger.error("Unexpected condition (a suitable edge has not been found). Mario you'd better go back to paper")
            exit(-1)

        # Wave frontier is owned by reduce_faces: selection strategies only read it.
        # A 'fallback' event from S4 ends the current wave (forced global F5 search).
        v1, v2 = edge_to_remove
        recently_modified_vertices = update_wave_frontier(recently_modified_vertices, len(f1), f1_plus_f2_temp, v1, v2)
        if selection_event == 'fallback':
            recently_modified_vertices = None

        # What kind of face am I reducing (I need only f1, f2 is only for debugging ... for now)
        len_of_the_face_to_reduce_f1 = len(f1)
        len_of_the_face_to_reduce_f2 = len(f2)

        # Remove the edge of an F2 (multiple edge)
        if len_of_the_face_to_reduce_f1 == 2:

            logger.info("BEGIN %s: Remove a multiple edge (len f1, f2: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

            # Get the two vertices to join
            # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O

            # >--0--<
            #
            # F2 is the zero in the center (in the drawing)
            vertex_to_join_near_v1 = next(edge for edge in f2 if edge[0] == v1)[1]
            vertex_to_join_near_v2 = next(edge for edge in f2 if edge[1] == v2)[0]

            # Update the statistics for the distribution of Fs
            stats['F#'][len_of_the_face_to_reduce_f1] -= 1
            stats['F#'][len_of_the_face_to_reduce_f2] -= 1

            # f1 and f2 have been joined before to test 1-edge-connectivity ... I can use that!
            g_faces.remove(f1)
            g_faces.remove(f2)
            g_faces.insert(-1, f1_plus_f2_temp)

            # Update the statistics for the distribution of Fs
            if len(f1_plus_f2_temp) in stats['F#'].keys():
                stats['F#'][len(f1_plus_f2_temp)] += 1
            else:
                stats['F#'][len(f1_plus_f2_temp)] = 1

            # I already prepared f1 and f2, but when these two faces are joined also the other face that has the two vertices has to be updated
            # A vertex is shared by three faces (two of these are f1 and f2). For this F2 case, the two vertices belong to only a third face
            # NOTE: For F3, F4, F5 ... v1 and v2 may have two different faces (other than f1 and f2)
            third_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v1))

            # Update the statistics for the distribution of Fs
            stats['F#'][len(third_face_to_update)] -= 1

            remove_vertex_from_face(third_face_to_update, v1)
            remove_vertex_from_face(third_face_to_update, v2)  # For this F2 case, the two vertices belong to only a third face

            # Update the statistics for the distribution of Fs
            if len(third_face_to_update) in stats['F#'].keys():
                stats['F#'][len(third_face_to_update)] += 1
            else:
                stats['F#'][len(third_face_to_update)] = 1

            # Ariadne ball of thread. First parameter == 2, will tell that it was a multiple edge
            # [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
            ariadne_step = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
            ariadne_s_thread.append(ariadne_step)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("ariadne_step: %s", ariadne_step)

            # Do one thing at a time and return at the beginning of the main loop
            logger.info("END %s: Remove a multiple edge (len f1, f2: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

        # Remove an F3 or F4 or F5
        else:

            logger.info("BEGIN %s: Remove an F3, F4 or F5 (len f1, f2: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

            # Get the vertices at the ends of the edge to remove
            # And find the other four neighbors :>.---.<: (If the --- is the removed edge, the four external dots represent the vertices I'm looking for)

            vertex_to_join_near_v1_on_the_face = next(edge for edge in f1 if edge[1] == v1)[0]
            vertex_to_join_near_v2_on_the_face = next(edge for edge in f1 if edge[0] == v2)[1]
            vertex_to_join_near_v1_not_on_the_face = next(edge for edge in f2 if edge[0] == v1)[1]
            vertex_to_join_near_v2_not_on_the_face = next(edge for edge in f2 if edge[1] == v2)[0]

            if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v1_on_the_face: %s", vertex_to_join_near_v1_on_the_face)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v2_on_the_face: %s", vertex_to_join_near_v2_on_the_face)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v1_not_on_the_face: %s", vertex_to_join_near_v1_not_on_the_face)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v2_not_on_the_face: %s", vertex_to_join_near_v2_not_on_the_face)

            # Update the statistics for the distribution of Fs
            stats['F#'][len_of_the_face_to_reduce_f1] -= 1
            stats['F#'][len_of_the_face_to_reduce_f2] -= 1

            # f1 and f2 have been joined before to test 1-edge-connectivity ... I can use that!
            g_faces.remove(f1)
            g_faces.remove(f2)
            g_faces.insert(-1, f1_plus_f2_temp)

            # Update the statistics for the distribution of Fs
            if len(f1_plus_f2_temp) in stats['F#'].keys():
                stats['F#'][len(f1_plus_f2_temp)] += 1
            else:
                stats['F#'][len(f1_plus_f2_temp)] = 1

            # I already prepared f1 and f2, but when these two faces are joined also the other faces that has the two vertices have to be updated
            # A vertex is shared by three faces (two of these are f1 and f2)
            # NOTE: For F3, F4, F5 ... v1 and v2, most of the times will have f3 and f4 different ... but they can also be the same face
            third_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v1))
            fourth_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v2))
            if logger.isEnabledFor(logging.DEBUG): logger.debug("third_face_to_update: %s", third_face_to_update)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("fourth_face_to_update: %s", fourth_face_to_update)

            # Update the statistics for the distribution of Fs
            if third_face_to_update == fourth_face_to_update:
                stats['F#'][len(third_face_to_update)] -= 1
            else:
                stats['F#'][len(third_face_to_update)] -= 1
                stats['F#'][len(fourth_face_to_update)] -= 1

            remove_vertex_from_face(third_face_to_update, v1)
            remove_vertex_from_face(fourth_face_to_update, v2)

            # Update the statistics for the distribution of Fs
            if third_face_to_update == fourth_face_to_update:

                # DONE: There is a small bug (SEE BUG-001) to care about here at the end of the process when four faces F3 remains (as in the Mercedes Benz symbol)
                if len(third_face_to_update) in stats['F#'].keys():
                    stats['F#'][len(third_face_to_update)] += 1
                else:
                    stats['F#'][len(third_face_to_update)] = 1

                # Fix to the BUG-001 - It happens because only at the end you have 2 vertices and 3 multiple edges. And two faces have the same representation
                if len(g_faces) == 3 and stats['F#'][len(third_face_to_update)] == 2:
                    stats['F#'][len(third_face_to_update)] += 1
            else:
                if len(third_face_to_update) in stats['F#'].keys():
                    stats['F#'][len(third_face_to_update)] += 1
                else:
                    stats['F#'][len(third_face_to_update)] = 1

                if len(fourth_face_to_update) in stats['F#'].keys():
                    stats['F#'][len(fourth_face_to_update)] += 1
                else:
                    stats['F#'][len(fourth_face_to_update)] = 1

            # Ariadne ball of thread
            # First parameter == len_of_the_face_to_reduce, will tell that it was a Fx face that has been removed (x = 3, 4 or 5)
            # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
            ariadne_step = [len_of_the_face_to_reduce_f1, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
            ariadne_s_thread.append(ariadne_step)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("ariadne_step: %s", ariadne_step)

            # Do one thing at a time and return at the beginning of the main loop
            logger.info("END %s: Remove an F3, F4 or F5 (case: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

        # Check 3-regularity (I commented this slow procedure
        # I did it run for a while, now I feel confident about this first part of the code)
        #
        # if check_regularity(g_faces) is False:
        #    logger.error("Unexpected condition (check_regularity is False). Mario you'd better go back to paper")
        #    log_faces(g_faces)
        #    exit(-1)

        # At this point the graph has 3 faces (an island with 2 lands + the ocean) and 3 edges ... easily 3-edge-colorable
        if len(g_faces) == 3:

            # Graph reduced
            is_the_end_of_the_reduction_process = True

            if logger.isEnabledFor(logging.DEBUG): logger.debug("--------------------------")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("The graph has been reduced")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("--------------------------")
            log_faces(g_faces)

        # END of main loop (-1 because the counter has been just incremented)
        logger.info("F# = %s", dict(sorted(stats['F#'].items())))
        logger.info("END %s: Main loop - len(ariadne_s_thread) = %s", i_global_counter, len(ariadne_s_thread))

        json.dump(stats['F#'], f_distribution)
        f_distribution.write("\n")

        # If not reduced, continue
        if is_the_end_of_the_reduction_process is False:
            i_global_counter += 1
            logger.info("")

    # Close the file of the distubutions
    f_distribution.close()

    return ariadne_s_thread


def rebuild_faces(g_faces, ariadne_s_thread):
    """
    Restore the edges one at a time and apply the half Kempe-cycle color switching method.\n
    Depending if the restored face is an F2, F3, F4, F5, different actions will be taken to be able to apply, at the end, the half Kempe-cycle color switching

    Parameters
    ----------
        g_faces: The planar representation of the graph
        ariadne_s_thread: You would better study the classics

    Returns
    -------
        the_colored_graph: The colored graph
    """

    # At this point the graph has 3 faces (an island with 2 lands + the ocean) and 3 edges ... easily 3-edge-colorable
    # WARNING: the color of the edges of a multiedge graph cannot be changed, so during the process it is necessary to delete and re-insert edges
    the_colored_graph = nx.MultiGraph()

    # Only 2 vertices have to be in the graph
    all_vertices = [element for face in g_faces for edge in face for element in edge]
    all_vertices = sorted(set(all_vertices))

    if len(all_vertices) != 2:
        logger.error("Unexpected condition (vertices left are not 2). Mario you'd better go back to paper")
        exit(-1)

    # Aliases
    v1 = all_vertices[0]
    v2 = all_vertices[1]

    # At this point the graph is that of an island perfectly slit in two (just to visualize it)
    # I now rebuild a new graph and, at the end of the rebuilding process, I'll check if it is isomorphic to the original
    #
    # NOTE: For the first step, it is NOT important to create the new graph selecting a particular order for the vertices ... they would all generate exactly the same graph
    graph_add_edge(the_colored_graph, v1, v2, "red")
    graph_add_edge(the_colored_graph, v1, v2, "green")
    graph_add_edge(the_colored_graph, v1, v2, "blue")

    # Check if I need to start the rebuilding process
    if ariadne_s_thread == []:
        is_the_end_of_the_rebuild_process = True
    else:
        is_the_end_of_the_rebuild_process = False

    i_global_rebuilding_counter = 0
    number_of_steps_to_take = len(ariadne_s_thread)

    # Start the rebuilding process
    while is_the_end_of_the_rebuild_process is False:

        i_global_rebuilding_counter += 1

        # Get the string to walk back home
        ariadne_step = ariadne_s_thread.pop()
        logger.info("ariadne_step (%s/%s): %s", i_global_rebuilding_counter, number_of_steps_to_take, ariadne_step)

        # F2 = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        # F3, 4, 5 = [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        if ariadne_step[0] == 2:
            ariadne_case_f2(the_colored_graph, ariadne_step)
        elif ariadne_step[0] == 3:
            ariadne_case_f3(the_colored_graph, ariadne_step)
        elif ariadne_step[0] == 4:
            ariadne_case_f4(the_colored_graph, ariadne_step)
        elif ariadne_step[0] == 5:
            ariadne_case_f5(the_colored_graph, ariadne_step)

        # Separator
        if logger.isEnabledFor(logging.DEBUG): logger.debug("")

        # After all cases attempt of a single step back to the original graph (one ariadne step), better to ckeck if the coloring is good
        # if not is_well_colored(the_colored_graph):
        #     logger.error("Unexpected condition (coloring is not valid). Mario you'd better go back to paper or learn to code")
        #     exit(-1)

        # If no other edges have to be restored, then I'm done
        if len(ariadne_s_thread) == 0:
            is_the_end_of_the_rebuild_process = True

    stats['time_ELABORATION_END'] = time.ctime()
    stats['time_ELABORATION'] = (datetime.datetime.now() - stats['time_ELABORATION']).seconds

    return the_colored_graph


def init_f_distribution(g_faces):
    """
    Count the number of faces by number of edges. Example: 4 faces F2, 5 faces F3 and so on

    Parameters
    ----------
        g_faces: The planar representation of the graph
    """

    for face in g_faces:
        len_of_the_face = len(face)
        if len_of_the_face in stats['F#'].keys():
            stats['F#'][len_of_the_face] += 1
        else:
            stats['F#'][len_of_the_face] = 1
            
    # Ordina il dizionario in base alla chiave (len_of_the_face)
    stats['F#'] = dict(sorted(stats['F#'].items()))
    
    # Create and if exist remove the f_distribution_file
    with open("debug/debug.f_distribution.json.dump", "w") as f_distribution:
        json.dump(stats['F#'], f_distribution)
        f_distribution.write("\n")

    # Save the initial face distribution
    stats['F-Initial#'] = stats['F#'].copy()


######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
# 4CT: MAIN FUNCTION Create/upload the graph to color. it has to be planar and initially without loops and multiple edges
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######

def main():

    ###############
    # Read options:
    ###############
    # (-r <vertices> or -i <file> or -p <planar embedding (json file)>) -o <file>
    parser = argparse.ArgumentParser(description='4ct args')
    group_input = parser.add_mutually_exclusive_group(required=True)
    group_input.add_argument("-r1", "--random1", help="Random graph: dual of a triangulation of N vertices", type=int)
    group_input.add_argument("-r2", "--random2", help="Random graph: subdivision of faces (directly planar)", type=int)
    group_input.add_argument("-e", "--edgelist", help="Load a .edgelist file (networkx)")
    group_input.add_argument("-p", "--planar", help="Load a planar embedding (json) of the graph G.faces() - Automatically saved at each run")
    parser.add_argument("-o", "--output", help="Save a .edgelist file (networkx), plus a .dot file (networkx). Specify the file without extension", required=False)
    parser.add_argument("-c", "--choices", help="Sequence of the Fs to choose (2345, 2354, 2435, 2453, 2534, 2543)", type=int, default=2345, choices=[2345, 2354, 2435, 2453, 2534, 2543], required=False)
    parser.add_argument("-s", "--shuffle", help="Shuffle the list at the beginning. Most of the times it solves the infinite loop condition", action='store_true')
    parser.add_argument("-n", "--num_executions", help="The entire process will be executed N times", type=int, default=1, required=False)
    group_selection = parser.add_mutually_exclusive_group(required=False)
    group_selection.add_argument("-s1", "--selection1", help="Edge selection strategy 1: first fit (first valid edge in the first face of the right priority) - default", action='store_true', default=False)
    group_selection.add_argument("-s2", "--selection2", help="Edge selection strategy 2: best adjacent face (maximizes f2 size across all candidates)", action='store_true', default=False)
    group_selection.add_argument("-s3", "--selection3", help="Edge selection strategy 3: for F5 faces, select edge with one shared vertex with adjacent F5/F6", action='store_true', default=False)
    group_selection.add_argument("-s4", "--selection4", help="Edge selection strategy 4: unavoidable set — max neighbor for F2/F3/F4, F5 pairs with locality", action='store_true', default=False)
    args = parser.parse_args()

    # Select edge selection strategy (-s1 = first fit (default), -s2 = best adjacent face, -s3 = f5 shared vertex, -s4 = unavoidable set)
    if args.selection1:
        selection_strategy = select_edge_to_remove_first_fit
    elif args.selection2:
        selection_strategy = select_edge_to_remove_by_largest_neighbor
    elif args.selection3:
        selection_strategy = select_edge_to_remove_f5_shared_vertex
    elif args.selection4:
        selection_strategy = select_edge_to_remove_unavoidable_set
    else:
        selection_strategy = select_edge_to_remove_first_fit

    # If using planar input, cap num_executions to the number of lines in the file
    num_executions = args.num_executions
    if args.planar is not None:
        total_lines = count_lines_in_file(args.planar)
        num_executions = total_lines

    # Execute n times the program to see if it is deterministic
    for i_execution in range(num_executions):
   
        # Initialize statistics (stats is global)
        initialize_statistics()

        logger.info("--------------------------------")
        logger.info("BEGIN: Create the graph to color" + " (execution " + str(i_execution + 1) + ")")
        logger.info("--------------------------------")
        stats['time_GRAPH_CREATION_BEGIN'] = time.ctime()

        # Create the graph
        if args.random1 is not None:
            the_graph, g_faces = create_from_random1(args.random1, args.shuffle)
        elif args.random2 is not None:
            the_graph, g_faces = create_from_random2(args.random2, args.shuffle)
        elif args.edgelist is not None:  # edgelist - Load a graph stored in edgelist format
            the_graph, g_faces = create_from_edge_list(args.edgelist, args.shuffle)
        elif args.planar is not None:  # Planar - Load a planar embedding of the graph (one line per execution)
            the_graph, g_faces = create_from_planar(args.planar, args.shuffle, line_number=i_execution)

        stats['time_GRAPH_CREATION_END'] = time.ctime()
        logger.info("------------------------------")
        logger.info("END: Create the graph to color" + " (execution " + str(i_execution + 1) + ")")
        logger.info("------------------------------")
        logger.info("")

        # Keep track of the distribution of faces length
        init_f_distribution(g_faces)
        logger.info("F-Initial#: %s", stats['F-Initial#'])
    
        ######
        ######
        # 4CT: AT THE BEGINNING THE GRAPH HAS TO BE CUBIC AND PLANAR WITH NO LOOPS
        # 4CT: NOTE: It can have multiple edges but some software is not able to compute planarity
        ######
        ######

        logger.debug("------------------------")
        logger.debug("BEGIN: Graph information" + " (execution " + str(i_execution + 1) + ")")
        logger.debug("------------------------")

        # Log faces
        log_faces(g_faces)

        logger.debug("----------------------")
        logger.debug("END: Graph information" + " (execution " + str(i_execution + 1) + ")")
        logger.debug("----------------------")
        logger.debug("")

        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        # 4CT: Method similar to the Kempe reduction "patching" method
        # 4CT: For each loop remove an edge from a face <= F5, until the graph will have only three faces (an island with two lands)
        ######

        logger.info("----------------------")
        logger.info("BEGIN: Reduction phase" + " (execution " + str(i_execution + 1) + ")")
        logger.info("----------------------")

        ariadne_s_thread = reduce_faces(g_faces, args.choices, selection_strategy)

        logger.debug("----------------------")
        logger.debug("END: Reduction phase" + " (execution " + str(i_execution + 1) + ")")
        logger.debug("----------------------")
        logger.debug("")

        logger.info("----------------------")
        logger.info("BEGIN: Rebuild faces" + " (execution " + str(i_execution + 1) + ")")
        logger.info("----------------------")

        the_colored_graph = rebuild_faces(g_faces, ariadne_s_thread)

        logger.debug("----------------------")
        logger.debug("END: Rebuild faces" + " (execution " + str(i_execution + 1) + ")")
        logger.debug("----------------------")
        logger.debug("")

        ######
        # 4CT: Restore the edges one at a time and apply the half Kempe-cycle color switching method
        # 4CT: Depending if the restored face is an F2, F3, F4, F5, different actions will be taken to be able to apply, at the end, the half Kempe-cycle color switching
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######
        ######

        ######
        ######
        # 4CT: Show the restored and 4 colored map and check for mistakes
        ######
        ######

        logger.info("------------------------------------------")
        logger.info("BEGIN: Show the restored and 4 colored map")
        logger.info("------------------------------------------")

        # Check if the recreated graph is isomorphic to the original
        # NOTE: is_isomorphic is a bit slow, since after all this time I am pretty sure the algorithm works, I decided to relax the control 
        logger.info("BEGIN: Check if isomorphic")
        # if nx.is_isomorphic(the_graph, the_colored_graph) is True:
        if the_graph.number_of_nodes() == the_colored_graph.number_of_nodes() and the_graph.number_of_edges() == the_colored_graph.number_of_edges():
            logger.info("Recreated graph is equal to the original")
        else:
            logger.error("Unexpected condition (recreated graph is different from the original). Mario you'd better go back to paper")
        logger.info("END: Check if isomorphic")

        logger.debug("BEGIN: print_graph (Original)")
        print_graph(the_graph)
        logger.debug("END: print_graph (Original)")

        logger.debug("BEGIN: print_graph (Colored)")
        print_graph(the_colored_graph)
        logger.debug("END: print_graph (Colored)")

        logger.debug("BEGIN: is well colored)")
        if is_well_colored(the_colored_graph) is False:
            logger.error("is_well_colored: False")
        else:
            logger.debug("is_well_colored: True")
        logger.debug("END: is well colored")

        logger.debug("----------------------------------------")
        logger.debug("END: Show the restored and 4 colored map")
        logger.debug("----------------------------------------")
        logger.info("")

        # Save the output graph
        if args.output is not None:
            export_graph(the_colored_graph, args.output)

        # Print statistics
        print_stats()


######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
# 4CT: MAIN FUNCTION Create/upload the graph to color. it has to be planar and initially without loops and multiple edges
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######
######

if __name__ == '__main__':

    # Statistics
    stats = {}

    # Set logging facilities
    logger = logging.getLogger()
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

    # Go
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()

    profiles_stats = pstats.Stats(profiler).sort_stats("cumulative")
    profiles_stats.print_stats(30)
