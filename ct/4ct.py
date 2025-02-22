#!/usr/bin/env sage

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
# - TODO: Get rid of sage
# - TODO: Fix docstring for each function
#
# BACKLOG to evaluate:
# - TODO: Realize the reconstruction phase with the lists of the edge representation instead of using the graph. It will probably be a lot faster, and won't need sage!
#
# Done:
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
from random import shuffle

import networkx
from sage.all import *

from ct.ct_graph_utils import check_graph_planarity_3_regularity_no_loops
from ct.ct_graph_utils import kempe_chain_color_swap
from ct.ct_graph_utils import graph_dual
from ct.ct_graph_utils import print_graph
from ct.ct_graph_utils import is_well_colored
from ct.ct_graph_utils import get_edge_color
from ct.ct_graph_utils import is_multiedge
from ct.ct_graph_utils import check_if_vertex_is_in_face
from ct.ct_graph_utils import create_graph_from_planar_representation
from ct.ct_graph_utils import export_graph
from ct.ct_graph_utils import are_edges_on_the_same_kempe_cycle
from ct.ct_graph_utils import apply_half_kempe_loop_color_switching
from ct.ct_graph_utils import remove_vertex_from_face
from ct.ct_graph_utils import rotate
from ct.ct_graph_utils import join_faces
from ct.ct_graph_utils import is_the_graph_one_edge_connected
from ct.ct_graph_utils import get_the_other_colors
from ct.ct_graph_utils import log_faces
from ct.ct_graph_utils import log_faces_info

from numpy.random import randint


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
# 4CT: BUGS
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

# BEGIN BUG-001
#
# BAD:
# ----
# 2020-04-12 14:59:17,282 - root - INFO - END 94: Main loop - len(ariadne_s_thread) = 95
# 2020-04-12 14:59:17,283 - root - INFO - BEGIN 95: Main loop
# 2020-04-12 14:59:17,283 - root - INFO - BEGIN 95: Search the right edge to remove (faces left: 5)
# 2020-04-12 14:59:17,283 - root - INFO - END 95: Search the right edge to remove. Found: (129, 194) (case: 3, 4)
# 2020-04-12 14:59:17,283 - root - INFO - BEGIN 95: Remove an F3, F4 or F5 (case: 3, 4)
# 2020-04-12 14:59:17,283 - root - INFO - XXXXXX. f3: [(73, 180), (180, 56), (56, 73)], f4: [(73, 56), (56, 185), (185, 73)]
# 2020-04-12 14:59:17,283 - root - INFO - END 95: Remove an F3, F4 or F5 (case: 3, 4)
# 2020-04-12 14:59:17,283 - root - INFO - XXX. stats['F#']: {3: 4, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0}
# 2020-04-12 14:59:17,283 - ct.ct_graph_utils - INFO - Face: [(73, 56), (56, 185), (185, 73)]
# 2020-04-12 14:59:17,283 - ct.ct_graph_utils - INFO - Face: [(73, 180), (180, 56), (56, 73)]
# 2020-04-12 14:59:17,283 - ct.ct_graph_utils - INFO - Face: [(56, 180), (180, 185), (185, 56)]
# 2020-04-12 14:59:17,283 - ct.ct_graph_utils - INFO - Face: [(185, 180), (180, 73), (73, 185)]
# 2020-04-12 14:59:17,284 - root - INFO -
# 2020-04-12 14:59:17,284 - root - INFO - END 95: Main loop - len(ariadne_s_thread) = 96
# 2020-04-12 14:59:17,284 - root - INFO - BEGIN 96: Main loop
# 2020-04-12 14:59:17,284 - root - INFO - BEGIN 96: Search the right edge to remove (faces left: 4)
# 2020-04-12 14:59:17,284 - root - INFO - END 96: Search the right edge to remove. Found: (73, 56) (case: 3, 3)
# 2020-04-12 14:59:17,284 - root - INFO - BEGIN 96: Remove an F3, F4 or F5 (case: 3, 3)
# 2020-04-12 14:59:17,284 - root - INFO - XXXXXX. f3: [(185, 180), (180, 185)], f4: [(185, 180), (180, 185)]
# 2020-04-12 14:59:17,284 - root - INFO - END 96: Remove an F3, F4 or F5 (case: 3, 3)
# 2020-04-12 14:59:17,284 - root - INFO - XXX. stats['F#']: {2: 2, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0}
# 2020-04-12 14:59:17,284 - ct.ct_graph_utils - INFO - Face: [(185, 180), (180, 185)]
# 2020-04-12 14:59:17,285 - ct.ct_graph_utils - INFO - Face: [(185, 180), (180, 185)]
# 2020-04-12 14:59:17,285 - ct.ct_graph_utils - INFO - Face: [(185, 180), (180, 185)]
#
# GOOD:
# -----
# 2020-04-12 15:00:14,269 - root - INFO - END 94: Main loop - len(ariadne_s_thread) = 95
# 2020-04-12 15:00:14,269 - root - INFO - BEGIN 95: Main loop
# 2020-04-12 15:00:14,269 - root - INFO - BEGIN 95: Search the right edge to remove (faces left: 5)
# 2020-04-12 15:00:14,269 - root - INFO - END 95: Search the right edge to remove. Found: (91, 192) (case: 3, 4)
# 2020-04-12 15:00:14,269 - root - INFO - BEGIN 95: Remove an F3, F4 or F5 (case: 3, 4)
# 2020-04-12 15:00:14,269 - root - INFO - XXXXXX. f3: [(157, 170), (170, 108), (108, 157)], f4: [(108, 170), (170, 101), (101, 108)]
# 2020-04-12 15:00:14,269 - root - INFO - END 95: Remove an F3, F4 or F5 (case: 3, 4)
# 2020-04-12 15:00:14,269 - root - INFO - XXX. stats['F#']: {3: 4, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
# 2020-04-12 15:00:14,270 - ct.ct_graph_utils - INFO - Face: [(108, 170), (170, 101), (101, 108)]
# 2020-04-12 15:00:14,270 - ct.ct_graph_utils - INFO - Face: [(157, 170), (170, 108), (108, 157)]
# 2020-04-12 15:00:14,270 - ct.ct_graph_utils - INFO - Face: [(170, 157), (157, 101), (101, 170)]
# 2020-04-12 15:00:14,270 - ct.ct_graph_utils - INFO - Face: [(157, 108), (108, 101), (101, 157)]
#
# 2020-04-12 15:00:14,270 - root - INFO - END 95: Main loop - len(ariadne_s_thread) = 96
# 2020-04-12 15:00:14,270 - root - INFO - BEGIN 96: Main loop
# 2020-04-12 15:00:14,270 - root - INFO - BEGIN 96: Search the right edge to remove (faces left: 4)
# 2020-04-12 15:00:14,270 - root - INFO - END 96: Search the right edge to remove. Found: (108, 170) (case: 3, 3)
# 2020-04-12 15:00:14,270 - root - INFO - BEGIN 96: Remove an F3, F4 or F5 (case: 3, 3)
# 2020-04-12 15:00:14,271 - root - INFO - XXXXXX. f3: [(157, 101), (101, 157)], f4: [(101, 157), (157, 101)]
# 2020-04-12 15:00:14,271 - root - INFO - END 96: Remove an F3, F4 or F5 (case: 3, 3)
# 2020-04-12 15:00:14,271 - root - INFO - XXX. stats['F#']: {2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
# 2020-04-12 15:00:14,271 - ct.ct_graph_utils - INFO - Face: [(101, 157), (157, 101)]
# 2020-04-12 15:00:14,271 - ct.ct_graph_utils - INFO - Face: [(101, 157), (157, 101)]
# 2020-04-12 15:00:14,271 - ct.ct_graph_utils - INFO - Face: [(157, 101), (101, 157)]
#
# END BUG-001

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

    stats['CASE-F2-01'] = 0

    stats['CASE-F3-01'] = 0

    stats['CASE-F4-01'] = 0
    stats['CASE-F4-02'] = 0
    stats['CASE-F4-03'] = 0

    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C3'] = 0
    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C4'] = 0
    stats['CASE-F5-C1!=C2-SameKempeLoop-C1-C2'] = 0

    stats['TOTAL_RANDOM_KEMPE_SWITCHES'] = 0
    stats['MAX_RANDOM_KEMPE_SWITCHES'] = 0

    stats['time_GRAPH_CREATION_BEGIN'] = 0
    stats['time_GRAPH_CREATION_END'] = 0

    stats['time_PLANAR_EMBEDDING_BEGIN'] = 0
    stats['time_PLANAR_EMBEDDING_END'] = 0

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
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

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
    the_colored_graph.delete_edge(vertex_to_join_near_v1, vertex_to_join_near_v2, previous_edge_color)

    # Restore the previous edge
    the_colored_graph.add_edge(v1, vertex_to_join_near_v1, previous_edge_color)
    the_colored_graph.add_edge(v2, vertex_to_join_near_v2, previous_edge_color)
    the_colored_graph.add_edge(v1, v2, new_multiedge_color_one)
    the_colored_graph.add_edge(v2, v1, new_multiedge_color_two)

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
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

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
        temp_multiple_edges_to_check = the_colored_graph.edges_incident(vertex_to_join_near_v1_on_the_face)  # Three edges will be returned
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
    the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
    the_colored_graph.delete_edge(vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

    # Restore the previous edge
    the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, previous_edge_color_at_v2)
    the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
    the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
    the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
    the_colored_graph.add_edge(v1, v2, new_edge_color)

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
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

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
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

        # CASE: F4 SUBCASE: Same color at v1 and v2
        # Since edges at v1 and v2 are on the same Kempe cycle (with the top edge), I can also avoid the kempe chain color switching, since in this case the chain is made of three edges
        the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        the_colored_graph.delete_edge(vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

        # Kempe chain color swap is done manually since the chain is only three edges long
        the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
        the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

        # Just for sure. Is the top edge a multiedge? I need to verify it. It should't be
        if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
            the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
            the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
            logger.error("HERE?")  # This is only to verify if this condition may happen ... and my reasoning was wrong :-(
            exit(-1)
        else:
            the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

        # Restore the other edges
        the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
        the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

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
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

            # CASE: F4, SUBCASE: The two edges are on the same Kempe cycle
            # Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping
            apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, previous_edge_color_at_v1, previous_edge_color_at_v2, previous_edge_color_at_v1, previous_edge_color_at_v2)

            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F4 - The two edges are on the same Kempe cycle")

        else:

            # Update stats
            stats['CASE-F4-03'] += 1

            if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: restore an F4 - The two edges are NOT on the same Kempe cycle")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels=True)), the_colored_graph.is_regular(3))

            # CASE: F4 SUBCASE: Worst case: The two edges are NOT on the same Kempe cycle
            # I'll rotate the colors of the cycle for the edge at v1, and then, since edge_color_at_v1 will be == edge_color_at_v2, apply CASE-001
            kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), previous_edge_color_at_v1, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])
            previous_edge_color_at_v1 = previous_edge_color_at_v2

            # CASE: F4, SUBCASE: The two edges are now on the same Kempe cycle
            # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
            the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            the_colored_graph.delete_edge(vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)

            # Kempe chain color swap is done manually since the chain is only three edges long
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

            # Just to be sure. Is the top edge a multiedge? I need to verify it. It should't be
            if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

            # Restore the other edges
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
            the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

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
    edges_at_vertices_near_v1_on_the_face = the_colored_graph.edges_incident(vertex_to_join_near_v1_on_the_face, labels=False)
    edges_at_vertices_near_v2_on_the_face = the_colored_graph.edges_incident(vertex_to_join_near_v2_on_the_face, labels=False)
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
    # TODO: Update the algoritm respect to how it was implemented
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

                # Save the max
                stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

                # Update stats
                stats['CASE-F5-C1==C2-SameKempeLoop-C1-C3'] += 1
                if logger.isEnabledFor(logging.DEBUG): logger.debug("END: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

            elif are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c4):

                if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C4")

                # Apply half Kempe loop color switching (c2==c1, c4)
                apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c4)
                end_of_f5_restore = True

                # Save the max
                stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

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

                # Save the max
                stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

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

            random_edge_to_fix_the_impasse = the_colored_graph.random_edge(labels=True)
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
                logger.error("ERROR: Infinite loop. Chech the debug.really_bad_case.* files")
                logger.error("Try to shuffle the faces at the beginning: sage 4ct.py -p debug/debug.previous_run.planar -c <USE the same sequence you used the previous run> -s")

                # This is used as a sentinel to use the runs.bash script
                open("debug/error.txt", 'a').close()
                exit(-1)

            if is_well_colored(the_colored_graph) is False:
                print_graph(the_colored_graph)
                logger.error("is_well_colored: False")
                exit(-1)

            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: Random switch")

    # END F5 has been restored
    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: restore an F5: %s", stats['TOTAL_RANDOM_KEMPE_SWITCHES'])


def select_edge_to_remove(g_faces, choices, i_global_counter):
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

    # Select a face < F6
    # Since faces less then 6 always exist for any graph (Euler), I can take the first face that I find with that characteristics (< 6)
    # A smart sort will reorder the list for the next cycle (I need to process faces with 2 or 3 edges first, to avoid bad conditions ahead)
    # if len(g_faces[0]) != 2:
    #     f_temp = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 5), g_faces[0]))))
    #     g_faces.remove(f_temp)
    #     g_faces.insert(0, f_temp)

    # Since faces less then 6 always exist for any graph (Euler) --> Select a face < F6
    #
    # OLD COMMENT: AND faces are sorted by their length, I can take the first one
    # OLD COMMENT: In this version instead of a full sort, I just move an F2, 3, 4, or 5 at the beginning of the list
    #
    # Permutations of 3, 4, 5 = {3, 4, 5} | {3, 5, 4} | {4, 3, 5} | {4, 5, 3} | {5, 3, 4} | {5, 4, 3}
    # F2s have to be selected first ... for now
    if choices == 2345:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 5), g_faces[0]))))
    elif choices == 2354:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 5), next((f for f in g_faces if len(f) == 4), g_faces[0]))))
    elif choices == 2435:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 5), g_faces[0]))))
    elif choices == 2453:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 5), next((f for f in g_faces if len(f) == 3), g_faces[0]))))
    elif choices == 2534:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 5), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 4), g_faces[0]))))
    elif choices == 2543:
        f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 5), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 3), g_faces[0]))))
    else:
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)

    len_of_the_face_to_reduce = len(f1)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("Selected face: %s", f1)

    is_the_edge_to_remove_found = False
    i_edge = 0
    while is_the_edge_to_remove_found is False and i_edge < len_of_the_face_to_reduce:

        if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: test the %s edge", i_edge)

        # One edge separates two faces (pay attention to multiple edges == F2)
        # The edge to remove can be found in the list of faces as (v1, v2) or (v2, v1)
        #
        # TODO: Instead of getting the edges in sequence, I should use a random selector (without repetitions)
        #
        # i_edge = randint(0, len(f1) - 1)  # When stuck, if you re-execute the program (with this random) it should work
        edge_to_remove = f1[i_edge]
        rotated_edge_to_remove = rotate(edge_to_remove, 1)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("len_of_the_face_to_reduce: %s", len_of_the_face_to_reduce)
            logger.debug("edge_to_remove: %s", edge_to_remove)
            logger.debug("rotated_edge_to_remove: %s", rotated_edge_to_remove)

        # TODO:
        # - It would be better not to select an edge (to remove) if it belongs to the ocean
        # - I also need to avoid that the ocean will become an F2 face (if ocean is F3 and selected edge has a vertex on the ocean)
        # - Can this be used only if the graph was created by me from the "base" graph?
        #   commented: if ((edge_to_remove[0] not in [0, 1, 2, 3]) and (edge_to_remove[1] not in [0, 1, 2, 3]) and (edge_to_remove not in g_faces[-1]) and (rotated_edge_to_remove not in g_faces[-1])):

        # If F2, the rotated edge appears twice in the list of faces
        if len_of_the_face_to_reduce == 2:

            # For F2 faces, edges will appear twice in all the edges lists of all faces
            temp_f2 = [face for face in g_faces if rotated_edge_to_remove in face]
            temp_f2.remove(f1)
            f2 = temp_f2[0]
            f1_plus_f2_temp = join_faces(f1, f2, edge_to_remove)
        else:
            f2 = next(face for face in g_faces if rotated_edge_to_remove in face)
            f1_plus_f2_temp = join_faces(f1, f2, edge_to_remove)

        # The resulting graph is 1-edge-connected if the new face has an edge that does not divide two countries, but separates a portion of the same land
        if is_the_graph_one_edge_connected(f1_plus_f2_temp) is True:

            # Skip to the next edge, this is not good
            i_edge += 1
        else:
            is_the_edge_to_remove_found = True

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Edge to remove found :-) %s", edge_to_remove)
                logger.debug("f1: %s", f1)
                logger.debug("f2: %s", f2)
                logger.debug("f1_plus_f2_temp: %s", f1_plus_f2_temp)

        if logger.isEnabledFor(logging.DEBUG): logger.debug("END: test the %s edge", i_edge)

    # If not found -> Reset the edge_to_remove
    if is_the_edge_to_remove_found is False:
        edge_to_remove = ()
        logger.info("END %s: Search the right edge to remove. NOT Found", i_global_counter)
    else:

        # What kind of face am I reducing (I need only f1, f2 is only for debugging ... for now)
        len_f1 = len(f1)
        len_f2 = len(f2)

        logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)", i_global_counter, edge_to_remove, len_f1, len_f2)

    return edge_to_remove, f1, f2, f1_plus_f2_temp


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

    # Compute the embedding only if it was non loaded with the -p (planar) parameter
    # The embedding is needed to get the face() representation of the map
    logger.info("BEGIN: Embed the graph into the plane (Sage function is_planar(set_embedding = True)). It may take very long time depending on the number of vertices")
    stats['time_PLANAR_EMBEDDING_BEGIN'] = time.ctime()
    the_graph.is_planar(set_embedding=True, set_pos=True)
    stats['time_PLANAR_EMBEDDING_END'] = time.ctime()
    logger.info("END: Embed the graph into the plane (is_planar(set_embedding = True)")

    # Just a test here: Using sage built-in functions to color the map, may take a loooooooot of time :-)
    #
    # logger.info("BEGIN: Coloring")
    # the_graph.allow_multiple_edges(False)
    # from sage.graphs.graph_coloring import edge_coloring
    # edge_coloring(the_graph)
    # logger.info("END: Coloring")
    # Tests starting from triangulations with 100 vertices: 7, 73, 54, 65, 216, 142, 15, 14, 21, 73, 24, 15, 32, 72, 232 seconds

    # Get the faces representation of the graph
    # From now on, 'till the end of the reduction process, I'll use only this representation (join_faces, remove vertices, etc.)
    # instead of the Graph object.
    # This is because the elaboration is faster and I don't have to deal with the limit of sage about multiple edges and loops
    # List it is sorted: means faces with len less than 6 are placed at the beginning

    # Save the face() representation only if it was non loaded with the -p (planar) parameter
    # In that case g_faces is already set
    temp_g_faces = the_graph.faces()

    # A full sort of all faces would make the algorithm faster later (maybe)
    temp_g_faces.sort(key=len)
    g_faces = [face for face in temp_g_faces]

    # Save the face representation for later executions (if needed)
    # OLD: with open("debug/debug.previous_run.serialized", 'wb') as fp: pickle.dump(g_faces, fp)
    # OLD: with open("debug/debug.previous_run.embedding_list", 'wb') as fp: fp.writelines(str(line) + '\n' for line in g_faces)
    with open("debug/debug.previous_run.planar", 'wb') as fp:
        json.dump(g_faces, fp)

    return g_faces


def create_from_random(number_of_vertices_for_the_random_triangulation, shuffle_the_planar_representation):
    """
    Create a random planar graph from the dual of a RandomTriangulation (Sage function).

    Parameters
    ----------
        number_of_vertices_for_the_random_triangulation: The number of vertices to create the graph
        shuffle_the_planar_representation: Shuffle the planar representation of the map

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Create a random planar graph from the dual of a RandomTriangulation (Sage function) of %s vertices. It may take very long time depending on the number of vertices", number_of_vertices_for_the_random_triangulation)
    if number_of_vertices_for_the_random_triangulation < 9:
        logger.warning("RandomTriangulation sometimes fails with n < 9. It is a Sage bug/limitation")

    temp_g = graphs.RandomTriangulation(number_of_vertices_for_the_random_triangulation)  # Random triangulation on the surface of a sphere
    temp_g.is_planar(set_embedding=True, set_pos=True)  # Cannot calculate the dual if the graph has not been embedded
    the_graph = graph_dual(temp_g)  # The dual of a triangulation is a 3-regular planar graph
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

    check_graph_planarity_3_regularity_no_loops(the_graph)

    # I need this (export + import) to be able to reproduce this test exactly in the same condition in a second run
    # I cannot use the output file because it has different ordering of edges and vertices, and the execution would run differently (I experimented it on my skin)
    # The export function saves the graph using a different order for the edges (even if the graph are exactly the same graph)
    the_graph.export_to_file("debug/debug.previous_run.edgelist", format="edgelist")

    the_graph = Graph(networkx.read_edgelist("debug/debug.previous_run.edgelist", create_using=networkx.MultiGraph()), multiedges=True)
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal

    # Convert the graph to planar (faces representation)
    g_faces = from_graph_to_planar(the_graph)

    # Shuffle the planar representation of the map
    if shuffle_the_planar_representation:
        shuffle(g_faces)

    logger.info("END: Create a random planar graph of %s vertices, from the dual of a RandomTriangulation of %s vertices", the_graph.order(), number_of_vertices_for_the_random_triangulation)

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
    the_graph = Graph(networkx.read_edgelist(edgelist_filename, create_using=networkx.MultiGraph()), multiedges=True)

    check_graph_planarity_3_regularity_no_loops(the_graph)

    # TODO: Why did I need to relabel them? For now I'll comment the line
    # the_graph.relabel()  # I need to relabel it
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal

    # Convert the graph to planar (faces representation)
    g_faces = from_graph_to_planar(the_graph)

    # Shuffle the planar representation of the map
    if shuffle_the_planar_representation:
        shuffle(g_faces)

    logger.info("END: Load the graph from the external file: %s", edgelist_filename)

    return the_graph, g_faces


def create_from_planar(planar_filename, shuffle_the_planar_representation):
    """
    Load the planar embedding of a graph (output of the gfaces() function).

    Parameters
    ----------
        planar_filename: The planar file to upload
        shuffle_the_planar_representation: Shuffle the planar representation of the map

    Returns
    -------
        the_graph: The graph
        g_faces: The planar representation of the graph
    """

    logger.info("BEGIN: Load the planar embedding of a graph (output of the gfaces() function): %s", planar_filename)

    # Warning: Sage NotImplementedError: cannot compute with embeddings of multiple-edged or looped graphs
    # with open(args.planar, 'r') as fp: g_faces = pickle.load(fp)
    with open(planar_filename, 'r') as fp:
        g_faces = json.load(fp)

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

    logger.info("END: Load the planar embedding of a graph (output of the gfaces() function): %s", planar_filename)

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

def reduce_faces(g_faces, choices):
    """
    Method similar to the Kempe reduction "patching" method.\n
    For each loop remove an edge from a face <= F5, until the graph will have only three faces (an island with two lands)

    Parameters
    ----------
        g_faces: The planar representation of the graph
        choices: The selection method for the edges

    Returns
    -------
        ariadne_s_thread: You would better study the classics
    """

    logger.info("----------------------")
    logger.info("BEGIN: Reduction phase")
    logger.info("----------------------")
    stats['time_ELABORATION_BEGIN'] = time.ctime()
    stats['time_ELABORATION'] = datetime.datetime.now()

    # It will contain items made of lists of values to find the way back to the original graph (Ariadne's String Myth)
    # _string not in the sense of programming language :-) search for the mitos: ariadne string
    ariadne_s_thread = []
    ariadne_step = []

    # Start the reduction process
    is_the_end_of_the_reduction_process = False
    i_global_counter = 0

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
        edge_to_remove, f1, f2, f1_plus_f2_temp = select_edge_to_remove(g_faces, choices, i_global_counter)

        # Check if math is right :-) An edge to remove must exist
        if edge_to_remove is ():
            logger.error("Unexpected condition (a suitable edge has not been found). Mario you'd better go back to paper")
            logger.info("TODO: For now I considered only the first selected face < F6. I may search the right edge in other faces < F6")
            logger.info("TODO: Should be easier to prove that among all faces < F6, an edge exists that if removed does not make the graph 1-edge-connected")
            exit(-1)

        # What kind of face am I reducing (I need only f1, f2 is only for debugging ... for now)
        len_of_the_face_to_reduce_f1 = len(f1)
        len_of_the_face_to_reduce_f2 = len(f2)

        # Remove the edge of an F2 (multiple edge)
        if len_of_the_face_to_reduce_f1 == 2:

            logger.info("BEGIN %s: Remove a multiple edge (case: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

            # Get the two vertices to join
            # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O
            v1 = edge_to_remove[0]
            v2 = edge_to_remove[1]

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
            logger.info("END %s: Remove a multiple edge (case: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

        # Remove an F3 or F4 or F5
        else:

            logger.info("BEGIN %s: Remove an F3, F4 or F5 (case: %s, %s)", i_global_counter, len_of_the_face_to_reduce_f1, len_of_the_face_to_reduce_f2)

            # Get the vertices at the ends of the edge to remove
            # And find the other four neighbors :>.---.<: (If the --- is the removed edge, the four external dots represent the vertices I'm looking for)
            v1 = edge_to_remove[0]
            v2 = edge_to_remove[1]

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

                # TODO: There is a small bug (SEE BUG-001) to care about here at the end of the process when for faces F3 remains (as in the Mercedes Benz symbol). ==
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

        # END of main loop (-1 because the counte has been just incremented)
        logger.info("F# = %s", stats['F#'])
        logger.info("END %s: Main loop - len(ariadne_s_thread) = %s", i_global_counter, len(ariadne_s_thread))

        json.dump(stats['F#'], f_distribution)
        f_distribution.write("\n")

        # If not reduced, continue
        if is_the_end_of_the_reduction_process is False:
            i_global_counter += 1
            logger.info("")

    # Close the file of the distubutions
    f_distribution.close()

    logger.info("--------------------")
    logger.info("END: Reduction phase")
    logger.info("--------------------")
    logger.info("")

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

    logger.info("---------------------------")
    logger.info("BEGIN: Reconstruction phase")
    logger.info("---------------------------")

    # At this point the graph has 3 faces (an island with 2 lands + the ocean) and 3 edges ... easily 3-edge-colorable
    # WARNING: the color of the edges of a multiedge graph cannot be changed, so during the process it is necessary to delete and re-insert edges
    the_colored_graph = Graph(sparse=True)
    the_colored_graph.allow_loops(False)
    the_colored_graph.allow_multiple_edges(True)  # During the process I need this to be set to true

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
    the_colored_graph.add_edge(v1, v2, "red")
    the_colored_graph.add_edge(v1, v2, "green")
    the_colored_graph.add_edge(v1, v2, "blue")

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
        if not is_well_colored(the_colored_graph):
            logger.error("Unexpected condition (coloring is not valid). Mario you'd better go back to paper or learn to code")
            exit(-1)

        # If no other edges have to be restored, then I'm done
        if len(ariadne_s_thread) == 0:
            is_the_end_of_the_rebuild_process = True

    stats['time_ELABORATION_END'] = time.ctime()
    stats['time_ELABORATION'] = (datetime.datetime.now() - stats['time_ELABORATION']).seconds
    logger.info("-------------------------")
    logger.info("END: Reconstruction phase")
    logger.info("-------------------------")
    logger.info("")

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

    # Create and if exist remove the f_distribution_file
    with open("debug/debug.f_distribution.json.dump", "wb") as f_distribution:
        json.dump(stats['F#'], f_distribution)
        f_distribution.write("\n")



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
    group_input.add_argument("-r", "--rand", help="Random graph: dual of a triangulation of N vertices", type=int)
    group_input.add_argument("-e", "--edgelist", help="Load a .edgelist file (networkx)")
    group_input.add_argument("-p", "--planar", help="Load a planar embedding (json) of the graph G.faces() - Automatically saved at each run")
    parser.add_argument("-o", "--output", help="Save a .edgelist file (networkx), plus a .dot file (networkx). Specify the file without extension", required=False)
    parser.add_argument("-c", "--choices", help="Sequence of the Fs to choose (2345, 2354, 2435, 2453, 2534, 2543)", type=int, default=2345, choices=[2345, 2354, 2435, 2453, 2534, 2543], required=False)
    parser.add_argument("-s", "--shuffle", help="Shuffle the list at the beginning. Most of the times it solves the infinite loop condition", action='store_true')
    parser.add_argument("-n", "--num_executions", help="The entire process will be executed N times", type=int, default=1, required=False)
    args = parser.parse_args()

    # Execute n times the program to see if it is deterministic
    for executions in range(args.num_executions):
   
        # Initialize statistics (stats is global)
        initialize_statistics()

        logger.info("--------------------------------")
        logger.info("BEGIN: Create the graph to color")
        logger.info("--------------------------------")
        stats['time_GRAPH_CREATION_BEGIN'] = time.ctime()

        # Create the graph
        if args.rand is not None:  # Random - Dual of a triangulation
            the_graph, g_faces = create_from_random(args.rand, args.shuffle)
        elif args.edgelist is not None:  # edgelist - Load a graph stored in edgelist format
            the_graph, g_faces = create_from_edge_list(args.edgelist, args.shuffle)
        elif args.planar is not None:  # Planar - Load a planar embedding of the graph
            the_graph, g_faces = create_from_planar(args.planar, args.shuffle)

        stats['time_GRAPH_CREATION_END'] = time.ctime()
        logger.info("------------------------------")
        logger.info("END: Create the graph to color")
        logger.info("------------------------------")
        logger.info("")

        # Keep track of the distribution of faces length
        init_f_distribution(g_faces)

        ######
        ######
        # 4CT: AT THE BEGINNING THE GRAPH HAS TO BE CUBIC AND PLANAR WITH NO LOOPS
        # 4CT: NOTE: It can have multiple edges but some software is not able to compute planarity
        ######
        ######

        logger.debug("------------------------")
        logger.debug("BEGIN: Graph information")
        logger.debug("------------------------")

        # Log faces
        log_faces(g_faces)

        logger.debug("----------------------")
        logger.debug("END: Graph information")
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

        ariadne_s_thread = reduce_faces(g_faces, args.choices)
        the_colored_graph = rebuild_faces(g_faces, ariadne_s_thread)

        ######
        ######
        # 4CT: Show the restored and 4 colored map and check for mistakes
        ######
        ######

        logger.info("------------------------------------------")
        logger.info("BEGIN: Show the restored and 4 colored map")
        logger.info("------------------------------------------")

        # Check if the recreated graph is isomorphic to the original
        logger.info("BEGIN: Check if isomorphic")
        if the_graph.is_isomorphic(the_colored_graph) is True:
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

        logger.debug("----------------------------------------")
        logger.debug("END: Show the restored and 4 colored map")
        logger.debug("----------------------------------------")
        logger.info("")

        # Save the output graph
        if args.output is not None:
            export_graph(the_colored_graph, args.output)

        # Print statistics
        print_stats()

    exit(0)


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
    main()
