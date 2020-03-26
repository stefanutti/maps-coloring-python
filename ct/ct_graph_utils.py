###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# History:
# - 10/Set/2019 - Creation data
#
# TODOs:
# - Fix docstring for each function
#
# Done:
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

import logging

from sage.all import *

logger = logging.getLogger(__name__)

# Valid colors
VALID_COLORS = ['red', 'green', 'blue']


def echo_function(text):
    """
    A true echo is a single reflection of the sound source

    Parameters
    ----------
    text: text to echo

    Returns
    -------
    text: return the input text parameter
    """

    print("echo: " + text)

    return text


def check_graph_planarity_3_regularity_no_loops(graph):
    """
    Check if I can work with this graph: has to be planar and 3 regular (planar cubic graph)

    Parameters
    ----------
        graph: The graph to check
    """

    # Check 3-regularity
    if graph.is_regular(3) is False:
        logger.error("Error: The graph is not 3-regular")
        exit(-1)
    else:
        logger.info("OK. The graph is 3-regular")

    # Check loops
    if graph.has_loops() is True:
        logger.error("ERROR: It seems that loops are difficult to handle during reduction and recoloring, so start without them and avoid their creation during the reduction process")
        exit(-1)
    else:
        logger.info("OK. The graph does not have loops. Consider that this program will avoid their creation during the reduction process")

    # Check multiple edges
    # It maybe important because many sofrware do not work with planarity algorithms when multiple edhes are present
    # But the algorithm that I implemented works also with multiple edges ... hence for now I comment this
    # if graph.has_multiple_edges() is True:
    #     logger.error("ERROR: The graph has multiple edges. At the beginning multiple edges are not permitted")
    #     exit(-1)
    # else:
    #     logger.info("OK. The graph does not have multiple edges. Consider that this program will also handle multiple edges during the reduction and reconstruction process")

    # Check if the graph is planar
    if graph.is_planar() is False:
        logger.error("ERROR: The graph is not planar")
        exit(-1)
    else:
        logger.info("OK. The graph is planar")

    # Additional info
    logger.info("The graph has %s vertices and %s edges", graph.order(), graph.size())

    return


def kempe_chain_color_swap(graph, starting_edge, c1, c2):
    """
    Execute a Kempe chain color swapping.\n
    Works for chains and cycles and consider also multiedges cases.

    Parameters
    ----------
        graph: The graph
        starting_edge: (n, m) the edge where to start the swap
        c1: the color to switch with c2
        c2: the color to switch with c1
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: kempe_chain_color_swap: %s, %s, %s", starting_edge, c1, c2)

    # Start the loop at e1
    current_edge = starting_edge
    previous_color = "none"  # Not important here, will be used later
    current_color = c1
    next_color = c2

    # From current edge, I'll search incident edges in one direction
    # The check is important to recognize the half cycle color switching to an entire cycle color switching
    direction = 1
    if logger.isEnabledFor(logging.DEBUG): logger.debug("degree: %s", graph.degree(current_edge[direction]))
    if graph.degree(current_edge[direction]) != 3:
        direction = 0

    is_the_end_of_switch_process = False
    while is_the_end_of_switch_process is False:

        # Debug
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Vertex at direction: %s", current_edge[direction])

        if logger.isEnabledFor(logging.DEBUG): logger.debug("Edges: %s, is_regular: %s", list(graph.edge_iterator(labels=True)), graph.is_regular(3))

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        temp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        if logger.isEnabledFor(logging.DEBUG): logger.debug("temp_next_edges_to_check: %s", temp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in temp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

        # Save current edge and vertex direction
        previous_edge = current_edge
        previous_vertex = current_edge[direction]

        # Check if I've looped an entire cycle
        if are_the_same_edge(starting_edge, edges_to_check[0]) or are_the_same_edge(starting_edge, edges_to_check[1]):
            is_the_end_of_switch_process = True
        else:

            # Check the color of the two edges and find the next chain
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
            previous_color = current_color
            current_color = next_color
            next_color = previous_color

            # Now: swap colors
            #
            # graph.set_edge_label(previous_edge[0], previous_edge[1], current_color)
            # graph.set_edge_label(current_edge[0], current_edge[1], previous_color)

            # Just to be sure. Is it a multiedge? I need to verify it. It should't be
            if is_multiedge(graph, previous_edge[0], previous_edge[1]):
                the_colored_graph.delete_edge(previous_edge[0], previous_edge[1], previous_color)
                the_colored_graph.add_edge(previous_edge[0], previous_edge[1], current_color)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                graph.set_edge_label(previous_edge[0], previous_edge[1], current_color)

            # Just to be sure. Is it a multiedge? I need to verify it. It should't be
            if is_multiedge(graph, current_edge[0], current_edge[1]):
                the_colored_graph.delete_edge(current_edge[0], current_edge[1], current_color)
                the_colored_graph.add_edge(current_edge[0], current_edge[1], previous_color)
                logger.error("HERE?")  # This is only to verify if this condition is real
                exit(-1)
            else:
                graph.set_edge_label(current_edge[0], current_edge[1], previous_color)

            # Update direction
            if current_edge[0] == previous_vertex:
                direction = 1
            else:
                direction = 0

            # Check if I've reached the end of a chain
            if logger.isEnabledFor(logging.DEBUG): logger.debug("degree: %s", graph.degree(current_edge[direction]))
            if graph.degree(current_edge[direction]) != 3:
                is_the_end_of_switch_process = True

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: kempe_chain_color_swap")

    return


def faces_by_vertices(g):
    """
    Return a face as a list of ordered vertices. Used to create random graphs.\n
    Taken on the internet (http://trac.sagemath.org/ticket/6236).

    Parameters
    ----------
        g: The graph

    Returns
    -------
        list_faces: Returns a face as a list of ordered vertices
    """

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


def graph_dual(g):
    """
    Return the dual of a graph. Used to create random graphs.\n
    Taken on the internet: to make a dual of a triangulation (http://trac.sagemath.org/ticket/6236).

    Parameters
    ----------
        g: The graph

    Returns
    -------
        dual: The dual of a graph
    """

    f = [tuple(face) for face in faces_by_vertices(g)]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]
    dual = Graph([f_edges, lambda f1, f2: set(f1).intersection([(e[1], e[0]) for e in f2])])

    return dual


def print_graph(graph):
    """
    Print graph.

    Parameters
    ----------
        graph: The graph to print
    """
    for vertex in graph.vertex_iterator():
        edges = graph.edges_incident(vertex)
        logger.info("vertex: %s, edges: %s, is well colored: %s", vertex, edges, are_incident_edges_well_colored(graph, vertex))

    return


def is_well_colored(graph):
    """
    Check if the graph is well colored.

    Parameters
    ----------
        graph: The graph to check

    Returns
    -------
        is_well_colored: True or False if the graph is well colored
    """

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

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_well_colored (%s)", is_well_colored)

    return is_well_colored


def are_incident_edges_well_colored(graph, vertex):
    """
    Check if the incident edges to a give vertex are well colored.

    Parameters
    ----------
        graph: The graph to check
        vertex: The vertex to check

    Returns
    -------
        are_incident_edges_well_colored: True or False if all edges of the given vertex are well colored
    """

    are_incident_edges_well_colored = False

    edges = graph.edges_incident(vertex)

    colors_around_this_vertex = [edges[0][2], edges[1][2], edges[2][2]]

    if all(color in VALID_COLORS for color in colors_around_this_vertex):
        are_incident_edges_well_colored = True

    return are_incident_edges_well_colored


def get_edge_color(graph, edge):
    """
    Get the color of an edge.\n
    In case of multiedge it will return one of the two edges.\n
    This is not a problem because when I'll rebuild the graph the deletes will be done namely using the three attributes (v1, v2, label) (label is the color).

    Parameters
    ----------
        graph: The graph to check
        edge: The edge you want the color

    Returns
    -------
        color_to_return: The color of the given edge
    """

    v1 = edge[0]
    v2 = edge[1]

    color_to_return = next(label for (va, vb, label) in graph.edges() if (va, vb) == (v1, v2) or (va, vb) == (v2, v1))

    return color_to_return


def is_multiedge(graph, v1, v2):
    """
    Are the two vertices connected by more than one edge?

    Parameters
    ----------
        graph: The graph to check
        v1: First vertex
        v2: Second vertex

    Returns
    -------
        is_multiedge: True or False it the two vertices are connected by more than one edge
    """

    is_multiedge = False

    if len(graph.edge_boundary([v1], [v2])) > 1:
        is_multiedge = True

    return is_multiedge


def check_if_vertex_is_in_face(face, vertex):
    """
    Check if the given vertex is in face

    Parameters
    ----------
        face: The face to check
        vertex: The vertex to check and see if it is part of the given face

    Returns
    -------
        True or False if the the given vertex is in face
    """

    return any([edge for edge in face if edge[0] == vertex or edge[1] == vertex])


def check_regularity(faces):
    """
    Check if 3 regular

    Parameters
    ----------
        faces: The faces of the graph to check

    Returns
    -------
        is_three_regular: True or False if the graph is three regular
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: check_regularity")

    is_three_regular = True

    # get all vertices
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


def create_graph_from_planar_representation(faces):
    """
    Create a graph from its planar representation

    Parameters
    ----------
        faces: The faces of the graph to create

    Returns
    -------
        new_graph: The graph created from its planar representation
    """

    # Create the graph from the list of faces
    flattened_egdes = [edge for face in faces for edge in face]

    # TODO: This cycle remove duplicates. Two adjacent faces, list at least one edge twice
    for edge in flattened_egdes:
        reverse_edge = (edge[1], edge[0])
        if reverse_edge in flattened_egdes:
            flattened_egdes.remove(reverse_edge)

    new_graph = Graph(sparse=True)
    new_graph.allow_loops(False)
    new_graph.allow_multiple_edges(True)
    for edge_to_add in flattened_egdes:
        new_graph.add_edge(edge_to_add)

    return new_graph


def export_graph(graph_to_export, name_of_file_without_extension):
    """
    Export graph

    Parameters
    ----------
        graph_to_export: The graph to export
        name_of_file_without_extension: The name that will be used to export the graph
    """

    # Save: edgelist, dot
    #
    # Other possibilities: adjlist, gexf, gml, graphml, multiline_adjlist, pajek, yaml
    #
    # Additional note (17/Oct/2016): I decided to save the graph also as a .dot file
    # The problem with dot file is that you can write .dot files directly, but you cannot read them back if you don't install an additional package
    logger.info("------------------------------------------------")
    logger.info("BEGIN: Save the 4 colored map in edgelist format")
    logger.info("------------------------------------------------")
    graph_to_export.export_to_file(name_of_file_without_extension + ".edgelist", format="edgelist")
    graph_to_export.graphviz_to_file_named(name_of_file_without_extension + ".dot", edge_labels=True, vertex_labels=False)
    logger.info("File saved: %s", name_of_file_without_extension)

    # Replace label with color
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


def are_the_same_edge(e1, e2):
    """
    Check if two edges are the same edge.\n
    (v1, v2) == (v2, v1)\n
    (v1, v2, color) == (v1, v2)\n
    (v1, v2, color) == (v2, v1)

    Parameters
    ----------
        e1: First edge
        e2: Second edge

    Returns
    -------
        True or False if it is the same edge or not
    """

    return e1[0] in e2 and e1[1] in e2


def are_edges_on_the_same_kempe_cycle(graph, e1, e2, c1, c2):
    """
    Check if egdes are on the same Kempe cycle

    Parameters
    ----------
        graph: The graph to check
        e1: First edge
        e2: Second edge
        c1: First color
        c2: Second color the the chain (a chain is defined by two colors)

    Returns
    -------
        are_edges_on_the_same_kempe_cycle_flag: True or False if the two edges are part of the same cycle
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: are_edges_on_the_same_kempe_cycle: %s, %s, %s, %s", e1, e2, c1, c2)

    # Flag to return
    are_edges_on_the_same_kempe_cycle_flag = False

    out_of_scope_color = get_the_other_colors([c1, c2])[0]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("out_of_scope_color: %s", out_of_scope_color)

    # Start the loop at e1
    current_edge = e1
    current_color = c1
    next_color = get_the_other_colors([out_of_scope_color, current_color])[0]
    if logger.isEnabledFor(logging.DEBUG): logger.debug("current_color: %s", current_color)

    # From current edge, I'll search incident edges in one direction: 1 for the first edge, and then will decide the graph
    # (v1, v2) if a search all incident edges to v2 I'll have (v2, vx) and (v2, vy). Next vertex to choose will be vx or vy ... depending on the next chain color
    direction = 1
    is_the_end_of_search_process = False
    while is_the_end_of_search_process is False:

        # Debug
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        temp_next_edges_to_check = graph.edges_incident(current_edge[direction])  # Still need to remove current edge
        if logger.isEnabledFor(logging.DEBUG): logger.debug("temp_next_edges_to_check: %s", temp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in temp_next_edges_to_check if (v1, v2) != (current_edge[0], current_edge[1]) and (v2, v1) != (current_edge[0], current_edge[1])]
        if logger.isEnabledFor(logging.DEBUG): logger.debug("vertex: %s, edges_to_check: %s", current_edge[direction], edges_to_check)

        # Check the color of the two edges and find the next chain
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
        current_color = next_color
        next_color = get_the_other_colors([out_of_scope_color, current_color])[0]

        # Update direction
        if current_edge[0] == previous_vertex:
            direction = 1
        else:
            direction = 0

        # Check if I've reached e2
        if are_the_same_edge(current_edge, e2):
            are_edges_on_the_same_kempe_cycle_flag = True
            is_the_end_of_search_process = True

        # Check if I've looped an entire cycle (of course without walking on e2 - previous check)
        if are_the_same_edge(current_edge, e1):
            is_the_end_of_search_process = True

        # Debug info for this loop
        if logger.isEnabledFor(logging.DEBUG): logger.debug("current_color: %s, next_color: %s, current_edge: %s, are_edges_on_the_same_kempe_cycle_flag: %s, is_the_end_of_search_process: %s", current_color, next_color, current_edge, are_edges_on_the_same_kempe_cycle, is_the_end_of_search_process)

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: are_edges_on_the_same_kempe_cycle_flag: %s", are_edges_on_the_same_kempe_cycle_flag)

    return are_edges_on_the_same_kempe_cycle_flag


def apply_half_kempe_loop_color_switching(graph, ariadne_step, color_at_v1, color_at_v2, swap_c1, swap_c2):
    """
    Apply half Kempe loop color switching

    Parameters
    ----------
        graph: The graph
        ariadne_step: This step
        color_at_v1: Second edge
        color_at_v2: First color
        swap_c1: Second color the the chain (a chain is defined by two colors)
        swap_c2: Second color the the chain (a chain is defined by two colors)

    Returns
    -------
        are_edges_on_the_same_kempe_cycle_flag: True or False if the two edges are part of the same cycle
    """

    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    v1_on_the_face = ariadne_step[3]
    v2_on_the_face = ariadne_step[4]
    v1_not_on_the_face = ariadne_step[5]
    v2_not_on_the_face = ariadne_step[6]

    # I broke the cycle to apply the half Kempe chain color swapping
    # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
    graph.delete_edge(v1_on_the_face, v1_not_on_the_face, color_at_v1)
    graph.delete_edge(v2_on_the_face, v2_not_on_the_face, color_at_v2)
    graph.add_edge(v1, v1_on_the_face, color_at_v1)
    graph.add_edge(v2, v2_on_the_face, color_at_v2)

    # Half Kempe chain color swapping
    kempe_chain_color_swap(graph, (v1, v1_on_the_face), swap_c1, swap_c2)

    # Restore the other edges
    graph.add_edge(v1, v1_not_on_the_face, color_at_v1)
    graph.add_edge(v2, v2_not_on_the_face, color_at_v2)
    graph.add_edge(v1, v2, get_the_other_colors([color_at_v1, swap_c2])[0])


def remove_vertex_from_face(face, vertex):
    """
    Remove a vertex from a face

    Parameters
    ----------
    face: The face
        vertex: This vertex to remove

    Returns
    -------
        face: The modified face
    """

    # Search the edge that contains the vertex as the second element of the tuple
    # new vA = first element of the edge found
    # Search the edge that contains the vertex as the first element of the tuple
    # new vB = second element of the edge found
    tuple_a = next((v1a, v2a) for v1a, v2a in face if v2a == vertex)
    tuple_b = next((v1b, v2b) for v1b, v2b in face if v1b == vertex)
    new_edge = (tuple_a[0], tuple_b[1])
    face.remove(tuple_a)
    index_for_insert = face.index(tuple_b)
    face.remove(tuple_b)
    face.insert(index_for_insert, new_edge)

    return face


def rotate(l, n):
    """
    Rotate elements (works for lists and tuple)

    Parameters
    ----------
        l: The list to rotate
        n: Index for rotating the list and tuple

    Returns
    -------
        The modified list or tuple
    """

    return l[n:] + l[:n]


def join_faces(f1, f2, edge_to_remove_on_f1):
    """
    join two faces:\n

    f1[:index_of_edge_to_remove_on_f1] + f2[index_of_edge_to_remove_on_f2 + 1:] + f2[:index_of_edge_to_remove_on_f2] + f1[index_of_edge_to_remove_on_f1 + 1:]\n

    f1 = [(6, 1), (1, 2), (2, 7), (7, 6)]\n
    f2 = [(3, 8), (8, 7), (7, 2), (2, 3)]\n
    edge_to_remove_on_f1 = (2, 7))\n
    temp f1_plus_f2 = [(6, 1), (1, 2), (2, 3), (3, 8), (8, 7), (7, 6)]\n
    f1_plus_f2 = [(6, 1), (1, 3), (3, 8), (8, 6)]\n

    f1 = [(2, 7), (7, 6), (6, 1), (1, 2)]\n
    f2 = [(2, 3), (3, 8), (8, 7), (7, 2)]\n
    edge_to_remove_on_f1 = (2, 7))\n
    temp f1_plus_f2 = [(2, 3), (3, 8), (8, 7), (7, 6), (6, 1), (1, 2)]\n
    f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]\n

    f1 = [(1, 2), (2, 7), (7, 6), (6, 1)]\n
    f2 = [(7, 2), (2, 3), (3, 8), (8, 7)]\n
    edge_to_remove_on_f1 = (2, 7))\n
    temp f1_plus_f2 = [(1, 2), (2, 3), (3, 8), (8, 7), (7, 6), (6, 1)]\n
    f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]\n

    f1 = [(1, 2), (2, 3), (3, 1)]\n
    f2 = [(2, 4), (4, 3), (3, 2)]\n
    edge_to_remove_on_f1 = (2, 3))\n
    temp f1_plus_f2 = [(1, 2), (2, 4), (4, 3), (3, 1)]\n
    f1_plus_f2 = [(1, 4), (4, 1)]\n

    f1 = [(2, 1), (1, 2)]\n
    f2 = [(2, 3), (3, 1), (1, 2)]\n
    edge_to_remove_on_f1 = (2, 1))\n
    temp f1_plus_f2 = [(2, 3), (3, 1), (1, 2)]\n
    f1_plus_f2 = [(3, 3)]

    Parameters
    ----------
        f1: First face
        f2: Second face adjacent to the first face
        edge_to_remove_on_f1: The edge to remove

    Returns
    -------
        f1_plus_f2: The new face as the sum of the two
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: join_faces")

    # You can only use this function if at least one face has length > 2
    if len(f1) == 2 and len(f2) == 2:
        logger.error("Unexpected condition (f2 + f2 would generate a single edge face). Mario you'd better go back to paper")
        exit(-1)

    # The edge (v1, v2) on f1 is (v2, v1) on the f2 face
    edge_to_remove_on_f2 = rotate(edge_to_remove_on_f1, 1)
    index_of_edge_to_remove_on_f1 = f1.index(edge_to_remove_on_f1)
    index_of_edge_to_remove_on_f2 = f2.index(edge_to_remove_on_f2)

    # Join the face - After this there will still be vertices to remove
    f1_plus_f2 = f1[:index_of_edge_to_remove_on_f1] + f2[index_of_edge_to_remove_on_f2 + 1:] + f2[:index_of_edge_to_remove_on_f2] + f1[index_of_edge_to_remove_on_f1 + 1:]

    # Debug
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


def is_the_graph_one_edge_connected(face):
    """
    Check if 1-edge-connected.\n
    The face that has been just modified has to be check for becoming one_edge_connected.\n
    face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]\n
    In this example (1, 2) is the edge that make to graph 1-edge-connected.

    Parameters
    ----------
        face: The face that has been just modified has to be check for becoming one_edge_connected

    Returns
    -------
        is_the_graph_one_edge_connected: True of False
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: is_the_graph_one_edge_connected")

    is_the_graph_one_edge_connected = False

    # This is true only for faces != F2
    # NOTE: F2 faces have this representation: [(v1, v2), (v2, v1)] that is correct
    if len(face) != 2:

        # Search the list [(),(),...,()]
        i_edge = 0
        while is_the_graph_one_edge_connected is False and i_edge < len(face):
            reverse_edge = rotate(face[i_edge], 1)

            # Start the search
            if reverse_edge in face[i_edge + 1:]:
                is_the_graph_one_edge_connected = True
            else:

                # Move to the next edge
                i_edge += 1

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_the_graph_one_edge_connected: %s", is_the_graph_one_edge_connected)

    return is_the_graph_one_edge_connected


def get_the_other_colors(colors):
    """
    Get the other colors

    Parameters
    ----------
        colors: A list of colors

    Returns
    -------
        Returns a list of missing colors respect to the given colors
    """

    # return [x for x in ["red", "green", "blue"] if x not in colors]
    return [x for x in VALID_COLORS if x not in colors]


def log_faces(faces):
    """
    Log faces (DEBUG)

    Parameters
    ----------
        faces: The faces of the map
    """

    if logger.isEnabledFor(logging.DEBUG):
        for face in faces:
            logger.debug("Face: %s", face)

    return
