###
#
# 4CT: Generate random planar graphs without using graphs library and most important without using complex algotithms, as the planarity embedding or testing functions
#
# I directly use the planar graph representation of a map, as described here:
#
# http://doc.sagemath.org/html/en/reference/graphs/sage/graphs/generic_graph.html#sage.graphs.generic_graph.GenericGraph.faces
# graphs.TetrahedralGraph().faces()
# [[(0, 1), (1, 2), (2, 0)],
#  [(3, 2), (2, 1), (1, 3)],
#  [(3, 0), (0, 2), (2, 3)],
#  [(3, 1), (1, 0), (0, 3)]]
#
# A combinatorial embedding of a graph is a clockwise ordering of the neighbors of each vertex.
#
# This is the base map
# https://4coloring.wordpress.com/2018/04/23/large-planar-map-creation-using-python/
#
# g_faces = [[(1, 2), (2, 3), (3, 1)], [(1, 3), (3, 4), (4, 1)], [(1, 4), (4, 2), (2, 1)], [(2, 4), (4, 3), (3, 2)]]
# 
# Vertex "1" is the center of the tetrahedron
# Vertices "2", "3". "4" are the vertices around the center (clockwise)
# Faces are represented "clockwise"
# Last face is alway the ocean
# The ocean is represented "counter-clockwise"
#
###
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# History:
# - 19/Mar/2018 - Creation data
#
# BACKLOG:
#
# Done:
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

######
######
######
# 4CT: Import stuffs
######
######
######

import argparse
import sys
import logging
import random
import json

######
######
######
# 4CT: Functions
######
######
######

#############################################
# Rotate elements (works for lists and tuple)
#############################################
def rotate(l, n):
    return l[n:] + l[:n]


###########
# Log faces
###########
def log_faces(faces):
    logger.debug("=======")
    for face in faces:
        logger.debug("Face: %s", face)
    logger.debug("=======")

    return


##############
# Split a face
##############
def split_face(selected_face, index_of_the_first_selected_edge, index_of_the_second_selected_edge):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: split_face")

    # Return the two new faces (list of two lists)
    #
    the_two_new_faces_to_return = []

    # First face
    #
    new_first_face = selected_face[:index_of_the_first_selected_edge] + [(selected_face[index_of_the_first_selected_edge][0], i_vertex)] + [(i_vertex, i_vertex + 1)] + [(i_vertex + 1, selected_face[index_of_the_second_selected_edge][1])] + selected_face[index_of_the_second_selected_edge + 1:]

    # For the second face you need to check for limit case
    #
    if (index_of_the_first_selected_edge != index_of_the_second_selected_edge):
        new_second_face = [(i_vertex, selected_face[index_of_the_first_selected_edge][1])] + selected_face[index_of_the_first_selected_edge + 1:index_of_the_second_selected_edge] + [(selected_face[index_of_the_second_selected_edge][0], i_vertex + 1)] + [(i_vertex + 1, i_vertex)]
    else:
        new_second_face = [(i_vertex, i_vertex + 1), (i_vertex + 1, i_vertex)]

    # List them up
    #
    the_two_new_faces_to_return = [new_first_face, new_second_face]

    # Debug
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new_first_face: %s", new_first_face)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new_second_face: %s", new_second_face)

    # Return the two new faces
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: split_face")
    return the_two_new_faces_to_return


########################
# Add a vertex to a face
########################
def add_vertex_to_face(face_to_update, edge_to_search, vertex_to_insert):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: add_vertex_to_face")

    # Insert the new vertex
    #
    index_where_to_insert_the_new_vertex = face_to_update.index(edge_to_search)
    new_face_to_return = face_to_update[:index_where_to_insert_the_new_vertex] + [(face_to_update[index_where_to_insert_the_new_vertex][0], vertex_to_insert)] + [(vertex_to_insert, face_to_update[index_where_to_insert_the_new_vertex][1])] + face_to_update[index_where_to_insert_the_new_vertex + 1:]

    # Return the new faces
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: add_vertex_to_face: %s", new_face_to_return)
    return new_face_to_return


########################
# Statistics
########################
def map_statistics(g_faces):

    # Return the new faces
    #
    if logger.isEnabledFor(logging.INFO): logger.info("Statistics up to F6, of the created map with %s faces:", len(g_faces))
    for i in range(2, 7):
        if logger.isEnabledFor(logging.INFO): logger.info("- F%s: %s", i, sum(len(face) == i for face in g_faces))

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
# 4CT: Main
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
# -f <faces> -o <file>
#
parser = argparse.ArgumentParser(description='4ct args')
parser.add_argument("-v", "--vertices", help="Stop at v vertices", type=int, default=10, required=True)
parser.add_argument("-o", "--output", help="Save a json", required=False)
args = parser.parse_args()

# This is the base map - See drawing: 07/Apr/2018, pag 0/n
#
g_faces = [[(1, 2), (2, 3), (3, 1)], [(1, 3), (3, 4), (4, 1)], [(1, 4), (4, 2), (2, 1)], [(2, 4), (4, 3), (3, 2)]]

# Basic tests
#
# i_vertex = 7
#
# test_face = [(1,2), (2,3), (3,4), (4, 5), (5, 6), (6, 1)]
# logger.info("TEST: %s", test_face)
# split_face(test_face, 0, 0)
# split_face(test_face, 1, 4)
# split_face(test_face, 5, 5)
# new_face = add_vertex_to_face(test_face, (6,1), 9)
# logger.info("TEST: new_face = %s", new_face)
#
# test_face = [(5,6), (6,5)]
# logger.info("TEST: %s", test_face)
# split_face(test_face, 0, 0)
# split_face(test_face, 0, 1)
# split_face(test_face, 1, 1)
#
# exit (-1)

# Aliases for args
#
number_of_vertices_to_generate = args.vertices

# Main loop: up to the number of requested vertices to be created (1 new face every 1 new edge = 2 new vertices)
#
i_vertex = 5
if logger.isEnabledFor(logging.DEBUG): log_faces(g_faces)
while i_vertex <= number_of_vertices_to_generate:

    # Choose a random edge of a random face
    # -2 will exclude also the ocean face (the last face)
    #
    i_selected_face = random.randint(0, len(g_faces) - 2)
    selected_face = g_faces[i_selected_face]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Selected face: %s", selected_face)

    # Choose two random edges of the previously selected face. The two random edges may be the same edge
    # From the middle of these two selected edges, a new edge is going to be created
    # See drawing: 07/Apr/2018, pag 2/n
    #
    index_of_the_first_selected_edge = random.randint(0, len(selected_face) - 1)
    first_selected_edge = selected_face[index_of_the_first_selected_edge]
    index_of_the_second_selected_edge = random.randint(index_of_the_first_selected_edge, len(selected_face) - 1)
    second_selected_edge = selected_face[index_of_the_second_selected_edge]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Selected edges: %s at index = %s, %s at index = %s", first_selected_edge, index_of_the_first_selected_edge, second_selected_edge, index_of_the_second_selected_edge)

    # Add the new edge from the first_selected_edge to the second_selected_edge (may be the same edge)
    #
    the_two_new_faces = split_face(selected_face, index_of_the_first_selected_edge, index_of_the_second_selected_edge)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("the_two_new_faces = %s", the_two_new_faces)

    ####
    # STEP: Start adjusting the two faces (may be also just one) touched by the new edge that has been created
    ####
    #
    # Depending on the situation, one or two faces may be found (touched)
    # See drawing: 07/Apr/2018, pag 1/n
    #
    # Edge to find
    #
    edge_to_find = rotate(first_selected_edge, 1)

    # Search the map
    #
    faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]

    if (len(selected_face) == 2):
        faces_that_have_been_found.remove(selected_face)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)

    # Depending on the situation, some checks need to be done
    #
    if (len(faces_that_have_been_found) == 1):
        face_to_adjust = faces_that_have_been_found[0]
        adjusted_face = add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex)
    elif (len(faces_that_have_been_found) == 2):
        if (len(faces_that_have_been_found[0]) == 2):
            face_to_adjust = faces_that_have_been_found[0]
            adjusted_face = add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex)
        else:
            face_to_adjust = faces_that_have_been_found[1]
            adjusted_face = add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_vertex)
    else:
        logger.error("Unexpected condition. Mario you'd better go back to paper (1)")
        exit(-1)

    # Adjust the list of faces
    #
    if (g_faces.index(face_to_adjust) == (len(g_faces) - 1)):
        g_faces.remove(face_to_adjust)
        g_faces.append(adjusted_face)
    else:
        g_faces.remove(face_to_adjust)
        g_faces.insert(-1, adjusted_face)

    ####
    # STEP: Adjust the second face. See drawing: 07/Apr/2018, pag 1/n
    ####
    #
    # Edge to find: in case of the new edge starts and ends at the same edge ... and since I've already updated the face, I'll adjust the search accordingly
    #
    if (index_of_the_first_selected_edge == index_of_the_second_selected_edge):
        edge_to_find = (second_selected_edge[1], i_vertex)
    else:
        edge_to_find = rotate(second_selected_edge, 1)

    # Search the map
    #
    faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]

    # There is a particular case here to consider. If the starting face was a F2 and if the new edge starts and ends at the same edge
    #
    # if (len(selected_face) == 2):
    #
    if ((len(selected_face) == 2) and (index_of_the_first_selected_edge != index_of_the_second_selected_edge)):
        faces_that_have_been_found.remove(selected_face)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)

    # Depending on the situation, some checks need to be done: same as above, but with vertex number = (i_vertex + 1)
    #
    if (len(faces_that_have_been_found) == 1):
        face_to_adjust = faces_that_have_been_found[0]
        adjusted_face = add_vertex_to_face(
            faces_that_have_been_found[0], edge_to_find, i_vertex + 1)
    elif (len(faces_that_have_been_found) == 2):
        if (len(faces_that_have_been_found[0]) == 2):
            face_to_adjust = faces_that_have_been_found[0]
            adjusted_face = add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex + 1)
        else:
            face_to_adjust = faces_that_have_been_found[1]
            adjusted_face = add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_vertex + 1)
    else:
        logger.error("Unexpected condition. Mario you'd better go back to paper (2)")
        exit(-1)

    # Adjust the list of faces
    #
    if (g_faces.index(face_to_adjust) == (len(g_faces) - 1)):
        g_faces.remove(face_to_adjust)
        g_faces.append(adjusted_face)
    else:
        g_faces.remove(face_to_adjust)
        g_faces.insert(-1, adjusted_face)

    # Adjust the list of all faces
    # Insert is used to leave the ocean as the last face
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("remove the selected face = %s", selected_face)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new fases = %s, %s", the_two_new_faces[0], the_two_new_faces[1])
    g_faces.remove(selected_face)
    g_faces.insert(-1, the_two_new_faces[0])
    g_faces.insert(-1, the_two_new_faces[1])

    # Let's move to the next face
    #
    i_vertex += 2

    # Logging time
    #
    if logger.isEnabledFor(logging.DEBUG): log_faces(g_faces)
    if ((i_vertex -1) % 1000) == 0:
        if logger.isEnabledFor(logging.INFO): logger.info("Loop: %s", i_vertex)


# Save the graph
#
if args.output is not None:
    with open(args.output, "w") as fp:
        json.dump(g_faces, fp)
else:
    print(g_faces)

# Print statistics
#
map_statistics(g_faces)