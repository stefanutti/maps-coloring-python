#!/usr/bin/env sage

###
###
# 4CT: This program uses these approaches together
#      - It consider Tait edge coloring and the equivalency of the 3-edge-coloring (known as Tait coloring) and 4-face-coloring (the original four color theorem for maps)
#      - Uses a modified Kempe reduction method: it does not shrink a face (faces <= F5) down to a point, but removes a single edge from it (from faces <= F5)
#      - Uses a modified Kempe chain edge color switching: when restoring edges from the reduced graph, it will swap Half of the cycle of a color chain
#        - !!! While rebuilding a map, all chains are actually loops !!!
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
# - 01/Aug/2016 - I still need to complete the reconstruction of the F5 case (Since restoration of F5 is rare, the program already works most of the times)
#
# Todo:
# - Realize a version in which faces are made of lists of ordered vertices [1, 4, 7, 8] not edges [(1,4),(4,7),(7,8),(8,1)]. Would it be faster?
# - Realize the reconstruction phase with the lists of the edge representation instead of using the graph. It will be lot faster!
#
# Done:
# - Logging system
# - Sage doesn't handle multiple edges or loops when embedding is involved
#   - For example G.faces() executes an embedding and returns an error if the graph contains an F2 or a loop
#   - To handle it, this program avoid loops, removing first F2 g_faces (with care of F2 near F3 g_faces) and then handle F3, F4, F5 cases (unavoidable set)
# - Load external graphs (edgelist)
# - Save graphs (sdgelist)
#
###

######
######
# 4CT: Import stuffs
######
######

import argparse
import copy
import sys
import collections
from random import randint

import logging.handlers

import networkx

from sage.all import *

# This solves this issue: http://ask.sagemath.org/question/33727/logging-failing-after-a-while/
#
# Only when running the code in the cloud: https://cloud.sagemath.com/
# sage_server.MAX_OUTPUT_MESSAGES = 100000 # Needed for the cloud version of Sage

######
######
# 4CT: Helping functions
######
######


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

    logger.debug("BEGIN: kempe_chain_color_swap: %s, %s, %s", starting_edge, c1, c2)

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
    logger.debug("degree: %s", graph.degree(current_edge[direction]))
    if graph.degree(current_edge[direction]) != 3:
        direction = 0

    is_the_end_of_switch_process = False
    while is_the_end_of_switch_process is False:

        # Debug
        #
        logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)
        logger.debug("Vertex at direction: %s", current_edge[direction])

        logger.debug("Edges: %s, is_regular: %s", list(graph.edge_iterator(labels = True)), graph.is_regular(3))

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        #
        tmp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        logger.debug("tmp_next_edges_to_check: %s", tmp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in tmp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

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

            # Since the next edge may be a multiedge, I need to verify it first
            #
            if is_multiedge(graph, previous_edge[0], previous_edge[1]):
                the_colored_graph.delete_edge(previous_edge[0], previous_edge[1], previous_color)
                the_colored_graph.add_edge(previous_edge[0], previous_edge[1], current_color)
                logger.error("HERE?")   # This is only to verify if this condition is real
                exit(-1)
            else:
                graph.set_edge_label(previous_edge[0], previous_edge[1], current_color)

            if is_multiedge(graph, current_edge[0], current_edge[1]):
                the_colored_graph.delete_edge(current_edge[0], current_edge[1], current_color)
                the_colored_graph.add_edge(current_edge[0], current_edge[1], previous_color)
                logger.error("HERE?")   # This is only to verify if this condition is real
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
            logger.debug("degree: %s", graph.degree(current_edge[direction]))
            if graph.degree(current_edge[direction]) != 3:
                is_the_end_of_switch_process = True

    logger.debug("END: kempe_chain_color_swap")

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

    stats['RANDOM_LOOPS'] = 0

    return


############################################
# Check if egdes are on the same Kempe cycle
############################################
def are_edges_on_the_same_kempe_cycle(graph, e1, e2, c1, c2):

    logger.debug("BEGIN: are_edges_on_the_same_kempe_cycle: %s, %s, %s, %s", e1, e2, c1, c2)

    # Flag to return
    #
    are_edges_on_the_same_kempe_cycle = False

    out_of_scope_color = get_the_other_colors([c1, c2])[0]
    logger.debug("out_of_scope_color: %s", out_of_scope_color)

    # Start the loop at e1
    #
    current_edge = e1
    current_color = c1
    next_color = get_the_other_colors([out_of_scope_color, current_color])[0]
    logger.debug("current_color: %s", current_color)

    # From current edge, I'll search incident edges in one direction: 1 for the first edge, and then will decide the graph
    # (v1, v2) if a search all incident edges to v2 I'll have (v2, vx) and (v2, vy). Next vertex to choose will be vx or vy ... depending on the next chain color
    #
    direction = 1
    is_the_end_of_search_process = False
    while is_the_end_of_search_process is False:

        # Debug
        #
        logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        #
        tmp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        logger.debug("tmp_next_edges_to_check: %s", tmp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in tmp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

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
            are_edges_on_the_same_kempe_cycle = True
            is_the_end_of_search_process = True

        # Check if I've looped an entire cycle (of course without walking on e2 - previous check)
        #
        if are_the_same_edge(current_edge, e1):
            is_the_end_of_search_process = True

        # Debug info for this loop
        #
        logger.debug("current_color: %s, next_color: %s, current_edge: %s, are_edges_on_the_same_kempe_cycle: %s, is_the_end_of_search_process: %s", current_color, next_color, current_edge, are_edges_on_the_same_kempe_cycle, is_the_end_of_search_process)

    logger.debug("END: are_edges_on_the_same_kempe_cycle: %s", are_edges_on_the_same_kempe_cycle)

    return are_edges_on_the_same_kempe_cycle


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
def print_stats():
    logger.info("------------------")
    logger.info("BEGIN: Print stats")
    logger.info("------------------")

    ordered_stats = collections.OrderedDict(sorted(stats.items()))
    for stat in ordered_stats:
        logger.info("Stat: %s = %s times", stat, stats[stat])

    logger.info("----------------")
    logger.info("END: Print stats")
    logger.info("----------------")


#######################
# Check if well colored
#######################
def is_well_colored(graph):

    logger.debug("BEGIN: is_well_colored")

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

    logger.debug("END: is_well_colored")

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

    return


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

    logger.debug("BEGIN: join_faces")

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
    logger.debug("f1: %s", f1)
    logger.debug("f2: %s", f2)
    logger.debug("edge_to_remove_on_f1: %s", edge_to_remove_on_f1)
    logger.debug("index_of_edge_to_remove_on_f1: %s", index_of_edge_to_remove_on_f1)
    logger.debug("index_of_edge_to_remove_on_f2: %s", index_of_edge_to_remove_on_f2)
    logger.debug("Temporary f1_plus_f2: %s", f1_plus_f2)

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

    logger.debug("f1_plus_f2: %s", f1_plus_f2)

    if len(f1_plus_f2) == 2 and (f1_plus_f2[0][0] != f1_plus_f2[1][1] or f1_plus_f2[0][1] != f1_plus_f2[1][0]):
        logger.error("Unexpected condition (f2 faces have to be: [(v1, v2), (v2, v1)]. Mario you'd better go back to paper")
        exit(-1)

    logger.debug("END: join_faces")

    return f1_plus_f2


#################################################################################
# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#################################################################################
def is_the_graph_one_edge_connected(face):

    logger.debug("BEGIN: is_the_graph_one_edge_connected")

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

    logger.debug("END: is_the_graph_one_edge_connected: %s", is_the_graph_one_edge_connected)

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

    logger.debug("BEGIN: check_regularity")

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

    logger.debug("END: check_regularity: %s", is_three_regular)

    return is_three_regular


###################
# Log faces (DEBUG)
###################
def log_faces(faces):
    for face in faces:
        logger.debug("Face: %s", face)

    return


######################
# Get the other colors
######################
def get_the_other_colors(colors):
    return [x for x in ["red", "green", "blue"] if x not in colors]


##################################################################################################################
##################################################################################################################
# MAIN: 4CT - Create/upload the graph to color. it has to be planar and without loops and initially multiple edges
##################################################################################################################
##################################################################################################################

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
# -random <vertices> -input <file> -output <file>
#
parser = argparse.ArgumentParser(description = '4ct args')

group_input = parser.add_mutually_exclusive_group(required = True)
group_input.add_argument("-r", help = "Random graph (dual of a triangulation of N vertices)", nargs = 1, type = int)
group_input.add_argument("-i", help = "Input edgelist filename (https://networkx.readthedocs.io/en/stable/reference/readwrite.edgelist.html)", nargs = 1)
parser.add_argument("-o", help="Output edgelist filename (https://networkx.readthedocs.io/en/stable/reference/readwrite.edgelist.html)", nargs = 1, required = False)

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

# Dual of a triangulation
#
if args.r is not None:
    number_of_vertices_for_the_random_triangulation = args.r[0]
    tmp_g = graphs.RandomTriangulation(number_of_vertices_for_the_random_triangulation)  # Random triangulation on the surface of a sphere
    void = tmp_g.is_planar(set_embedding = True, set_pos = True)  # Cannot calculate the dual if the graph has not been embedded
    the_graph = graph_dual(tmp_g)  # The dual of a triangulation is a 3-regular planar graph
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

    # I need this (export + import) to be able to reproduce a test exactly in the same condition of a previous run
    # I cannot use the output file because it has different ordering of edges and vertices, and the execution would run differently (I experimented it on my skin)
    # The export function saves the graph using a different order for the edges (even if the graph are exactly the same graph)
    #
    the_graph.export_to_file("input_random_file.edgelist", format = "edgelist")
    the_graph = Graph(networkx.read_edgelist("input_random_file.edgelist"))
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal

    logger.info("3-regular (cubic) planar graph of %s vertices created", the_graph.order())

if args.i is not None:
    the_graph = Graph(networkx.read_edgelist(args.i[0]))
    the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value
    the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
    the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal

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

logger.info("BEGIN: Embed the graph into the plane (is_planar(set_embedding = True)")
void = the_graph.is_planar(set_embedding = True, set_pos = True)
logger.info("END: Embed the graph into the plane (is_planar(set_embedding = True)")

# Get the faces representation of the graph
# From now on, 'till the end of the reduction process, I'll use only this representation (join_faces, remove vertices, etc.) instead of the Graph object
# This is because the elaboration is a lot faster and I don't have to deal with the limit of sage about multiple edges and loops
# List it is sorted: means faces with len less than 6 are placed at the beginning
#
temp_g_faces = the_graph.faces()
temp_g_faces.sort(key = len)
g_faces = [face for face in temp_g_faces]

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
# 4CT : Method similar to the Kempe reduction "patching" method: for each loop remove an edge from a face <= F5, until the graph will have only four faces (an island with three lands)
#######
#######

logger.info("----------------------")
logger.info("BEGIN: Reduction phase")
logger.info("----------------------")

# Start the reduction process
#
is_the_end_of_the_reduction_process = False
i_global_counter = 0
while is_the_end_of_the_reduction_process is False:

    logger.info("BEGIN %s: Main loop", i_global_counter)

    # Deep debug: Log all faces
    #
    # log_faces(g_faces)

    # Do one thing at a time and return at the beginning of this top level loop
    #
    is_one_thing_done = False

    # f1, f2, edge_to_remove, rotated_edge_to_remove, len_of_the_face_to_reduce will be valid during the rest of this "while" loop after the first block ("Select an edge") has been executed
    #
    selected_face = []
    f1 = []
    f2 = []
    edge_to_remove = ()
    rotated_edge_to_remove = ()
    len_of_the_face_to_reduce = 0

    # Select a face < F6
    # Since faces less then 6 always exist for any graph (Euler) AND faces are sorted by their length, I can take the first one
    # f1 = next((face for face in g_faces if len(face) == 5), g_faces[0])  ## Test to elaborate F5 first
    #
    f1 = g_faces[0]
    len_of_the_face_to_reduce = len(f1)

    logger.info("BEGIN %s: Search the right edge to remove (case: %s)", i_global_counter, len_of_the_face_to_reduce)

    # Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected
    #
    is_the_edge_to_remove_found = False
    i_edge = 0
    while is_the_edge_to_remove_found is False and i_edge < len_of_the_face_to_reduce:

        logger.debug("BEGIN %s: test the %s edge", i_global_counter, i_edge)

        # One edge separates two faces (pay attention to multiple edges == F2)
        # The edge to remove can be found in the list of faces as (v1, v2) or (v2, v1)
        #
        edge_to_remove = f1[i_edge]
        rotated_edge_to_remove = rotate(edge_to_remove, 1)

        logger.debug("len_of_the_face_to_reduce: %s", len_of_the_face_to_reduce)
        logger.debug("edge_to_remove: %s", edge_to_remove)
        logger.debug("rotated_edge_to_remove: %s", rotated_edge_to_remove)

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
            logger.debug("Edge to remove found :-) %s", edge_to_remove)
            logger.debug("f1: %s", f1)
            logger.debug("f2: %s", f2)
            logger.debug("f1_plus_f2_temp: %s", f1_plus_f2_temp)

        logger.debug("END %s: test the %s edge", i_global_counter, i_edge)

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
        remove_vertex_from_face(third_face_to_update, v2)

        # Ariadne ball of thread. First parameter == 2, will tell that it was a multiple edge
        # [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        #
        ariadne_step = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        ariadne_string.append(ariadne_step)
        logger.info("ariadne_step: %s", ariadne_step)

        # Do one thing at a time and return at the beginning of the main loop
        #
        is_one_thing_done = True
        logger.info("END %s: Remove a multiple edge (case: %s)", i_global_counter, len_of_the_face_to_reduce)

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

        logger.debug("vertex_to_join_near_v1_on_the_face: %s", vertex_to_join_near_v1_on_the_face)
        logger.debug("vertex_to_join_near_v2_on_the_face: %s", vertex_to_join_near_v2_on_the_face)
        logger.debug("vertex_to_join_near_v1_not_on_the_face: %s", vertex_to_join_near_v1_not_on_the_face)
        logger.debug("vertex_to_join_near_v2_not_on_the_face: %s", vertex_to_join_near_v2_not_on_the_face)

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
        logger.debug("third_face_to_update: %s", third_face_to_update)
        logger.debug("fourth_face_to_update: %s", fourth_face_to_update)

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
        is_one_thing_done = True
        logger.info("END %s: Remove an F3, F4 or F5 (case: %s)", i_global_counter, len_of_the_face_to_reduce)

    # A final sort will reorder the list for the next cycle (I need to process faces with 2 or 3 edges first)
    # NOTE:
    # - I tried to process F5 first but the problem is that you can risk to end up with particular cases
    #   f1 = next((face for face in g_faces if len(face) == 2), next((face for face in g_faces if len(face) == 5), g_faces[0]))
    #   g_faces.remove(f1)
    #   g_faces.insert(0, f1)
    #
    g_faces.sort(key = len)
    # f1 = next((face for face in g_faces if len(face) == 3), next((face for face in g_faces if len(face) == 4), g_faces[0]))
    # g_faces.remove(f1)
    # g_faces.insert(0, f1)

    # Check 3-regularity
    #
    if check_regularity(g_faces) is False:
        logger.error("Unexpected condition (check_regularity is False). Mario you'd better go back to paper")
        log_faces(g_faces)
        exit(-1)

    # If the graph has been completely reduced, it will be a graph of four faces (an island with three lands) and six edges ... easily 3-edge-colorable
    # The graph is that of an island perfectly slit as a pie in 120 degree slices (just to visualize it)
    #
    if len(g_faces) == 4:

        # Graph reduced
        #
        is_the_end_of_the_reduction_process = True
        logger.debug("The graph has been reduced")
        log_faces(g_faces)

    # END of main loop (-1 because the counte has been just incremented)
    #
    logger.info("END %s: Main loop", i_global_counter)
    logger.info("")

    # Something has been done! Plot it
    #
    if is_the_end_of_the_reduction_process is False:
        i_global_counter += 1
        # the_graph.plot()
        # show(the_graph)

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
# 4CT : Restore the edges one at a time and apply the half Kempe-cycle color switching method
# 4CT : Depending if the restored face is an F2, F3, F4, F5, different actions will be taken to be able to apply, at the end, the half Kempe-cycle color switching
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
        logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

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
        logger.debug("new_multiedge_color_one: %s, new_multiedge_color_two: %s", new_multiedge_color_one, new_multiedge_color_two)

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

        logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
        if is_well_colored(the_colored_graph) is False:
            logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
            exit(-1)

        logger.info("END: restore an F2 (multiple edge)")

    elif ariadne_step[0] == 3:

        # CASE: F3
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        # Update stats
        #
        stats['CASE-F3-01'] += 1
        logger.info("BEGIN: restore an F3")
        logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

        v1 = ariadne_step[1]
        v2 = ariadne_step[2]
        vertex_to_join_near_v1_on_the_face = ariadne_step[3]
        vertex_to_join_near_v2_on_the_face = ariadne_step[4]
        vertex_to_join_near_v1_not_on_the_face = ariadne_step[5]
        vertex_to_join_near_v2_not_on_the_face = ariadne_step[6]

        # For F3 to compute the new colors is easy (check also if it is a multiple edges)
        #
        logger.debug("vertex_to_join_near_v1_on_the_face: %s, vertex_to_join_near_v2_on_the_face: %s, vertex_to_join_near_v1_not_on_the_face: %s, vertex_to_join_near_v2_not_on_the_face: %s", vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face)

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

        logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

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

        logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s, new_edge_color: %s", previous_edge_color_at_v1, previous_edge_color_at_v2, new_edge_color)

        logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
        if is_well_colored(the_colored_graph) is False:
            logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
            exit(-1)

        logger.info("END: restore an F3")

    elif ariadne_step[0] == 4:

        # CASE: F4
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        #
        logger.info("BEGIN: restore an F4")
        logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

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
        logger.debug("previous_edge_color_at_v1: %s, previous_edge_color_at_v2: %s", previous_edge_color_at_v1, previous_edge_color_at_v2)

        # For an F4, the top edge is the edge not adjacent to the edge to restore (as in a rectangular area)
        #
        edge_color_of_top_edge = get_edge_color(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face))
        logger.debug("edge_color_of_top_edge: %s", edge_color_of_top_edge)

        # Handle the different cases
        #
        if previous_edge_color_at_v1 == previous_edge_color_at_v2:

            # Update stats
            #
            stats['CASE-F4-01'] += 1
            logger.info("BEGIN: restore an F4 - Same color at v1 and v2")
            logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

            # CASE: F4 SUBCASE: Same color at v1 and v2
            # Since edges at v1 and v2 are on the same Kempe cycle (with the top edge), I can also avoid the kempe chain color switching, since in this case the chain is made of three edges
            #
            the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
            the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))

            # Kempe chain color swap is done manually since the chain is only three edges long
            #
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, edge_color_of_top_edge)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)

            # Since the top edge may be a multiedge, I need to verify it first
            #
            if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                logger.error("HERE?")   # This is only to verify if this condition is real
                exit(-1)
            else:
                the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

            # Restore the other edges
            #
            the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
            the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
            the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

            logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
            if is_well_colored(the_colored_graph) is False:
                logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
                exit(-1)

            logger.info("END: restore an F4 - Same color at v1 and v2")
        else:

            # In this case I have to check if the edges at v1 and v2 are on the same Kempe cycle
            #
            if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face), (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face), previous_edge_color_at_v1, previous_edge_color_at_v2) is True:

                # Update stats
                #
                stats['CASE-F4-02'] += 1

                logger.info("BEGIN: restore an F4 - The two edges are on the same Kempe cycle")
                logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

                # CASE: F4, SUBCASE: The two edges are on the same Kempe cycle
                # Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping
                #
                # I broke the cycle to apply the half Kempe chain color swapping
                #
                the_colored_graph.delete_edge((vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1))
                the_colored_graph.delete_edge((vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2))
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v2)

                logger.debug("bbb: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

                # Half Kempe chain color swapping
                #
                kempe_chain_color_swap(the_colored_graph, (v1, vertex_to_join_near_v1_on_the_face), previous_edge_color_at_v1, previous_edge_color_at_v2)

                # Restore the other edges
                #
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
                the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, previous_edge_color_at_v2])[0])

                logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
                if is_well_colored(the_colored_graph) is False:
                    logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
                    exit(-1)

                logger.info("END: restore an F4 - The two edges are on the same Kempe cycle")

            else:

                # Update stats
                #
                stats['CASE-F4-03'] += 1

                logger.info("BEGIN: restore an F4 - The two edges are NOT on the same Kempe cycle")
                logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))

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

                # Since the top edge may be a multiedge, I need to verify it first
                #
                if is_multiedge(the_colored_graph, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face):
                    the_colored_graph.delete_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, edge_color_of_top_edge)
                    the_colored_graph.add_edge(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)
                    logger.error("HERE?")   # This is only to verify if this condition is real
                    exit(-1)
                else:
                    the_colored_graph.set_edge_label(vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, previous_edge_color_at_v1)

                # Restore the other edges
                #
                the_colored_graph.add_edge(v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
                the_colored_graph.add_edge(v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
                the_colored_graph.add_edge(v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

                logger.debug("Edges: %s, is_regular: %s", list(the_colored_graph.edge_iterator(labels = True)), the_colored_graph.is_regular(3))
                if is_well_colored(the_colored_graph) is False:
                    logger.error("Unexpected condition (Not well colored). Mario you'd better go back to paper")
                    exit(-1)

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

        # Three cycles max:
        # - the first cycle normalize the condition (if not already normalized): With c1 == c2 (at the two edges e1 and e2)
        # - the second cycle connect (on the same Kempe loop) e1 and e2
        # - the third cycle compute the new color
        #
        end_of_f5_restore = False
        i_loop = 0
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

                logger.info("C1==C2")

                # The four edges are: c1, c3, c4, c2==c1
                # In case e1 and e2 are not on the same Kempe loop (c1, c3) or (c2, c4), the switch of the top colors (c3, c4) solves (I hope) the situation
                #
                if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c3):

                    logger.info("BEGIN: CASE-F5-C1==C2-SameKempeLoop-C1-C3")

                    # Apply half Kempe loop color switching (c1, c3)
                    #
                    apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c1, c1, c3)
                    end_of_f5_restore = True

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

                    # Update stats
                    #
                    stats['CASE-F5-C1==C2-SameKempeLoop-C1-C4'] += 1

                    logger.info("END: CASE-F5-C1==C2-SameKempeLoop-C1-C4")
            else:

                logger.info("C1!=C2")

                # In case e1 and e2 are not on the same Kempe loop (c1, c2), the swap of c2, c1 at e2 will give the the first case
                #
                if are_edges_on_the_same_kempe_cycle(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), (vertex_to_join_near_v2_not_on_the_face, vertex_to_join_near_v2_on_the_face), c1, c2):

                    logger.info("BEGIN: CASE-F5-C1!=C2-SameKempeLoop-C1-C4")

                    # Apply half Kempe loop color switching (c1, c2)
                    #
                    apply_half_kempe_loop_color_switching(the_colored_graph, ariadne_step, c1, c2, c1, c2)
                    end_of_f5_restore = True

                    # Update stats
                    #
                    stats['CASE-F5-C1!=C2-SameKempeLoop-C1-C4'] += 1

                    logger.info("END: CASE-F5-C1!=C2-SameKempeLoop-C1-C4")

            # Try a random switch
            #
            if end_of_f5_restore is False:
                random_iterations = randint(1, 4)

                for i_random in range(1, random_iterations):
                    random_color_number = randint(0, 1)
                    edge_color_of_random_edge = the_colored_graph.random_edge(labels = False)
                    random_color = get_edge_color(the_colored_graph, edge_color_of_random_edge)
                    kempe_chain_color_swap(the_colored_graph, edge_color_of_random_edge, random_color, get_the_other_colors([random_color])[random_color_number])
                    logger.info("Random: %s, random_edge: %s, random_color: %s", stats['RANDOM_LOOPS'], edge_color_of_random_edge, random_color)

                stats['RANDOM_LOOPS'] += 1

                if stats['RANDOM_LOOPS'] == 1000:
                    print_graph(the_colored_graph)
                    logger.info("faces: %s", the_colored_graph.faces())
                    exit(-1)

                # if random_edge == 1:
                #     kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v1_on_the_face), c1, get_the_other_colors([c1])[random_color])
                # elif random_edge == 2:
                #     kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v2_not_on_the_face), c2, get_the_other_colors([c2])[random_color])
                # elif random_edge == 3:
                #     kempe_chain_color_swap(the_colored_graph, (vertex_to_join_near_v1_on_the_face, vertex_in_the_top_middle), c3, get_the_other_colors([c3])[random_color])
                # elif random_edge == 4:
                #     kempe_chain_color_swap(the_colored_graph, (vertex_in_the_top_middle, vertex_to_join_near_v2_on_the_face), c4, get_the_other_colors([c4])[random_color])

                # logger.info("c1: %s, c2: %s, c3: %s, c4: %s, random_edge: %s, random_color: %s", c1, c2, c3, c4, random_edge, random_color)

            # Update counter
            #
            i_loop += 1

        # END F5 has been restored
        #
        logger.info("END: restore an F5: %s", i_loop)

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
if args.o is not None:

    # Possibilities: adjlist, dot, edgelist, gexf, gml, graphml, multiline_adjlist, pajek, yaml
    # Format chosen: edgelist
    #
    logger.info("------------------------------------------------")
    logger.info("BEGIN: Save the 4 colored map in edgelist format")
    logger.info("------------------------------------------------")

    the_colored_graph.export_to_file(args.o[0], format = "edgelist")
    logger.info("File saved: %s", args.o[0])

    logger.info("----------------------------------------------")
    logger.info("END: Save the 4 colored map in edgelist format")
    logger.info("----------------------------------------------")

# Print statistics
#
print_stats()
