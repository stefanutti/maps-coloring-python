#!/usr/bin/env sage

###
###
# 4CT: This program uses these approaches together
#      - It consider Tait edge coloring and the equivalency of the 3-edge-coloring (known as Tait coloring) and 4-face-coloring (the original four color theorem for maps)
#      - Uses a modified Kempe reduction method: it does not shrink a face (faces <= F5) down to a point, but removes a single edge from it (from faces <= F5)
#      - Uses a modified Kempe chain edge color switching: when restoring edges from the reduced graph, it will swap Half of the cycle of a color chain
#        - !!! While rebuilding a map, all chains are actually loops!!!
#
###
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
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
#   - Bad: Using this method You can encounter maps for which the method loops indefinitely
#   - Good: Now that I know, at least I won't spend more time on this aspect. The other good thing is the this case is very rare, the the program can color almost all maps
#
#
# TODOs:
# - Moved to: https://github.com/stefanutti/maps-coloring-python/issues
#
# BACKLOG to evaluate:
# - TODO: Realize a version in which faces are made of lists of ordered vertices [1, 4, 7, 8] not edges [(1,4),(4,7),(7,8),(8,1)]. Would it be faster?
# - TODO: Realize the reconstruction phase with the lists of the edge representation instead of using the graph. It will probably be a lot faster!
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
import copy
import sys
import collections
import timeit
import logging.handlers
import random
import time
from datetime import datetime

import json

import networkx

from sage.all import *
from sage.graphs.graph_coloring import edge_coloring

# This solves this issue: http://ask.sagemath.org/question/33727/logging-failing-after-a-while/
# Only when running the code in the cloud: https://cloud.sagemath.com/
# sage_server.MAX_OUTPUT_MESSAGES = 100000 # Needed for the cloud version of Sage

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
# 4CT: Helping functions
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


###########################################################################
# Return a face as a list of ordered vertices. Used to create random graphs
# Taken on the internet (http://trac.sagemath.org/ticket/6236)
###########################################################################
def faces_by_vertices(g):
    d = {}
    for key, val in g.get_embedding().iteritems():
        d[key] = dict(zip(val, val[1:] + [val[0]]))
    list_faces = []
    for start in d:
        while d[start]:
            face = []
            prev = start
            _, curr = d[start].popitem()
            face.append(start)
            while curr != start:
                face.append(curr)
                prev, curr = (curr, d[curr].pop(prev))
            list_faces.append(face)

    return list_faces


#################################################################################################
# Return the dual of a graph. Used to create random graphs
# Taken on the internet: to make a dual of a triangulation (http://trac.sagemath.org/ticket/6236)
#################################################################################################
def graph_dual(g):
    f = [tuple(face) for face in faces_by_vertices(g)]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]
    dual = Graph([f_edges, lambda f1, f2: set(f1).intersection([(e[1], e[0]) for e in f2])])

    return dual


##########################################################################################
# Check if I can work with this graph: has to be planar and 3 regular (planar cubic graph)
##########################################################################################
def check_graph_at_beginning(graph):
    # Check 3-regularity
    #
    if graph.is_regular(3) is False:
        logger.error("Error: The graph is not 3-regular")
        exit(-1)
    else:
        logger.info("OK. The graph is 3-regular")

    # Check loops
    #
    if graph.has_loops() is True:
        logger.error("ERROR: It seems that loops are difficult to handle during reduction and recoloring, so I'll start without them and avoid their creation during the reduction process")
        exit(-1)
    else:
        logger.info("OK. The graph does not have loops. Consider that this program will avoid their creation during the reduction process")

    # Check multiple edges
    #
    if graph.has_multiple_edges() is True:
        logger.error("ERROR: The graph has multiple edges. At the beginning multiple edges are not permitted")
        exit(-1)
    else:
        logger.info("OK. The graph does not have multiple edges. Consider that this program will also handle multiple edges during the reduction and reconstruction process")

    # Check if the graph is planar
    #
    if graph.is_planar() is False:
        logger.error("ERROR: The graph is not planar")
        exit(-1)
    else:
        logger.info("OK. The graph is planar")

    # Additional info
    #
    logger.info("The graph has %s vertices and %s edges", graph.order(), graph.size())

    return


#############
# Print graph
#############
def print_graph(graph):
    for vertex in graph.vertex_iterator():
        edges = graph.edges_incident(vertex)
        logger.info("vertex: %s, edges: %s, is well colored: %s", vertex, edges, are_incident_edges_well_colored(graph, vertex))

    return


######################################
# Execute a Kempe chain color swapping
# Works for chains and cycles
#
# I considered also multiedge cases
######################################
def kempe_chain_color_swap(graph, starting_edge, c1, c2):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: kempe_chain_color_swap: %s, %s, %s", starting_edge, c1, c2)

    # Start the loop at e1
    #
    current_edge = starting_edge
    previous_color = "none"  # Not important here, will be used later
    current_color = c1
    next_color = c2

    # From current edge, I'll search incident edges in one direction
    # The check is important to recognize the half cycle color switching to an entire cycle color switching
    #
    direction = 1
    if logger.isEnabledFor(logging.DEBUG): logger.debug("degree: %s", graph.degree(current_edge[direction]))
    if graph.degree(current_edge[direction]) != 3:
        direction = 0

    is_the_end_of_switch_process = False
    while is_the_end_of_switch_process is False:

        # Debug
        #
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Vertex at direction: %s", current_edge[direction])

        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph.edge_iterator(labels = True)), graph.is_regular(3))

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        #
        tmp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        if logger.isEnabledFor(logging.DEBUG): logger.debug("tmp_next_edges_to_check: %s", tmp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in tmp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

        # Save current edge and vertex direction
        #
        previous_edge = current_edge
        previous_vertex = current_edge[direction]

        # Check if I've looped an entire cycle
        #
        if are_the_same_edge(starting_edge, edges_to_check[0]) or are_the_same_edge(starting_edge, edges_to_check[1]):
            is_the_end_of_switch_process = True
        else:

            # Check the color of the two edges and find the next chain
            #
            next_e1_color = edges_to_check[0][2]
            next_e2_color = edges_to_check[1][2]
            if next_e1_color == next_color:
                current_edge = edges_to_check[0]
            elif next_e2_color == next_color:
                current_edge = edges_to_check[1]
            else:
                logger.error("Unexpected condition (next color should exist). Mario you'd better go back to paper")
                exit(-1)

            # Update current and next color
            #
            previous_color = current_color
            current_color = next_color
            next_color = previous_color

            # Now: swap colors
            #
            # graph.set_edge_label(previous_edge[0], previous_edge[1], current_color)
            # graph.set_edge_label(current_edge[0], current_edge[1], previous_color)

            # Just to be sure. Is it a multiedge? I need to verify it. It should't be
            #
            if is_multiedge(graph, previous_edge[0], previous_edge[1]):
                the_colored_graph.delete_edge(previous_edge[0], previous_edge[1], previous_color)
                the_colored_graph.add_edge(previous_edge[0], previous_edge[1], current_color)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                graph.set_edge_label(previous_edge[0], previous_edge[1], current_color)

                # Just to be sure. Is it a multiedge? I need to verify it. It should't be
            #
            if is_multiedge(graph, current_edge[0], current_edge[1]):
                the_colored_graph.delete_edge(current_edge[0], current_edge[1], current_color)
                the_colored_graph.add_edge(current_edge[0], current_edge[1], previous_color)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                graph.set_edge_label(current_edge[0], current_edge[1], previous_color)

            # Update direction
            #
            if current_edge[0] == previous_vertex:
                direction = 1
            else:
                direction = 0

            # Check if I've reached the end of a chain
            #
            if logger.isEnabledFor(logging.DEBUG): logger.debug("degree: %s", graph.degree(current_edge[direction]))
            if graph.degree(current_edge[direction]) != 3:
                is_the_end_of_switch_process = True

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: kempe_chain_color_swap")

    return


######################################
# Check if two edges are the same edge
# (v1, v2) == (v2, v1)
# (v1, v2, color) == (v1, v2)
# (v1, v2, color) == (v2, v1)
######################################
def are_the_same_edge(e1, e2):
    return e1[0] in e2 and e1[1] in e2


#######################
# Initialize statistics
#######################
def initialize_statistics(stats):
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


############################################
# Check if egdes are on the same Kempe cycle
############################################
def are_edges_on_the_same_kempe_cycle(graph, e1, e2, c1, c2):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: are_edges_on_the_same_kempe_cycle: %s, %s, %s, %s", e1, e2, c1, c2)

    # Flag to return
    #
    are_edges_on_the_same_kempe_cycle_flag = False

    out_of_scope_color = get_the_other_colors([c1, c2])[0]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("out_of_scope_color: %s", out_of_scope_color)

    # Start the loop at e1
    #
    current_edge = e1
    current_color = c1
    next_color = get_the_other_colors([out_of_scope_color, current_color])[0]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("current_color: %s", current_color)

    # From current edge, I'll search incident edges in one direction: 1 for the first edge, and then will decide the graph
    # (v1, v2) if a search all incident edges to v2 I'll have (v2, vx) and (v2, vy). Next vertex to choose will be vx or vy ... depending on the next chain color
    #
    direction = 1
    is_the_end_of_search_process = False
    while is_the_end_of_search_process is False:

        # Debug
        #
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        #
        tmp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        if logger.isEnabledFor(logging.DEBUG): logger.debug("tmp_next_edges_to_check: %s", tmp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in tmp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

        # Check the color of the two edges and find the next chain
        #
        next_e1_color = edges_to_check[0][2]
        next_e2_color = edges_to_check[1][2]
        previous_vertex = current_edge[direction]
        if next_e1_color == next_color:
            current_edge = edges_to_check[0]
        elif next_e2_color == next_color:
            current_edge = edges_to_check[1]
        else:
            logger.error("Unexpected condition (next color should exist). Mario you'd better go back to paper")
            exit(-1)

        # Update current and next color
        #
        current_color = next_color
        next_color = get_the_other_colors([out_of_scope_color, current_color])[0]

        # Update direction
        #
        if current_edge[0] == previous_vertex:
            direction = 1
        else:
            direction = 0

        # Check if I've reached e2
        #
        if are_the_same_edge(current_edge, e2):
            are_edges_on_the_same_kempe_cycle_flag = True
            is_the_end_of_search_process = True

        # Check if I've looped an entire cycle (of course without walking on e2 - previous check)
        #
        if are_the_same_edge(current_edge, e1):
            is_the_end_of_search_process = True

        # Debug info for this loop
        #
        if logger.isEnabledFor(logging.DEBUG): logger.debug("current_color: %s, next_color: %s, current_edge: %s, are_edges_on_the_same_kempe_cycle_flag: %s, is_the_end_of_search_process: %s", current_color, next_color, current_edge, are_edges_on_the_same_kempe_cycle, is_the_end_of_search_process)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: are_edges_on_the_same_kempe_cycle_flag: %s", are_edges_on_the_same_kempe_cycle_flag)

    return are_edges_on_the_same_kempe_cycle_flag


#######################################
# Apply half Kempe loop color switching
#######################################
def apply_half_kempe_loop_color_switching(graph, ariadne_step, color_at_v1, color_at_v2, swap_c1, swap_c2):
    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    v1_on_the_face = ariadne_step[3]
    v2_on_the_face = ariadne_step[4]
    v1_not_on_the_face = ariadne_step[5]
    v2_not_on_the_face = ariadne_step[6]

    # I broke the cycle to apply the half Kempe chain color swapping
    #
    graph.delete_edge((v1_on_the_face, v1_not_on_the_face, color_at_v1))
    graph.delete_edge((v2_on_the_face, v2_not_on_the_face, color_at_v2))
    graph.add_edge(v1, v1_on_the_face, color_at_v1)
    graph.add_edge(v2, v2_on_the_face, color_at_v2)

    # Half Kempe chain color swapping
    #
    kempe_chain_color_swap(graph, (v1, v1_on_the_face), swap_c1, swap_c2)

    # Restore the other edges
    #
    graph.add_edge(v1, v1_not_on_the_face, color_at_v1)
    graph.add_edge(v2, v2_not_on_the_face, color_at_v2)
    graph.add_edge(v1, v2, get_the_other_colors([color_at_v1, swap_c2])[0])


#############
# Print stats
#############
def print_stats(stats):
    logger.info("------------------")
    logger.info("BEGIN: Print stats")
    logger.info("------------------")

    ordered_stats = collections.OrderedDict(sorted(stats.items()))
    for stat in ordered_stats:
        logger.info("Stat: %s = %s", stat, stats[stat])

    logger.info("----------------")
    logger.info("END: Print stats")
    logger.info("----------------")


#######################
# Check if well colored
#######################
def is_well_colored(graph):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: is_well_colored")

    is_well_colored = True

    i_vertex = 0
    is_end_of_job = False
    vertices = graph.vertices()
    while is_end_of_job is False and i_vertex < len(vertices):
        vertex = vertices[i_vertex]

        edges = graph.edges_incident(vertex)

        colors_around_this_vertex = [edges[0][2], edges[1][2], edges[2][2]]

        if not all(color in VALID_COLORS for color in colors_around_this_vertex):
            is_well_colored = False
            is_end_of_job = True
        else:
            i_vertex += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_well_colored")

    return is_well_colored


###############################################################
# Check if the incident edges to a give vertex are well colored
###############################################################
def are_incident_edges_well_colored(graph, vertex):
    are_incident_edges_well_colored = False

    edges = graph.edges_incident(vertex)

    colors_around_this_vertex = [edges[0][2], edges[1][2], edges[2][2]]

    if all(color in VALID_COLORS for color in colors_around_this_vertex):
        are_incident_edges_well_colored = True

    return are_incident_edges_well_colored


#############################################
# Rotate elements (works for lists and tuple)
#############################################
def rotate(l, n):
    return l[n:] + l[:n]


#############################
# Remove a vertex from a face
#############################
def remove_vertex_from_face(face, vertex):
    # Search the edge that contains the vertex as the second element of the tuple
    # new vA = first element of the edge found
    # Search the edge that contains the vertex as the first element of the tuple
    # new vB = second element of the edge found
    #
    tuple_a = next((v1a, v2a) for v1a, v2a in face if v2a == vertex)
    tuple_b = next((v1b, v2b) for v1b, v2b in face if v1b == vertex)
    new_edge = (tuple_a[0], tuple_b[1])
    face.remove(tuple_a)
    index_for_insert = face.index(tuple_b)
    face.remove(tuple_b)
    face.insert(index_for_insert, new_edge)

    return face


##########################
# Get the color of an edge
# In case of multiedge it will return one of the two edges
# This is not a problem because when I'll rebuild the graph the deletes will be done namely using the three attributes (v1, v2, label) (label is the color)
##########################
def get_edge_color(graph, edge):
    v1 = edge[0]
    v2 = edge[1]
    return next(label for (va, vb, label) in graph.edges() if (va, vb) == (v1, v2) or (va, vb) == (v2, v1))


#################
# Is a multiedge?
#################
def is_multiedge(graph, v1, v2):
    is_multiedge = False

    if len(graph.edge_boundary([v1], [v2])) > 1:
        is_multiedge = True

    return is_multiedge


###################################################################################################################################
# join two faces
#
# f1[:index_of_edge_to_remove_on_f1] + f2[index_of_edge_to_remove_on_f2 + 1:] + f2[:index_of_edge_to_remove_on_f2] + f1[index_of_edge_to_remove_on_f1 + 1:]
#
# f1 = [(6, 1), (1, 2), (2, 7), (7, 6)]
# f2 = [(3, 8), (8, 7), (7, 2), (2, 3)]
# edge_to_remove_on_f1 = (2, 7))
# temp f1_plus_f2 = [(6, 1), (1, 2), (2, 3), (3, 8), (8, 7), (7, 6)]
# f1_plus_f2 = [(6, 1), (1, 3), (3, 8), (8, 6)]
#
# f1 = [(2, 7), (7, 6), (6, 1), (1, 2)]
# f2 = [(2, 3), (3, 8), (8, 7), (7, 2)]
# edge_to_remove_on_f1 = (2, 7))
# temp f1_plus_f2 = [(2, 3), (3, 8), (8, 7), (7, 6), (6, 1), (1, 2)]
# f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]
#
# f1 = [(1, 2), (2, 7), (7, 6), (6, 1)]
# f2 = [(7, 2), (2, 3), (3, 8), (8, 7)]
# edge_to_remove_on_f1 = (2, 7))
# temp f1_plus_f2 = [(1, 2), (2, 3), (3, 8), (8, 7), (7, 6), (6, 1)]
# f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]
#
# f1 = [(1, 2), (2, 3), (3, 1)]
# f2 = [(2, 4), (4, 3), (3, 2)]
# edge_to_remove_on_f1 = (2, 3))
# temp f1_plus_f2 = [(1, 2), (2, 4), (4, 3), (3, 1)]
# f1_plus_f2 = [(1, 4), (4, 1)]
#
# f1 = [(2, 1), (1, 2)]
# f2 = [(2, 3), (3, 1), (1, 2)]
# edge_to_remove_on_f1 = (2, 1))
# temp f1_plus_f2 = [(2, 3), (3, 1), (1, 2)]
# f1_plus_f2 = [(3, 3)]
###################################################################################################################################
def join_faces(f1, f2, edge_to_remove_on_f1):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: join_faces")

    # You can only use this function if at least one face has length > 2
    #
    if len(f1) == 2 and len(f2) == 2:
        logger.error("Unexpected condition (f2 + f2 would generate a single edge face). Mario you'd better go back to paper")
        exit(-1)

    # The edge (v1, v2) on f1 is (v2, v1) on the f2 face
    #
    edge_to_remove_on_f2 = rotate(edge_to_remove_on_f1, 1)
    index_of_edge_to_remove_on_f1 = f1.index(edge_to_remove_on_f1)
    index_of_edge_to_remove_on_f2 = f2.index(edge_to_remove_on_f2)

    # Join the face - After this there will still be vertices to remove
    #
    f1_plus_f2 = f1[:index_of_edge_to_remove_on_f1] + f2[index_of_edge_to_remove_on_f2 + 1:] + f2[:index_of_edge_to_remove_on_f2] + f1[index_of_edge_to_remove_on_f1 + 1:]

    # Debug
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("f1: %s", f1)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("f2: %s", f2)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_to_remove_on_f1: %s", edge_to_remove_on_f1)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("index_of_edge_to_remove_on_f1: %s", index_of_edge_to_remove_on_f1)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("index_of_edge_to_remove_on_f2: %s", index_of_edge_to_remove_on_f2)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Temporary f1_plus_f2: %s", f1_plus_f2)

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex A
    #
    # Search the edge that contains v1 (edge_to_remove_on_f1[0]) as the second element of the tuple
    # new vA = first element of the edge found
    # Search the edge that contains v1 (edge_to_remove_on_f1[0]) as the first element of the tuple
    # new vB = second element of the edge found
    #
    tuple_a = next((v1a, v2a) for v1a, v2a in f1_plus_f2 if v2a == edge_to_remove_on_f1[0])
    tuple_b = next((v1b, v2b) for v1b, v2b in f1_plus_f2 if v1b == edge_to_remove_on_f1[0])
    new_edge = (tuple_a[0], tuple_b[1])
    f1_plus_f2.remove(tuple_a)
    index_for_insert = f1_plus_f2.index(tuple_b)
    f1_plus_f2.remove(tuple_b)
    f1_plus_f2.insert(index_for_insert, new_edge)

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    # Search the edge that contains v2 (edge_to_remove_on_f1[1]) as the second element of the tuple
    # new vA = first element of the edge found
    # Search the edge that contains v2 (edge_to_remove_on_f1[1]) as the first element of the tuple
    # new vB = second element of the edge found
    #
    tuple_a = next((v1a, v2a) for v1a, v2a in f1_plus_f2 if v2a == edge_to_remove_on_f1[1])
    tuple_b = next((v1b, v2b) for v1b, v2b in f1_plus_f2 if v1b == edge_to_remove_on_f1[1])
    new_edge = (tuple_a[0], tuple_b[1])
    f1_plus_f2.remove(tuple_a)
    index_for_insert = f1_plus_f2.index(tuple_b)
    f1_plus_f2.remove(tuple_b)
    f1_plus_f2.insert(index_for_insert, new_edge)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("f1_plus_f2: %s", f1_plus_f2)

    if len(f1_plus_f2) == 2 and (f1_plus_f2[0][0] != f1_plus_f2[1][1] or f1_plus_f2[0][1] != f1_plus_f2[1][0]):
        logger.error("Unexpected condition (f2 faces have to be: [(v1, v2), (v2, v1)]. Mario you'd better go back to paper")
        exit(-1)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: join_faces")

    return f1_plus_f2


#################################################################################
# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#################################################################################
def is_the_graph_one_edge_connected(face):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: is_the_graph_one_edge_connected")

    is_the_graph_one_edge_connected = False

    # This is true only for faces != F2
    # NOTE: F2 faces have this representation: [(v1, v2), (v2, v1)] that is correct
    #
    if len(face) != 2:

        # Search the list [(),(),...,()]
        #
        i_edge = 0
        while is_the_graph_one_edge_connected is False and i_edge < len(face):
            reverse_edge = rotate(face[i_edge], 1)

            # Start the search
            #
            if reverse_edge in face[i_edge + 1:]:
                is_the_graph_one_edge_connected = True
            else:

                # Move to the next edge
                #
                i_edge += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_the_graph_one_edge_connected: %s", is_the_graph_one_edge_connected)

    return is_the_graph_one_edge_connected


############################
# Check if vertex is in face
############################
def check_if_vertex_is_in_face(face, vertex):
    return any([edge for edge in face if edge[0] == vertex or edge[1] == vertex])


####################
# Check if 3 regular
####################
def check_regularity(faces):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: check_regularity")

    is_three_regular = True

    # get all vertices
    #
    vertices = [element for face in faces for edge in face for element in edge]
    vertices = sorted(set(vertices))

    i_vertex = 0
    while is_three_regular is True and i_vertex < len(vertices):
        vertex = vertices[i_vertex]
        occurrences = [element for face in faces for edge in face for element in edge if element == vertex]
        if len(occurrences) != 6:
            is_three_regular = False
        else:
            i_vertex += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: check_regularity: %s", is_three_regular)

    return is_three_regular


###################
# Log faces (DEBUG)
###################
def log_faces(faces):
    for face in faces:
        logger.info("Face: %s", face)

    return


######################
# Get the other colors
######################
def get_the_other_colors(colors):
    return [x for x in ["red", "green", "blue"] if x not in colors]


##############
# Export graph
##############
def export_graph(graph_to_export, name_of_file_without_extension):

    # Possibilities: adjlist, dot, edgelist, gexf, gml, graphml, multiline_adjlist, pajek, yaml
    # Format chosen: edgelist
    #
    # Additional note (17/Oct/2016): I decided to save the graph also as a .dot file
    # The problem with dot file is that you can write .dot files directly, but you cannot read them back if you don't install an additional package
    #
    logger.info("------------------------------------------------")
    logger.info("BEGIN: Save the 4 colored map in edgelist format")
    logger.info("------------------------------------------------")
    graph_to_export.export_to_file(name_of_file_without_extension + ".edgelist", format = "edgelist")
    graph_to_export.graphviz_to_file_named(name_of_file_without_extension + ".dot", edge_labels = True, vertex_labels = False)
    logger.info("File saved: %s", name_of_file_without_extension)

    # Replace label with color
    #
    filedata = None
    with open(name_of_file_without_extension + ".dot", 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('label', 'color')
    with open(name_of_file_without_extension + ".dot", 'w') as file:
        file.write(filedata)

    logger.info("----------------------------------------------")
    logger.info("END: Save the 4 colored map in edgelist format")
    logger.info("----------------------------------------------")

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
# 4CT # MAIN: Create/upload the graph to color. it has to be planar and without loops and initially multiple edges
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

##############################################
# 4CT : Constants and variables initialization
##############################################

# General plot options
#
plot_options = {'vertex_size': 150,
                'vertex_labels': True,
                'layout': "spring",
                'edge_style': 'solid',
                'edge_color': 'black',
                'edge_colors': None,
                'edge_labels': False,
                'iterations': 50,
                'tree_orientation': 'down',
                'heights': None,
                'graph_border': False,
                'talk': False,
                'color_by_label': True,
                'partition': None,
                'dist': .075,
                'max_dist': 1.5,
                'loop_size': .075}

EDGE_COLOR_BY_LABEL = {'red': 'red', 'green': 'green', 'blue': 'blue'}

# Valid colors
#
VALID_COLORS = ['red', 'green', 'blue']

# Set logging facilities: LEVEL XXX
#
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)

###############
# Read options:
###############
# (-r <vertices> or -i <file> or -p <planar embedding (json file)>) -o <file>
#
parser = argparse.ArgumentParser(description = '4ct args')

group_input = parser.add_mutually_exclusive_group(required = False)
group_input.add_argument("-r", "--random", help = "Random graph: dual of a triangulation of N vertices", type = int, default = 100)
group_input.add_argument("-i", "--input", help = "Load a .edgelist file (networkx)")
group_input.add_argument("-p", "--planar", help = "Load a .json planar embedding of the graph G.faces() - Automatically saved at each run")
parser.add_argument("-o", "--output", help = "Save a .edgelist file (networkx), plus a .dot file (networkx). Specify the file without extension", required = False)

args = parser.parse_args()

# Initialize statistics
#
stats = {}
initialize_statistics(stats)

# It will contain items made of lists of values to find the way back to the original graph (Ariadne's String Myth)
#
ariadne_string = []

logger.info("--------------------------------")
logger.info("BEGIN: Create the graph to color")
logger.info("--------------------------------")
stats['time_GRAPH_CREATION_BEGIN'] = time.ctime()

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

# Random - Dual of a triangulation
#
if args.random is not None:
    logger.info("BEGIN: Create a random planar graph from the dual of a RandomTriangulation (Sage function) of %s vertices. It may take very long time depending on the number of vertices", args.random)
    number_of_vertices_for_the_random_triangulation = args.random
    tmp_g = graphs.RandomTriangulation(number_of_vertices_for_the_random_triangulation)  # Random triangulation on the surface of a sphere
    void = tmp_g.is_planar(set_embedding = True, set_pos = True)  # Cannot calculate the dual if the graph has not been embedded
    the_graph = graph_dual(tmp_g)  # The dual of a triangulation is a 3-regular planar graph
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

    # I need this (export + import) to be able to reproduce this test exactly in the same condition in a future run
    # I cannot use the output file because it has different ordering of edges and vertices, and the execution would run differently (I experimented it on my skin)
    # The export function saves the graph using a different order for the edges (even if the graph are exactly the same graph)
    #
    the_graph.export_to_file("debug.temp.edgelist", format = "edgelist")
    the_graph = Graph(networkx.read_edgelist("debug.temp.edgelist"))
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal

    logger.info("END: Create a random planar graph of %s vertices, from the dual of a RandomTriangulation of %s vertices", the_graph.order(), number_of_vertices_for_the_random_triangulation)

# Input - Load a graph stored in edgelist mode
#
if args.input is not None:
    logger.info("BEGIN: Load the graph from the external file: %s", args.input)
    the_graph = Graph(networkx.read_edgelist(args.input))
    the_graph.relabel()  # I need to relabel it
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal
    logger.info("END: Load the graph from the external file: %s", args.input)

# Planar - Load a planar embedding of the graph
#
if args.planar is not None:
    logger.info("BEGIN: Load the planar embedding of a graph (output of the gfaces() function): %s", args.planar)
    # with open(args.planar, 'r') as fp: g_faces = pickle.load(fp)
    with open(args.planar, 'r') as fp: g_faces = json.load(fp)

    # Cast back to tuples. json.dump write the "list of list of tuples" as "list of list of list"
    #
    # Original: [[(3,2),(3,5)],[(2,4),(1,3),(1,3)], ... ,[(1,2),(3,4),(6,7)]]
    # Saved as: [[[3,2],[3,5]],[[2,4],[1,3],[1,3]], ... ,[[1,2],[3,4],[6,7]]]
    #
    g_faces = [[tuple(l) for l in L] for L in g_faces]

    # Create the graph from the list of faces
    #
    flattened_egdes = [edge for face in g_faces for edge in face]
    for edge in flattened_egdes:
        reverse_edge = (edge[1], edge[0])
        if reverse_edge in flattened_egdes:
            flattened_egdes.remove(reverse_edge)

    the_graph = Graph(sparse = True)
    the_graph.allow_loops(False)
    the_graph.allow_multiple_edges(True)

    for edge_to_add in flattened_egdes:
        the_graph.add_edge(edge_to_add)

    print_graph(the_graph)
    logger.info("END: Load the planar embedding of a graph (output of the gfaces() function): %s", args.planar)

stats['time_GRAPH_CREATION_END'] = time.ctime()
logger.info("------------------------------")
logger.info("END: Create the graph to color")
logger.info("------------------------------")
logger.info("")

#######
#######
# 4CT : AT THE BEGINNING THE GRAPH HAS TO BE CUBIC AND PLANAR
#######
#######

logger.info("------------------------")
logger.info("BEGIN: Graph information")
logger.info("------------------------")

check_graph_at_beginning(the_graph)

# Compute the embedding only if it was non loaded withe the -p (planar) parameter
#
if args.planar is None:
    logger.info("BEGIN: Embed the graph into the plane (Sage function is_planar(set_embedding = True)). It may take very long time depending on the number of vertices")
    stats['time_PLANAR_EMBEDDING_BEGIN'] = time.ctime()
    void = the_graph.is_planar(set_embedding = True, set_pos = True)
    stats['time_PLANAR_EMBEDDING_END'] = time.ctime()
    logger.info("END: Embed the graph into the plane (is_planar(set_embedding = True)")

# Using sage built-in functions to color the map, may take a loooooooot of time :-)
#
# logger.info("BEGIN: Coloring")
# the_graph.allow_multiple_edges(False)
# edge_coloring(the_graph)
# logger.info("END: Coloring")
# Tests starting from triangulations with 100 vertices: 7, 73, 54, 65, 216, 142, 15, 14, 21, 73, 24, 15, 32, 72, 232 seconds
#

# Get the faces representation of the graph
# From now on, 'till the end of the reduction process, I'll use only this representation (join_faces, remove vertices, etc.) instead of the Graph object
# This is because the elaboration is faster and I don't have to deal with the limit of sage about multiple edges and loops
# List it is sorted: means faces with len less than 6 are placed at the beginning
#

# Save the face() representation only if it was non loaded with the -p (planar) parameter
#
if args.planar is None:
    temp_g_faces = the_graph.faces()
    temp_g_faces.sort(key = len)
    g_faces = [face for face in temp_g_faces]

    # Save the face representation for later executions (if needed)
    #
    # OLD: with open("debug.input_planar_g_faces.serialized", 'wb') as fp: pickle.dump(g_faces, fp)
    # OLD: with open("debug.input_planar_g_faces.embedding_list", 'wb') as fp: fp.writelines(str(line) + '\n' for line in g_faces)
    with open("debug.input_planar_g_faces.json", 'wb') as fp: json.dump(g_faces, fp)

# Override creation (mainly to debug previously elaborated maps)
#
# g_faces = [[(27, 26), (26, 36), (36, 27)], [(11, 19), (19, 12), (12, 11)], [(38, 44), (44, 41), (41, 38)], [(3, 2), (2, 15), (15, 3)],
#            [(48, 49), (49, 46), (46, 48)], [(32, 54), (54, 55), (55, 33), (33, 32)], [(39, 46), (46, 49), (49, 42), (42, 39)],
#            [(33, 55), (55, 52), (52, 34), (34, 33)], [(40, 41), (41, 44), (44, 43), (43, 40)], [(26, 25), (25, 35), (35, 36), (36, 26)],
#            [(7, 8), (8, 54), (54, 32), (32, 7)], [(2, 1), (1, 14), (14, 15), (15, 2)], [(16, 17), (17, 9), (9, 10), (10, 16)],
#            [(5, 24), (24, 20), (20, 6), (6, 5)], [(13, 14), (14, 1), (1, 0), (0, 13)], [(34, 52), (52, 53), (53, 50), (50, 31), (31, 34)],
#            [(10, 12), (12, 19), (19, 18), (18, 16), (16, 10)], [(31, 50), (50, 51), (51, 47), (47, 45), (45, 30), (30, 31)],
#            [(28, 37), (37, 22), (22, 21), (21, 35), (35, 25), (25, 28)], [(21, 20), (20, 24), (24, 27), (27, 36), (36, 35), (35, 21)],
#            [(38, 29), (29, 30), (30, 45), (45, 43), (43, 44), (44, 38)],
#            [(23, 51), (51, 50), (50, 53), (53, 17), (17, 16), (16, 18), (18, 23)],
#            [(39, 40), (40, 43), (43, 45), (45, 47), (47, 48), (48, 46), (46, 39)],
#            [(9, 13), (13, 0), (0, 4), (4, 11), (11, 12), (12, 10), (10, 9)],
#            [(28, 29), (29, 38), (38, 41), (41, 40), (40, 39), (39, 42), (42, 37), (37, 28)], [(42, 49), (49, 48), (48, 47), (47, 51), (51, 23), (23, 22), (22, 37), (37, 42)],
#            [(8, 7), (7, 5), (5, 6), (6, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 8)], [(18, 19), (19, 11), (11, 4), (4, 6), (6, 20), (20, 21), (21, 22), (22, 23), (23, 18)],
#            [(55, 54), (54, 8), (8, 3), (3, 15), (15, 14), (14, 13), (13, 9), (9, 17), (17, 53), (53, 52), (52, 55)],
#            [(31, 30), (30, 29), (29, 28), (28, 25), (25, 26), (26, 27), (27, 24), (24, 5), (5, 7), (7, 32), (32, 33), (33, 34), (34, 31)]]

# g_faces = [[(28, 26), (26, 32), (32, 28)], [(47, 46), (46, 49), (49, 47)],
#            [(10, 3), (3, 2), (2, 10)], [(51, 55), (55, 53), (53, 51)],
#            [(55, 54), (54, 52), (52, 53), (53, 55)], [(0, 7), (7, 9), (9, 1), (1, 0)],
#            [(34, 35), (35, 40), (40, 39), (39, 34)], [(38, 36), (36, 49), (49, 46), (46, 38)],
#            [(2, 1), (1, 9), (9, 10), (10, 2)], [(29, 27), (27, 34), (34, 39), (39, 29)],
#            [(52, 54), (54, 44), (44, 42), (42, 52)], [(17, 18), (18, 20), (20, 21), (21, 17)],
#            [(32, 26), (26, 30), (30, 23), (23, 24), (24, 32)], [(8, 7), (7, 0), (0, 4), (4, 6), (6, 8)],
#            [(30, 31), (31, 21), (21, 20), (20, 23), (23, 30)], [(6, 4), (4, 5), (5, 11), (11, 12), (12, 6)],
#            [(21, 31), (31, 16), (16, 15), (15, 17), (17, 21)], [(48, 37), (37, 33), (33, 43), (43, 50), (50, 48)],
#            [(54, 55), (55, 51), (51, 50), (50, 43), (43, 44), (44, 54)], [(36, 37), (37, 48), (48, 45), (45, 47), (47, 49), (49, 36)],
#            [(5, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 5)], [(13, 8), (8, 6), (6, 12), (12, 15), (15, 16), (16, 13)],
#            [(18, 19), (19, 22), (22, 25), (25, 24), (24, 23), (23, 20), (20, 18)],
#            [(46, 47), (47, 45), (45, 41), (41, 40), (40, 35), (35, 38), (38, 46)],
#            [(11, 14), (14, 19), (19, 18), (18, 17), (17, 15), (15, 12), (12, 11)],
#            [(53, 52), (52, 42), (42, 41), (41, 45), (45, 48), (48, 50), (50, 51), (51, 53)],
#            [(8, 13), (13, 14), (14, 11), (11, 5), (5, 3), (3, 10), (10, 9), (9, 7), (7, 8)],
#            [(40, 41), (41, 42), (42, 44), (44, 43), (43, 33), (33, 25), (25, 22), (22, 29), (29, 39), (39, 40)],
#            [(30, 26), (26, 28), (28, 27), (27, 29), (29, 22), (22, 19), (19, 14), (14, 13), (13, 16), (16, 31), (31, 30)],
#            [(35, 34), (34, 27), (27, 28), (28, 32), (32, 24), (24, 25), (25, 33), (33, 37), (37, 36), (36, 38), (38, 35)]]

# Log faces
#
log_faces(g_faces)

logger.info("----------------------")
logger.info("END: Graph information")
logger.info("----------------------")
logger.info("")

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
# 4CT : Method similar to the Kempe reduction "patching" method
# 4CT : - For each loop remove an edge from a face <= F5, until the graph will have only four faces (an island with three lands)
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

logger.info("----------------------")
logger.info("BEGIN: Reduction phase")
logger.info("----------------------")
stats['time_ELABORATION_BEGIN'] = time.ctime()
stats['time_ELABORATION'] = datetime.now()

# Start the reduction process
#
is_the_end_of_the_reduction_process = False
f2_exist = True  # It is set to true only to force the search of F2 at the beginning of the algorithm
i_global_counter = 0
while is_the_end_of_the_reduction_process is False:

    logger.info("BEGIN %s: Main loop", i_global_counter)

    # Deep debug: Log all faces
    #
    # log_faces(g_faces)

    # f1, f2, edge_to_remove, rotated_edge_to_remove, len_of_the_face_to_reduce will be valid during the rest of this "while" loop after the first block ("Select an edge") has been executed
    #
    selected_face = []
    f1 = []
    f2 = []
    edge_to_remove = ()
    rotated_edge_to_remove = ()
    f1_plus_f2_temp = []  # It is used to speed up computation. At the beginning is used to see it the graph is_the_graph_one_edge_connected() and then reused

    # Select a face < F6
    # Since faces less then 6 always exist for any graph (Euler), I can take the first face that I find with that characteristics (<6)
    #
    # NOTE:
    # - I tried to process F5 first but the problem is that you can risk to end up with particular cases like an F2 at the end
    #   f1 = next((face for face in g_faces if len(face) == 5), next((face for face in g_faces if len(face) == 2), g_faces[0]))
    #
    if f2_exist is True:
        if len(g_faces[0]) != 2:
            f1 = next((f for f in g_faces if len(f) == 2), next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 5), g_faces[0]))))
        else:
            f1 = g_faces[0]
    else:
        if len(g_faces[0]) != 3:
            f1 = next((f for f in g_faces if len(f) == 3), next((f for f in g_faces if len(f) == 4), next((f for f in g_faces if len(f) == 5), g_faces[0])))
        else:
            f1 = g_faces[0]

    len_of_the_face_to_reduce = len(f1)

    logger.info("BEGIN %s: Search the right edge to remove (case: %s)", i_global_counter, len_of_the_face_to_reduce)

    # Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected
    #
    is_the_edge_to_remove_found = False
    i_edge = 0
    f1_edges_enumeration = range(0, len(f1) - 1)
    while is_the_edge_to_remove_found is False and i_edge < len_of_the_face_to_reduce:

        if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN %s: test the %s edge", i_global_counter, i_edge)

        # One edge separates two faces (pay attention to multiple edges == F2)
        # The edge to remove can be found in the list of faces as (v1, v2) or (v2, v1)
        # TODO: Instead of getting the edges in sequence, I should use a random selector (without repetitions)
        #
        i_edge = randint(0, len(f1) - 1)  # When stuck it you re-execute the program it should work
        edge_to_remove = f1[i_edge]
        rotated_edge_to_remove = rotate(edge_to_remove, 1)

        if logger.isEnabledFor(logging.DEBUG): logger.debug("len_of_the_face_to_reduce: %s", len_of_the_face_to_reduce)
        if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_to_remove: %s", edge_to_remove)
        if logger.isEnabledFor(logging.DEBUG): logger.debug("rotated_edge_to_remove: %s", rotated_edge_to_remove)

        # If F2, the rotated edge appears twice in the list of faces
        #
        if len_of_the_face_to_reduce == 2:

            # For F2 faces, edges will appear twice in all the edges lists of all faces
            #
            temp_f2 = [face for face in g_faces if rotated_edge_to_remove in face]
            temp_f2.remove(f1)
            f2 = temp_f2[0]
            f1_plus_f2_temp = join_faces(f1, f2, edge_to_remove)
        else:
            f2 = next(face for face in g_faces if rotated_edge_to_remove in face)
            f1_plus_f2_temp = join_faces(f1, f2, edge_to_remove)

        # The resulting graph is 1-edge-connected if the new face has an edge that does not divide two countries, but separates a portion of the same land
        #
        if is_the_graph_one_edge_connected(f1_plus_f2_temp) is True:

            # Skip the next edge, this is not good
            #
            i_edge += 1
        else:
            is_the_edge_to_remove_found = True
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edge to remove found :-) %s", edge_to_remove)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("f1: %s", f1)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("f2: %s", f2)
            if logger.isEnabledFor(logging.DEBUG): logger.debug("f1_plus_f2_temp: %s", f1_plus_f2_temp)

        if logger.isEnabledFor(logging.DEBUG): logger.debug("END %s: test the %s edge", i_global_counter, i_edge)

    # Check if math is right :-)
    #
    if is_the_edge_to_remove_found is False:
        logger.error("Unexpected condition (a suitable edge has not been found). Mario you'd better go back to paper")
        logger.info("For now I considered only the first face < F6. I may search the right edge in other faces < F6")
        logger.info("Should be easy to prove that among all faces < F6, an edge exist that if removed does not make the graph 1-edge-connected")
        exit(-1)

    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s)", i_global_counter, edge_to_remove, len_of_the_face_to_reduce)

    # Remove the edge of an F2 (multiple edge)
    #
    if len_of_the_face_to_reduce == 2:

        logger.info("BEGIN %s: Remove a multiple edge (case: %s)", i_global_counter, len_of_the_face_to_reduce)

        # Get the two vertices to join
        # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O
        #
        v1 = edge_to_remove[0]
        v2 = edge_to_remove[1]

        # >--0--<
        #
        # F2 is the zero in the center (in the drawing)
        #
        vertex_to_join_near_v1 = next(edge for edge in f2 if edge[0] == v1)[1]
        vertex_to_join_near_v2 = next(edge for edge in f2 if edge[1] == v2)[0]

        # f1 and f2 have been joined before to test 1-edge-connectivity ... I can use that!
        #
        g_faces.remove(f1)
        g_faces.remove(f2)
        g_faces.append(f1_plus_f2_temp)

        # I already prepared f1 and f2, but when these two faces are joined also the other face that has the two vertices has to be updated
        # A vertex is shared by three faces (two of these are f1 and f2). For this F2 case, the two vertices belong to only a third face
        # NOTE: For F3, F4, F5 ... v1 and v2 may have two different faces (other than f1 and f2)
        #
        third_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v1))
        remove_vertex_from_face(third_face_to_update, v1)
        remove_vertex_from_face(third_face_to_update, v2)  # For this F2 case, the two vertices belong to only a third face

        # Ariadne ball of thread. First parameter == 2, will tell that it was a multiple edge
        # [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        #
        ariadne_step = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        ariadne_string.append(ariadne_step)
        logger.info("ariadne_step: %s", ariadne_step)

        # Do one thing at a time and return at the beginning of the main loop
        #
        logger.info("END %s: Remove a multiple edge (case: %s)", i_global_counter, len_of_the_face_to_reduce)

        # f2_exist?
        #
        if len(f1_plus_f2_temp) == 2 or len(third_face_to_update) == 2:
            f2_exist = True
        else:
            f2_exist = False

    # Remove an F3 or F4 or F5
    #
    else:

        logger.info("BEGIN %s: Remove an F3, F4 or F5 (case: %s)", i_global_counter, len_of_the_face_to_reduce)

        # Get the vertices at the ends of the edge to remove
        # And find the other four neighbors :>.---.<: (If the --- is the removed edge, the four external dots represent the vertices I'm looking for)
        #
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

        # f1 and f2 have been joined before to test 1-edge-connectivity ... I can use that!
        #
        g_faces.remove(f1)
        g_faces.remove(f2)
        g_faces.append(f1_plus_f2_temp)

        # I already prepared f1 and f2, but when these two faces are joined also the other faces that has the two vertices have to be updated
        # A vertex is shared by three faces (two of these are f1 and f2)
        # NOTE: For F3, F4, F5 ... v1 and v2, most of the times will have f3 and f4 different ... but they can also be the same face
        #
        third_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v1))
        fourth_face_to_update = next(face for face in g_faces if check_if_vertex_is_in_face(face, v2))
        if logger.isEnabledFor(logging.DEBUG): logger.debug("third_face_to_update: %s", third_face_to_update)
        if logger.isEnabledFor(logging.DEBUG): logger.debug("fourth_face_to_update: %s", fourth_face_to_update)

        remove_vertex_from_face(third_face_to_update, v1)
        remove_vertex_from_face(fourth_face_to_update, v2)

        # Ariadne ball of thread
        # First parameter == len_of_the_face_to_reduce, will tell that it was a Fx face that has been removed (x = 3, 4 or 5)
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        #
        ariadne_step = [len_of_the_face_to_reduce, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        ariadne_string.append(ariadne_step)
        logger.info("ariadne_step: %s", ariadne_step)

        # Do one thing at a time and return at the beginning of the main loop
        #
        logger.info("END %s: Remove an F3, F4 or F5 (case: %s)", i_global_counter, len_of_the_face_to_reduce)

        # f2_exist?
        #
        if len(f1_plus_f2_temp) == 2 or len(third_face_to_update) == 2 or len(fourth_face_to_update) == 2:
            f2_exist = True
        else:
            f2_exist = False

    # Check 3-regularity (I commented this slow procedure: I let it run for a while, now I feel confident about this first part of the code)
    #
    # if check_regularity(g_faces) is False:
    #    logger.error("Unexpected condition (check_regularity is False). Mario you'd better go back to paper")
    #    log_faces(g_faces)
    #    exit(-1)

    # If the graph has been completely reduced, it will be a graph of four faces (an island with three lands) and six edges ... easily 3-edge-colorable
    # The graph is that of an island perfectly slit as a pie in 120 degree slices (just to visualize it)
    #
    # Note: With 4 faces is possible, in theory, to have other kind of maps, but since I removed always F2 faces first (multiple edge), this situation is not possible
    #
    if len(g_faces) == 4:

        # Graph reduced
        #
        is_the_end_of_the_reduction_process = True
        if logger.isEnabledFor(logging.DEBUG): logger.debug("The graph has been reduced")
        log_faces(g_faces)

    # END of main loop (-1 because the counte has been just incremented)
    #
    logger.info("END %s: Main loop", i_global_counter)
    logger.info("")

    # Something has been done! Plot it
    #
    if is_the_end_of_the_reduction_process is False:
        i_global_counter += 1

logger.info("--------------------")
logger.info("END: Reduction phase")
logger.info("--------------------")
logger.info("")

logger.info("-----------------------------------------")
logger.info("BEGIN: Print Ariadne's string information")
logger.info("-----------------------------------------")

# Log Ariadne's string information
#
for step in ariadne_string:
    logger.info("ariadne_string: %s", step)

logger.info("---------------------------------------")
logger.info("END: Print Ariadne's string information")
logger.info("---------------------------------------")
logger.info("")

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
# 4CT : Restore the edges one at a time and apply the half Kempe-cycle color switching method
# 4CT : Depending if the restored face is an F2, F3, F4, F5, different actions will be taken to be able to apply, at the end, the half Kempe-cycle color switching
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

logger.info("---------------------------")
logger.info("BEGIN: Reconstruction phase")
logger.info("---------------------------")

# At this point the graph has three faces (an island with two lands) and three edges ... easily 3-edge-colorable
# WARNING: the color of the edges of a multiedge graph cannot be changed, so it is necessary to delete and re-insert the edge
#
the_colored_graph = Graph(sparse = True)
the_colored_graph.allow_loops(False)
the_colored_graph.allow_multiple_edges(True)  # During the process I need this set to true

# Only four vertices have to be in the graph
#
all_vertices = [element for face in g_faces for edge in face for element in edge]
all_vertices = sorted(set(all_vertices))

for v in all_vertices:
    logger.info("v: %s", v)

if len(all_vertices) != 4:
    logger.error("Unexpected condition (vertices left are not 4). Mario you'd better go back to paper")
    exit(-1)

v1 = all_vertices[0]
v2 = all_vertices[1]
v3 = all_vertices[2]
v4 = all_vertices[3]

# At this point the graph is that of an island perfectly slit as a pie in 120 degree slices (just to visualize it)
# I decided to rebuild a new graph and, at the end of the process, to check if it is isomorphic to the original
#
# NOTE: It is not important to create the new graph selecting a particular order for the vertices ... they would all generate exactly the same graph
# I'll use: v1 at the center, v2, v3, v4 clockwise order (to visualize it in the mind)
#
the_colored_graph.add_edge(v1, v2, "red")
the_colored_graph.add_edge(v1, v3, "green")
the_colored_graph.add_edge(v1, v4, "blue")
the_colored_graph.add_edge(v2, v3, "blue")
the_colored_graph.add_edge(v3, v4, "red")
the_colored_graph.add_edge(v4, v2, "green")

# Start the rebuilding process
#
is_the_end_of_the_rebuild_process = False
while is_the_end_of_the_rebuild_process is False:

    # Get the string to walk back home
    #
    ariadne_step = ariadne_string.pop()
    logger.info("ariadne_step: %s", ariadne_step)

    # F2 = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
    #
    if ariadne_step[0] == 2:

        # CASE: F2
        # Update stats
        #
        stats['CASE-F2-01'] += 1

        logger.info("BEGIN: restore an F2 (multiple edge)")
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

        v1 = ariadne_step[1]
        v2 = ariadne_step[2]
        vertex_to_join_near_v1 = ariadne_step[3]
        vertex_to_join_near_v2 = ariadne_step[4]

        # For F2 to compute the new colors is easy
        #
        previous_edge_color = get_edge_color(the_colored_graph, (vertex_to_join_near_v1, vertex_to_join_near_v2))

        # Choose available colors
        #
        new_multiedge_color_one = get_the_other_colors([previous_edge_color])[0]
        new_multiedge_color_two = get_the_other_colors([previous_edge_color])[1]
        if logger.isEnabledFor(logging.DEBUG): logger.debug("new_multiedge_color_one: %s, new_multiedge_color_two: %s", new_multiedge_color_one, new_multiedge_color_two)

        # Delete the edge
        #
        the_colored_graph.delete_edge((vertex_to_join_near_v1, vertex_to_join_near_v2, previous_edge_color))

        # Restore the previous edge
        #
        the_colored_graph.add_edge(v1, vertex_to_join_near_v1, previous_edge_color)
        the_colored_graph.add_edge(v2, vertex_to_join_near_v2, previous_edge_color)
        the_colored_graph.add_edge(v1, v2, new_multiedge_color_one)
        the_colored_graph.add_edge(v2, v1, new_multiedge_color_two)

        logger.info("previous_edge_color: %s, new_multiedge_color_one: %s, new_multiedge_color_two: %s", previous_edge_color, new_multiedge_color_one, new_multiedge_color_two)

        # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
        # if is_well_colored(the_colored_graph) is False:
        #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
        #     exit(-1)

        logger.info("END: restore an F2 (multiple edge)")

    elif ariadne_step[0] == 3:

        # CASE: F3
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        # Update stats
        #
        stats['CASE-F3-01'] += 1
        logger.info("BEGIN: restore an F3")
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

        v1 = ariadne_step[1]
        v2 = ariadne_step[2]
        vertex_to_join_near_v1_on_the_face = ariadne_step[3]
        vertex_to_join_near_v2_on_the_face = ariadne_step[4]
        vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
        vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

        # For F3 to compute the new colors is easy (check also if it is a multiple edges)
        #
        if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex_to_join_near_v1_on_the_face: %s, vertex_to_join_near_v2_on_the_face: %s, vertex_to_join_near_v1_not_on_the_face: %s, vertex_to_join_near_v2_not_on_the_face: %s", vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face)

        # If e1 and e2 have the same vertices, they are the same multiedge
        #
        if (vertex_to_join_near_v1_on_the_face == vertex_to_join_near_v2_on_the_face) and (vertex_to_join_near_v1_not_on_the_face == vertex_to_join_near_v2_not_on_the_face):

            # Get the colors of the two edges (multiedge). Select only the two multiedges (e1, e2 with same vertices)
            #
            tmp_multiple_edges_to_check = the_colored_graph.edges_incident(vertex_to_join_near_v1_on_the_face)  # Three edges will be returned
            multiple_edges_to_check = [(va, vb, l) for (va, vb, l) in tmp_multiple_edges_to_check if (vertex_to_join_near_v1_not_on_the_face == va) or (vertex_to_join_near_v1_not_on_the_face == vb)]
            previous_edge_color_at_v1 = multiple_edges_to_check[0][2]
            previous_edge_color_at_v2 = multiple_edges_to_check[1][2]
        else:
            previous_edge_color_at_v1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))
            previous_edge_color_at_v2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))

        if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

        # Checkpoint
        #
        if previous_edge_color_at_v1 == previous_edge_color_at_v2:
            logger.error("Unexpected condition (for F3 faces two edges have a vertex in common, and so colors MUST be different at this point). Mario you'd better go back to paper")
            exit(-1)

        # Choose a different color
        #
        new_edge_color = get_the_other_colors([previous_edge_color_at_v1, previous_edge_color_at_v2])[0]

        # Delete the edges
        # Since e1 and e2 may be the same multiedge or maybe separately on different multiedge, I remove them using also the "label" parameter
        #
        the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
        the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))

        # Restore the previous edge
        #
        the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, previous_edge_color_at_v2)
        the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
        the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
        the_colored_graph.add_edge(v1, v2, new_edge_color)

        if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s, new_edge_color: %s", previous_edge_color_at_v1, previous_edge_color_at_v2, new_edge_color)

        # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
        # if is_well_colored(the_colored_graph) is False:
        #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
        #     exit(-1)

        logger.info("END: restore an F3")

    elif ariadne_step[0] == 4:

        # CASE: F4
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        #
        logger.info("BEGIN: restore an F4")
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

        v1 = ariadne_step[1]
        v2 = ariadne_step[2]
        vertex_to_join_near_v1_on_the_face = ariadne_step[3]
        vertex_to_join_near_v2_on_the_face = ariadne_step[4]
        vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
        vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

        # For F4 to compute the new colors is not so easy
        #
        previous_edge_color_at_v1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))
        previous_edge_color_at_v2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))
        if logger.isEnabledFor(logging.DEBUG): logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

        # For an F4, the top edge is the edge not adjacent to the edge to restore (as in a rectangular area)
        #
        edge_color_of_top_edge = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face))
        if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_color_of_top_edge: %s", edge_color_of_top_edge)

        # Handle the different cases
        #
        if previous_edge_color_at_v1 == previous_edge_color_at_v2:

            # Update stats
            #
            stats['CASE-F4-01'] += 1
            logger.info("BEGIN: restore an F4 - Same color at v1 and v2")
            if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

            # CASE: F4 SUBCASE: Same color at v1 and v2
            # Since edges at v1 and v2 are on the same Kempe cycle (with the top edge), I can also avoid the kempe chain color switching, since in this case the chain is made of three edges
            #
            the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
            the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))

            # Kempe chain color swap is done manually since the chain is only three edges long
            #
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

            # Just for sure. Is the top edge a multiedge? I need to verify it. It should't be
            #
            if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

            # Restore the other edges
            #
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
            the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

            # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
            # if is_well_colored(the_colored_graph) is False:
            #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
            #     exit(-1)

            logger.info("END: restore an F4 - Same color at v1 and v2")
        else:

            # In this case I have to check if the edges at v1 and v2 are on the same Kempe cycle
            #
            if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face), previous_edge_color_at_v1, previous_edge_color_at_v2) is True:

                # Update stats
                #
                stats['CASE-F4-02'] += 1

                logger.info("BEGIN: restore an F4 - The two edges are on the same Kempe cycle")
                if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

                # CASE: F4, SUBCASE: The two edges are on the same Kempe cycle
                # Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping
                #
                # I broke the cycle to apply the half Kempe chain color swapping
                #
                the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
                the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v2)

                # Half Kempe chain color swapping
                #
                kempe_chain_color_swap(the_colored_graph, (v1, vertex_to_join_near_v1_on_the_face), previous_edge_color_at_v1, previous_edge_color_at_v2)

                # Restore the other edges
                #
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
                the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, previous_edge_color_at_v2])[0])

                # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
                # if is_well_colored(the_colored_graph) is False:
                #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
                #     exit(-1)

                logger.info("END: restore an F4 - The two edges are on the same Kempe cycle")

            else:

                # Update stats
                #
                stats['CASE-F4-03'] += 1

                logger.info("BEGIN: restore an F4 - The two edges are NOT on the same Kempe cycle")
                if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

                # CASE: F4 SUBCASE: Worst case: The two edges are NOT on the same Kempe cycle
                # I'll rotate the colors of the cycle for the edge at v1, and then, since edge_color_at_v1 will be == edge_color_at_v2, apply CASE-001
                #
                kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), previous_edge_color_at_v1, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])
                previous_edge_color_at_v1 = previous_edge_color_at_v2

                # CASE: F4, SUBCASE: The two edges are now on the same Kempe cycle
                #
                the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
                the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))

                # Kempe chain color swap is done manually since the chain is only three edges long
                #
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

                # Just to be sure. Is the top edge a multiedge? I need to verify it. It should't be
                #
                if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                    the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                    the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                    logger.error("HERE?")  # This is only to verify if this condition is real
                    exit(-1)
                else:
                    the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

                # Restore the other edges
                #
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
                the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

                # if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
                # if is_well_colored(the_colored_graph) is False:
                #     logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
                #     exit(-1)

                logger.info("END: restore an F4 - The two edges are NOT on the same Kempe cycle")

        logger.info("END: restore an F4")

    elif ariadne_step[0] == 5:

        # CASE: F5
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        #
        logger.info("BEGIN: restore an F5")

        v1 = ariadne_step[1]
        v2 = ariadne_step[2]
        vertex_to_join_near_v1_on_the_face = ariadne_step[3]
        vertex_to_join_near_v2_on_the_face = ariadne_step[4]
        vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
        vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

        # I have to get the two edges that are on top
        # These are two edges that have near_v1_on_the_face and near_v2_on_the_face and a shared vertex
        # First thing: I need to get the vertex_in_the_top_middle
        #
        edges_at_vertices_near_v1_on_the_face = the_colored_graph.edges_incident([vertex_to_join_near_v1_on_the_face], labels = False)
        edges_at_vertices_near_v2_on_the_face = the_colored_graph.edges_incident([vertex_to_join_near_v2_on_the_face], labels = False)
        tmp_v1 = [item for sublist in edges_at_vertices_near_v1_on_the_face for item in sublist]
        tmp_v1.remove(vertex_to_join_near_v1_not_on_the_face)
        tmp_v2 = [item for sublist in edges_at_vertices_near_v2_on_the_face for item in sublist]
        tmp_v2.remove(vertex_to_join_near_v2_not_on_the_face)
        vertex_in_the_top_middle = list(set.intersection(set(tmp_v1), set(tmp_v2)))[0]

        # Useful to try to verify if the number of switches may be limited
        #
        restore_random_edge_to_fix_the_impasse = (0, 0)
        restore_color_one = ""
        restore_color_two = ""

        # The algorithm:
        #
        # - Check if c1 and c2 are on the same Kempe chain
        # - If not, try a random swap
        #   - First try a swap starting from an edge on the face
        #   - Then try a swap starting from a random edge of the kempe loop on v1
        #   - Then try a swap starting from a random edge of the entire graph
        #
        end_of_f5_restore = False
        i_attempt = 0
        while end_of_f5_restore is False:

            # For F5 to compute the new colors is difficult (and needs to be proved if always works in all cases)
            # I need to handle the different cases
            #
            c1 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face))
            c3 = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_in_the_top_middle))
            c4 = get_edge_color(the_colored_graph, (vertex_in_the_top_middle, vertex_to_join_near_v2_on_the_face))
            c2 = get_edge_color(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face))

            # F5-C1
            #
            if c1 == c2:

                # The four edges are: c1, c3, c4, c2==c1
                #
                # NOTE:
                # - Next comment was not true:
                #   - In case e1 and e2 are not on the same Kempe loop (c1, c3) or (c2, c4), the switch of the top colors (c3, c4) solves (I hope) the situation
                #
                if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c3):

                    logger.info("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

                    # Apply half Kempe loop color switching (c1, c3)
                    #
                    apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c3)
                    end_of_f5_restore = True

                    # Save the max
                    #
                    stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

                    # Update stats
                    #
                    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C3'] += 1
                    logger.info("END: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

                elif are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c4):

                    logger.info("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C4")

                    # Apply half Kempe loop color switching (c2==c1, c4)
                    #
                    apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c4)
                    end_of_f5_restore = True

                    # Save the max
                    #
                    stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

                    # Update stats
                    #
                    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C4'] += 1
                    logger.info("END: CASE-F5-C1==C2-SameKempeLoop-C1-C4")

            else:

                # NOTE:
                # - Next comment was true, but not useful:
                #   - In case e1 and e2 are not on the same Kempe loop (c1, c2), the swap of c2, c1 at e2 will give the the first case
                #
                if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c2):

                    logger.info("BEGIN: CASE-F5-C1!=C2-SameKempeLoop-C1-C4")

                    # Apply half Kempe loop color switching (c1, c2)
                    #
                    apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c2, c1, c2)
                    end_of_f5_restore = True

                    # Save the max
                    #
                    stats['MAX_RANDOM_KEMPE_SWITCHES'] = max(i_attempt, stats['MAX_RANDOM_KEMPE_SWITCHES'])

                    # Update stats
                    #
                    stats['CASE-F5-C1!=C2-SameKempeLoop-C1-C2'] += 1

                    logger.info("END: CASE-F5-C1!=C2-SameKempeLoop-C1-C2")

            # Try random switches around the graph for a random few times
            #
            # TODO: If the switch didn't solve the problem, reset the color and try another random switch. I need to verify if a single switch may fix am impasse
            #
            if end_of_f5_restore is False:

                # Attempts to change (swap) something in the graph
                #
                stats['TOTAL_RANDOM_KEMPE_SWITCHES'] += 1
                i_attempt += 1

                # Useful to try to verify if the number of switches may be limited. I need to verify if a single switch may fix all impasses
                #
                if i_attempt > 1:

                    # Restore previous coloring, at the beginning of the loop to fix this impasse
                    #
                    # OMG: I commented next line but it seems that this case (sage 4ct.py -p debug.input_planar_g_faces.serialized.400.bad_one_switch_is_not_enough) loops forever!!!??? :-(
                    #      ariadne_step: [5, 12, 7, 32, 6, 15, 10]
                    #
                    # kempe_chain_color_swap(the_colored_graph, restore_random_edge_to_fix_the_impasse, restore_color_one, restore_color_two)

                    restore_random_edge_to_fix_the_impasse = (0, 0)
                    restore_color_one = ""
                    restore_color_two = ""

                random_other_color_number = randint(0, 1)
                random_edge_to_fix_the_impasse = the_colored_graph.random_edge(labels = False)
                color_of_the_random_edge = get_edge_color(the_colored_graph, random_edge_to_fix_the_impasse)
                other_color = get_the_other_colors(color_of_the_random_edge)[random_other_color_number]
                kempe_chain_color_swap(the_colored_graph, random_edge_to_fix_the_impasse, color_of_the_random_edge, other_color)
                logger.info("random_edge: %s, Kempe color switch: (%s, %s)", random_edge_to_fix_the_impasse, color_of_the_random_edge, other_color)

                # Useful to try to verify if the number of switches may be limited. I need to verify if a single switch may fix all impasses
                #
                # restore_random_edge_to_fix_the_impasse = random_edge_to_fix_the_impasse
                # restore_color_one = other_color
                # restore_color_two = color_of_the_random_edge

                # Only for debug: which map is causing this impasse?
                #
                if i_attempt == 1000:
                    the_colored_graph.allow_multiple_edges(False)  # At this point there are no multiple edge
                    export_graph(the_colored_graph, "debug.really_bad_case")
                    logger.error("ERROR: Infinite loop. Chech the debug.really_bad_case.* files")

                    # This is used as a sentinel to use the runs.bash script
                    #
                    open("error.txt", 'a').close()
                    exit(-1)

        # END F5 has been restored
        #
        logger.info("END: restore an F5: %s", stats['TOTAL_RANDOM_KEMPE_SWITCHES'])

    # Separator
    #
    logger.info("")

    # After all cases
    #
    if not is_well_colored(the_colored_graph):
        logger.error("Unexpected condition (coloring is not valid). Mario you'd better go back to paper or learn to code")
        exit(-1)

    # If no other edges are to be restored, then I've done
    #
    if len(ariadne_string) == 0:
        is_the_end_of_the_rebuild_process = True

stats['time_ELABORATION_END'] = time.ctime()
stats['time_ELABORATION'] = (datetime.now() - stats['time_ELABORATION']).seconds
logger.info("-------------------------")
logger.info("END: Reconstruction phase")
logger.info("-------------------------")
logger.info("")

#######
#######
# 4CT : Show the restored and 4 colored map
#######
#######

logger.info("------------------------------------------")
logger.info("BEGIN: Show the restored and 4 colored map")
logger.info("------------------------------------------")

# Now I can restore the multiedge flag
#
if the_colored_graph.has_multiple_edges():
    logger.error("Unexpected condition (recreated graph has multiple edges at the end). Mario you'd better go back to paper")
    exit(-1)

the_colored_graph.allow_multiple_edges(False)  # At this point there are no multiple edge

# Check if the recreated graph is isomorphic to the original
#
logger.info("BEGIN: Check if isomorphic")
is_isomorphic = the_graph.is_isomorphic(the_colored_graph)
logger.info("END: Check if isomorphic")

if is_isomorphic is False:
    logger.error("Unexpected condition (recreated graph is different from the original). Mario you'd better go back to paper")

logger.info("BEGIN: print_graph (Original)")
print_graph(the_graph)
logger.info("END: print_graph (Original)")
logger.info("BEGIN: print_graph (Colored)")
print_graph(the_colored_graph)
logger.info("END: print_graph (Colored)")

logger.info("----------------------------------------")
logger.info("END: Show the restored and 4 colored map")
logger.info("----------------------------------------")

# Save the output graph
#
if args.output is not None:
    export_graph(the_colored_graph, args.output)

# Print statistics
#
print_stats(stats)

exit(0)
