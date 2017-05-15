#!/usr/bin/env sage

#######
#######
# 4CT : Four color method using Tait edge three coloring + Kempe face reduction method + Kempe (half) chain color switching
#######
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
# Notes:
# - This program uses these approaches together
#   - It consider Tait edge coloring and the equivalency of the 3-edge-coloring (known as Tait coloring) and 4-face-coloring (the original four color theorem for maps)
#   - Uses a modified Kempe reduction method: it does not shrink a face (g_faces <= F5) down to a point, but removes a single edge from it (for g_faces <= F5)
#   - Uses a modified Kempe chain edge color switching: when restoring edges from the reduced graph, it will swap Half of the cycle of a color chain
#
# Todo:
# - Why g_faces() need to run the embedding planarity algorithm for cubic planar graph?
#   - I mean, if I know that the graph is planar (because I built it so), why do i need to make it planar to have the g_faces()
#
# Done:
# - Logging system
# - Sage doesn't handle multiple edges or loops when embedding is involved
#   - For example G.faces() executes an embedding and returns an error if the graph contains an F2 or a loop
#   - To handle it, this program avoid loops, removing first F2 g_faces (with care of F2 near F3 g_faces) and then handle F3, F4, F5 cases (unavoidable set)
#
#######

import sys

import logging.handlers
import copy

from sage.all import *

# This solves this issue: http://ask.sagemath.org/question/33727/logging-failing-after-a-while/
#
# Only when running the code in the cloud: https://cloud.sagemath.com/
# sage_server.MAX_OUTPUT_MESSAGES = 100000 # Needed for the cloud version of Sage

#######
#######
# 4CT : functions
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
def check_graph_at_beginning(g):
    # Check 3-regularity
    #
    if g.is_regular(3) is False:
        logger.info("Error: The graph is not 3-regular")
        quit()
    else:
        logger.info("Good. The graph is 3-regular")

    # Check loops
    #
    if g.has_loops() is True:
        logger.error("ERROR: It seems that loops are difficult to handle during reduction and recoloring, so I'll start without them and avoid their creation during the reduction process")
        quit()
    else:
        logger.info("OK. The graph does not have loops. Consider that this program will avoid their creation during the reduction process")

    # Check multiple edges
    #
    if g.has_multiple_edges() is True:
        logger.error("ERROR: The graph has multiple edges. At the beginning multiple edges are not permitted")
        quit()
    else:
        logger.info("OK. The graph does not have multiple edges. Consider that this program will also handle multiple edges during the reduction process")

    # Check if the graph is planar
    #
    if g.is_planar() is False:
        logger.error("ERROR: The graph is not planar")
        quit()
    else:
        logger.info("OK. The graph is planar")

    logger.info("It has number_of_faces = %s", len(g.faces()))

    return


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

    # You can only use this function if at least one face has length > 2
    #
    if len(f1) == 2 and len(f2) == 2:
        logger.error("Unexpected condition (f2 + f2 would generate a single edge face). Mario you'd better study math a bit longer")
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
    logger.debug("f1 = %s", f1)
    logger.debug("f2 = %s", f2)
    logger.debug("edge_to_remove_on_f1 = %s", edge_to_remove_on_f1)
    logger.debug("index_of_edge_to_remove_on_f1 = %s", index_of_edge_to_remove_on_f1)
    logger.debug("index_of_edge_to_remove_on_f2 = %s", index_of_edge_to_remove_on_f2)
    logger.debug("Temporary f1_plus_f2 = %s", f1_plus_f2)

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

    logger.debug("f1_plus_f2 = %s", f1_plus_f2)

    if len(f1_plus_f2) == 2 and (f1_plus_f2[0][0] != f1_plus_f2[1][1] or f1_plus_f2[0][1] != f1_plus_f2[1][0]):
        logger.error("Unexpected condition (f2 faces have to be: [(v1, v2), (v2, v1)]. Mario you'd better study math a bit longer")
        exit(-1)

    return f1_plus_f2


#################################################################################
# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#################################################################################
def check_if_one_edge_connected(face):

    # Return variable
    #
    is_one_edge_connected_graph = False

    # This is true only for faces != F2
    # NOTE: F2 faces have this representation: [(v1, v2), (v2, v1)] that is correct
    #
    if len(face) != 2:

        # Search the list [(),(),...,()]
        #
        i_edge = 0
        while is_one_edge_connected_graph is False and i_edge < len(face):
            reverse_edge = rotate(face[i_edge], 1)

            # Start the search
            #
            if reverse_edge in face[i_edge + 1:]:
                is_one_edge_connected_graph = True
            else:

                # Move to the next edge
                #
                i_edge += 1

    # Return
    #
    return is_one_edge_connected_graph


############################
# Check if vertex is in face
############################
def check_if_vertex_is_in_face(face, vertex):
    return any([edge for edge in face if edge[0] == vertex or edge[1] == vertex])


####################
# Check if 3 regular
####################
def check_regularity(faces):

    # Return variable
    #
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

    # Return
    #
    return is_three_regular


###########
# Log faces
###########
def log_faces(faces):
    for face in g_faces:
        logger.debug("Face: %s", face)

    return


##############################################
##############################################
# 4CT : Constants and variables initialization
##############################################
##############################################

# Set logging facilities: LEVEL XXX
#
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)

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

# General plot options
#
edge_color_by_label = {'green': 'green', 'blue': 'blue', 'red': 'red'}

# It will contain items made of lists of values to find the way back to the original graph (Ariadne's String Myth)
#
ariadne_string = []

###################################################################################################################
###################################################################################################################
# MAIN: 4CT - Create/upload the graph to color. it has to be planar and without loops. Multiple edges are permitted
###################################################################################################################
###################################################################################################################

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

# 2) simplicial_complexes
#
# the_graph = simplicial_complexes.RandomTwoSphere(100).flip_graph()
# the_graph.allow_loops(False)
# the_graph.allow_multiple_edges(True)
# the_graph.relabel()

# 3: Dual of a triangulation
#
number_of_vertices_for_the_random_triangulation = 30
tmp_g = graphs.RandomTriangulation(number_of_vertices_for_the_random_triangulation)  # Random triangulation on the surface of a sphere
void = tmp_g.is_planar(set_embedding = True, set_pos = True)  # Cannot calculate the dual if the graph has not been embedded
the_graph = graph_dual(tmp_g)  # The dual of a triangulation is a 3-regular planar graph
the_graph.allow_loops(False)  # At the beginning and during the process I'll avoid this situation anyway
the_graph.allow_multiple_edges(True)  # During the reduction process the graph may have multiple edges - It is normal
the_graph.relabel()  # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

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
void = the_graph.is_planar(set_embedding = True, set_pos = True)

# Get the faces representation of the graph
# From now on, 'till the end of the reduction process, I'll use only this representation (join_faces, remove vertices, etc.) instead of the Graph object
# List it is sorted: means faces with len less than 6 are at the beginning
#
temp_g_faces = the_graph.faces()
temp_g_faces.sort(key = len)
g_faces = [face for face in temp_g_faces]

logger.info("----------------------")
logger.info("END: Graph information")
logger.info("----------------------")
logger.info("")

#######
#######
# 4CT : Method similar to the Kempe reduction "patching" method: for each loop remove an edge from a face <= F5, until the graph will have only three faces (an island with two lands)
#######
#######

is_the_end_of_the_reduction_process = False

logger.info("----------------------")
logger.info("BEGIN: Reduction phase")
logger.info("----------------------")

# Start the reduction process
#
i_global_counter = 0
while is_the_end_of_the_reduction_process is False:

    logger.info("BEGIN %s: Main loop", i_global_counter)

    # Log all faces
    #
    log_faces(g_faces)

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

    logger.info("BEGIN %s: Search the right edge to remove", i_global_counter)

    # Select a face < F6
    # Since faces less then 6 always exist for any graph (Euler) AND faces are sorted by their length, I can take the first one
    #
    f1 = g_faces[0]
    len_of_the_face_to_reduce = len(f1)

    # Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected
    #
    is_the_edge_to_remove_found = False
    i_edge = 0
    while is_the_edge_to_remove_found is False and i_edge < len_of_the_face_to_reduce:

        logger.info("BEGIN %s: test the %s edge", i_global_counter, i_edge)

        # One edge separates two faces (pay attention to multiple edges == F2)
        # The edge to remove can be found in the list of faces as (v1, v2) or (v2, v1)
        #
        edge_to_remove = f1[i_edge]
        rotated_edge_to_remove = rotate(edge_to_remove, 1)

        logger.debug("len_of_the_face_to_reduce = %s", len_of_the_face_to_reduce)
        logger.debug("edge_to_remove = %s", edge_to_remove)
        logger.debug("rotated_edge_to_remove = %s", rotated_edge_to_remove)

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
        if check_if_one_edge_connected(f1_plus_f2_temp):
            i_edge += 1
        else:
            is_the_edge_to_remove_found = True
            logger.debug("Edge to remove found :-) %s", edge_to_remove)
            logger.debug("f1 = %s", f1)
            logger.debug("f2 = %s", f2)
            logger.debug("f1_plus_f2_temp = %s", f1_plus_f2_temp)

        logger.info("END %s: test the %s edge", i_global_counter, i_edge)

    # Check if math hypothesis was right
    #
    if is_the_edge_to_remove_found is False:
        logger.error("Unexpected condition (a suitable edge has not been found). Mario you'd better study math a bit longer")
        logger.info("For now I considered only the first face < F6. I may search the right edge in other faces < F6")
        logger.info("I should prove that among all faces < F6, an edge exist that if remove does not make the graph 1-edge-connected")
        exit(-1)

    logger.info("END %s: Search the right edge to remove", i_global_counter)

    # Remove the edge of an F2 (multiple edge)
    #
    if len_of_the_face_to_reduce == 2:

        logger.info("BEGIN %s: Remove a multiple edge", i_global_counter)

        # Get the two vertices to join
        # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O
        #
        v1 = edge_to_remove[0]
        v2 = edge_to_remove[1]
        
        # >--0--<
        #
        vertex_to_join_near_v1 = next(edge for edge in f2 if edge[1] == v1)[0]
        vertex_to_join_near_v2 = next(edge for edge in f2 if edge[0] == v2)[1]

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
        item = [2, v1, v2, vertex_to_join_near_v1, vertex_to_join_near_v2]
        ariadne_string.append(item)
        logger.debug("ariadne_string: %s", item)

        # Do one thing at a time and return at the beginning of the main loop
        #
        is_one_thing_done = True
        logger.info("END %s: Remove a multiple edge", i_global_counter)

    # Remove an F3 or F4 or F5
    #
    if len_of_the_face_to_reduce > 2 and is_one_thing_done is False and is_the_end_of_the_reduction_process is False:

        logger.info("BEGIN %s: Remove an F3, F4 or F5", i_global_counter)

        # Get the vertices at the ends of the edge to remove
        # And find the other four neighbors :>.---.<: (If the --- is the removed edge, the four external dots represent the vertices I'm looking for)
        #
        v1 = edge_to_remove[0]
        v2 = edge_to_remove[1]

        vertex_to_join_near_v1_on_the_face = next(edge for edge in f1 if edge[1] == v1)[0]
        vertex_to_join_near_v2_on_the_face = next(edge for edge in f1 if edge[0] == v2)[1]
        vertex_to_join_near_v1_not_on_the_face = next(edge for edge in f2 if edge[0] == v1)[1]
        vertex_to_join_near_v2_not_on_the_face = next(edge for edge in f2 if edge[1] == v2)[0]

        logger.debug("vertex_to_join_near_v1_on_the_face = %s", vertex_to_join_near_v1_on_the_face)
        logger.debug("vertex_to_join_near_v2_on_the_face = %s", vertex_to_join_near_v2_on_the_face)
        logger.debug("vertex_to_join_near_v1_not_on_the_face = %s", vertex_to_join_near_v1_not_on_the_face)
        logger.debug("vertex_to_join_near_v2_not_on_the_face = %s", vertex_to_join_near_v2_not_on_the_face)

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
        logger.debug("third_face_to_update = %s", third_face_to_update)
        logger.debug("fourth_face_to_update = %s", fourth_face_to_update)

        remove_vertex_from_face(third_face_to_update, v1)
        remove_vertex_from_face(fourth_face_to_update, v2)

        # Ariadne ball of thread
        # First parameter == len_of_the_face_to_reduce, will tell that it was a Fx face that has been removed (x = 3, 4 or 5)
        # [x, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        #
        item = [len_of_the_face_to_reduce, v1, v2, vertex_to_join_near_v1_on_the_face, vertex_to_join_near_v2_on_the_face, vertex_to_join_near_v1_not_on_the_face, vertex_to_join_near_v2_not_on_the_face]
        ariadne_string.append(item)
        logger.debug("ariadne_string: %s", item)

        # Do one thing at a time and return at the beginning of the main loop
        #
        is_one_thing_done = True
        logger.info("END %s: Remove an F3, F4 or F5", i_global_counter)

    # A final sort will reorder the list for the next cycle
    # TODO: Verify if it is possible to insert the new face in the righ sorted place. For now re-sort alllllllllll
    #
    g_faces.sort(key = len)

    # Check 3-regularity
    #
    if check_regularity(g_faces) is False:
        logger.error("Unexpected condition (check_regularity is False). Mario you'd better study math a bit longer")
        log_faces(g_faces)
        exit(-1)

    # If the graph has been completely reduced, it will be a graph of three faces (an island with two lands) and three edges ... easily 3-edge-colorable
    #
    if len(g_faces) == 3:

        # Graph reduced
        #
        is_the_end_of_the_reduction_process = True
        logger.debug("The graph has been reduced")
        log_faces(g_faces)

    # Something has been done! Plot it
    #
    if is_the_end_of_the_reduction_process is False:
        i_global_counter += 1
        # the_graph.plot()
        # show(the_graph)

    # END of main loop (-1 because the counte has been just incremented)
    #
    logger.info("END %s: Main loop", i_global_counter - 1)
    logger.info("")
    logger.info("")

logger.info("--------------------")
logger.info("END: Reduction phase")
logger.info("--------------------")
logger.info("")

logger.info("-----------------------------------")
logger.info("BEGIN: Ariadne's string information")
logger.info("-----------------------------------")

# Log Ariadne's string information
#
for i in ariadne_string:
    logger.info("ariadne_string: %s", i)

logger.info("---------------------------------")
logger.info("END: Ariadne's string information")
logger.info("---------------------------------")
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
# NOTE: the color of the edges of a multi edge graph cannot be changed
#
the_colored_graph = Graph(sparse = True)
the_colored_graph.allow_loops(False)
the_colored_graph.allow_multiple_edges(True)

v1 = g_faces[0][0][0]
v2 = g_faces[0][0][1]
logger.debug("v1 = %s, v2 = %s", v1, v2)
the_colored_graph.add_edge(v1, v2, "red")
the_colored_graph.add_edge(v1, v2, "green")
the_colored_graph.add_edge(v1, v2, "blu")

# the_graph.show()

is_the_end_of_the_rebuild_process = False
while is_the_end_of_the_rebuild_process is False:

    # Get the edge to restore
    #
    ariadne_step = ariadne_string.pop()
    logger.info("ariadne_step: %s", ariadne_step)

    if ariadne_step[0] == 2:
        logger.info("BEGIN: restore a multiple edge")
        logger.info("END: restore a multiple edge")
    if ariadne_step[0] == 3:
        logger.info("BEGIN: restore an F3")
        logger.info("END: restore an F3")
    if ariadne_step[0] == 4:
        logger.info("BEGIN: restore an F4")
        logger.info("END: restore an F4")
    if ariadne_step[0] == 5:
        logger.info("BEGIN: restore an F5")
        logger.info("END: restore an F5")

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

show(the_graph)
