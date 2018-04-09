###
###
#
# 4CT: Generate random graphs
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
import collections
import logging.handlers
import random

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
    for face in faces:
        logger.info("Face: %s", face)

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
    new_first_face = selected_face[:index_of_the_first_selected_edge] + [(selected_face[index_of_the_first_selected_edge][0], i_face)] + [(i_face, i_face + 1)] + [(i_face + 1, selected_face[index_of_the_second_selected_edge][1])] + selected_face[index_of_the_second_selected_edge + 1:]

    # For the second face you need to check for limit case 
    #
    if (index_of_the_first_selected_edge != index_of_the_second_selected_edge):
        new_second_face = [(i_face, selected_face[index_of_the_first_selected_edge][1])] + selected_face[index_of_the_first_selected_edge + 1:index_of_the_second_selected_edge] + [(selected_face[index_of_the_second_selected_edge][0], i_face + 1)] + [(i_face + 1, i_face)]
    else:
        new_second_face = [(i_face, i_face + 1), (i_face + 1, i_face)]

    # List them up
    #
    the_two_new_faces_to_return = [new_first_face, new_second_face]

    # Debug
    #
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new_first_face: %s", new_first_face)
    if logger.isEnabledFor(logging.DEBUG): logger.debug("new_second_face: %s", new_second_face)

    # Return the two new faces
    #
    return the_two_new_faces_to_return


########################
# Add a vertex to a face
########################
def add_vertex_to_face(face_to_update, edge_to_find, vertex_to_insert):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: add_vertex_to_face")

    face_to_update



######
######
######
# 4CT: Main
######
######
######

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
# -f <faces> -o <file>
#
parser = argparse.ArgumentParser(description = '4ct args')

group_input = parser.add_mutually_exclusive_group(required = False)
group_input.add_argument("-f", "--faces", help = "Stop at f faces", type = int, default = 10)
parser.add_argument("-o", "--output", help = "Save a .edgelist file (networkx), plus a .dot file (networkx). Specify the file without extension", required = False)

args = parser.parse_args()

# This is the base map - See drawing: 07/Apr/2018, pag 0/n
#
g_faces = [[(1, 2), (2, 3), (3, 1)], [(1, 3), (3, 4), (4, 1)], [(1, 4), (4, 2), (2, 1)], [(2, 4), (4, 3), (3, 2)]]
log_faces(g_faces)

# Basic tests
#
# i_face = 2
#
# test_face = [(1,2), (2,3), (3,4), (4, 5), (5, 6), (6, 1)]
# logger.info("TEST: %s", test_face)
# split_face(test_face, 0, 0)
# split_face(test_face, 1, 4)
# split_face(test_face, 5, 5)
#
# test_face = [(1,2), (2,1)]
# logger.info("TEST: %s", test_face)
# split_face(test_face, 0, 0)
# split_face(test_face, 0, 1)
# split_face(test_face, 1, 1)
#
# exit (-1)

# Main loop: up to the number of requested faces to be created (1 new face every 1 new edge)
#
number_of_faces_to_generate = args.faces
i_face = 5
while i_face < number_of_faces_to_generate:

    # Choose a random edge of a random face
    # -2 will exclude also the ocean face
    #
    i_selected_face = random.randint(0, len(g_faces) - 2)
    selected_face = g_faces[i_selected_face]
    logger.info("Selected face: %s", selected_face)

    # Choose two random edges of the previously selected face. The two random edges may be the same edge
    # From the middle of these two selected edges, a new edge is created - See drawing: 07/Apr/2018, pag 2/n
    #
    index_of_the_first_selected_edge = random.randint(0, len(selected_face) - 1)
    first_selected_edge = selected_face[index_of_the_first_selected_edge]
    index_of_the_second_selected_edge = random.randint(index_of_the_first_selected_edge, len(selected_face) - 1)
    second_selected_edge = selected_face[index_of_the_second_selected_edge]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("Selected edges: %s at index = %s, %s at index = %s", first_selected_edge, index_of_the_first_selected_edge, second_selected_edge, index_of_the_second_selected_edge)

    # Add the new edge from the first_selected_edge to the second_selected_edge (may be the same edge)
    #
    the_two_new_faces = split_face(selected_face, index_of_the_first_selected_edge, index_of_the_second_selected_edge)

    # Adjust the two faces (may be also just one) touched by the new edge that has been created
    # Depending on the situation, one or two faces may be found (touched) - See drawing: 07/Apr/2018, pag 1/n
    #
    edge_to_find = rotate(first_selected_edge, 1)
    faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)
    if (len (faces_that_have_been_found) == 1):
        add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_face)
    elif (len (faces_that_have_been_found) == 2):
        if (len(faces_that_have_been_found[0]) == 2):
            add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_face)
        else:
            add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_face)
    else:
        logger.error("Unexpected condition. Mario you'd better go back to paper")
        exit (-1)

    # In case of the new edge touches the same edge and since I've already updated the face, I'll adjust the search - See drawing: 07/Apr/2018, pag 1/n
    #
    if (index_of_the_first_selected_edge == index_of_the_second_selected_edge):
        edge_to_find = (second_selected_edge[1], i_face)
    else:
        edge_to_find = rotate(second_selected_edge, 1)

    # Adjust the second faces
    #
    faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)
    if (len (faces_that_have_been_found) == 1):
        add_vertex_to_face(faces_that_have_been_found[0], i_face)
    elif (len (faces_that_have_been_found) == 2):
        if (len(faces_that_have_been_found[0]) == 2):
            add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_face)
        else:
            add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_face)
    else:
        logger.error("Unexpected condition. Mario you'd better go back to paper")
        exit (-1)

    # Adjust the list of all faces
    # insert is used to leave the ocean as the last face
    #
    g_faces.remove(selected_face)
    g_faces.insert(-1, the_two_new_faces[0])
    g_faces.insert(-1, the_two_new_faces[1])

    # Let's move to the next face
    #
    i_face += 1
