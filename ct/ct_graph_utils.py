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
import random
import json
from collections import defaultdict, deque
from itertools import permutations

import networkx as nx

logger = logging.getLogger(__name__)

# Valid colors
VALID_COLORS = ['red', 'green', 'blue']


###
# Helper functions to provide Sage-like API on top of NetworkX
###

def is_graph_regular(graph, k):
    """
    Check if graph is k-regular (all vertices have degree k).
    Sage API: graph.is_regular(k)
    """
    return all(d == k for n, d in graph.degree())


def graph_has_loops(graph):
    """
    Check if graph has self-loops.
    Sage API: graph.has_loops()
    """
    return nx.number_of_selfloops(graph) > 0


def graph_edges(graph):
    """
    Return list of edges with labels (color attribute).
    Sage API: graph.edges() returns (u, v, label)
    """
    return [(u, v, data.get('color', None))
            for u, v, key, data in graph.edges(keys=True, data=True)]


def graph_edges_incident(graph, vertex):
    """
    Return edges incident to a vertex.
    Sage API: graph.edges_incident(vertex)
    Returns list of (u, v, label)
    """
    return [(vertex, neighbor, data.get('color', None))
            for neighbor, edges in graph[vertex].items()
            for key, data in edges.items()]


def graph_edges_incident_no_labels(graph, vertex):
    """
    Return edges incident to a vertex without labels.
    Sage API: graph.edges_incident(vertex, labels=False)
    Returns list of (u, v)
    """
    return list(graph.edges(vertex, keys=False, data=False))


def graph_add_edge(graph, u, v, label=None):
    """
    Add an edge with optional label (color).
    Sage API: graph.add_edge(u, v, label)
    """
    graph.add_edge(u, v, color=label)


def graph_delete_edge(graph, u, v, label=None):
    """
    Delete an edge, optionally matching by label.
    Sage API: graph.delete_edge(u, v, label)
    For MultiGraph, we need to find the edge with matching label.
    """
    if label is None:
        # Remove any edge between u and v
        if graph.has_edge(u, v):
            keys = list(graph[u][v].keys())
            if keys:
                graph.remove_edge(u, v, keys[0])
    else:
        # Find and remove the edge with matching label
        if graph.has_edge(u, v):
            for key in list(graph[u][v].keys()):
                if graph[u][v][key].get('color') == label:
                    graph.remove_edge(u, v, key)
                    break


def graph_set_edge_label(graph, u, v, new_label):
    """
    Set the label of an edge.
    Sage API: graph.set_edge_label(u, v, label)
    For MultiGraph, update the first edge found.
    """
    edge_data = graph[u][v]
    first_key = next(iter(edge_data))
    edge_data[first_key]['color'] = new_label


def graph_edge_boundary(graph, v1_list, v2_list):
    """
    Return edges between two sets of vertices.
    Sage API: graph.edge_boundary([v1], [v2])
    """
    result = []
    for u in v1_list:
        for v in v2_list:
            if graph.has_edge(u, v):
                for key in graph[u][v]:
                    label = graph[u][v][key].get('color', None)
                    result.append((u, v, label))
    return result


def graph_random_edge(graph, labels=True):
    """
    Return a random edge from the graph.
    Sage API: graph.random_edge(labels=True)
    """
    if labels:
        edges = list(graph.edges(keys=False, data=True))
        if edges:
            u, v, data = random.choice(edges)
            return (u, v, data.get('color', None))
        return None
    else:
        edges = list(graph.edges(keys=False, data=False))
        if edges:
            return random.choice(edges)
        return None


def graph_edge_iterator(graph, labels=True):
    """
    Return an iterator over edges.
    Sage API: graph.edge_iterator(labels=True)
    """
    if labels:
        return iter(graph_edges(graph))
    else:
        return iter(graph.edges())


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
    if is_graph_regular(graph, 3) is False:
        logger.error("Error: The graph is not 3-regular")
        exit(-1)
    else:
        logger.info("OK. The graph is 3-regular")

    # Check loops
    if graph_has_loops(graph) is True:
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
    if nx.is_planar(graph) is False:
        logger.error("ERROR: The graph is not planar")
        exit(-1)
    else:
        logger.info("OK. The graph is planar")

    # Additional info
    logger.info("The graph has %s vertices and %s edges", graph.number_of_nodes(), graph.number_of_edges())

    return


def kempe_chain_color_swap(graph, starting_edge, c1, c2):
    """
    Execute a Kempe chain color swapping.\n
    Works for chains and cycles and consider also multiedges cases.

    Parameters
    ----------
    graph: The graph\n
    starting_edge: (n, m) the edge where to start the swap
    c1: the color to switch with c2
    c2: the color to switch with c1
    """

    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN: kempe_chain_color_swap: %s, %s, %s", starting_edge, c1, c2)

    # Start the loop at starting_edge
    current_edge = starting_edge
    previous_color = c2
    current_color = c1
    next_color = c2

    # From current edge, I'll search incident edges in one direction (at the beginning in case of cycles any direction is good)
    # This check (degree) is important to recognize the "half cycle color switching" respect tp an "entire cycle color switching"
    # In half cycle color switching, edges at the two ends have been removed and the vertices at the two ends have degree == 2
    direction_fix = 1
    if graph.degree(current_edge[direction_fix]) != 3:
        direction_fix = 0  # Change direction. I was almost falling into the void

    is_the_end_of_switch_process = False
    while is_the_end_of_switch_process is False:

        # From the current edge, I'll search incident edges on the chosen direction [0 or 1]. current_edge[direction] is a vertex
        temp_next_edges_to_check = graph_edges_incident(graph, current_edge[direction_fix])  # Still need to remove current edge

        # I need to filter the edge I was coming from (it may be two edges in case I was walking on a multiedge connection)
        other_direction_fix = 1 - direction_fix
        vertex_i_was_coming_from = current_edge[other_direction_fix]
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in temp_next_edges_to_check if vertex_i_was_coming_from not in (v1, v2)]

        # In case of the previous vertex was a multiedge, the list remains with one element. And the algorith from here won't work. This is a workaround
        # In half chain switches with the last edge being a multiedge, the list can be empty
        if len(edges_to_check) < 2:
            edges_to_check.append((-1, -1, "none"))  # Add a fake edge

        # Check if the next edge is the starting_edge. It would mean that I've looped an entire cycle
        # or Check if I've reached the end of a chain (half loop)
        if (graph.degree(current_edge[direction_fix]) != 3) or are_the_same_edge(starting_edge, edges_to_check[0]) or are_the_same_edge(starting_edge, edges_to_check[1]):
            is_the_end_of_switch_process = True

            # Now: swap color of what now is the previous edge
            if is_multiedge(graph, current_edge[0], current_edge[1]):
                graph_delete_edge(graph, current_edge[0], current_edge[1], current_color)
                graph_add_edge(graph, current_edge[0], current_edge[1], previous_color)
            else:
                graph_set_edge_label(graph, current_edge[0], current_edge[1], previous_color)
        else:

            # Save current edge, color and vertex direction
            previous_edge = current_edge
            previous_color = current_color
            previous_vertex = current_edge[direction_fix]

            # Check the color of the two edges and find the next chain. (-1, -1, "none") will be excluded :-)
            try_next_e1_color = edges_to_check[0][2]
            try_next_e2_color = edges_to_check[1][2]
            if try_next_e1_color == next_color:
                current_edge = edges_to_check[0]
            elif try_next_e2_color == next_color:
                current_edge = edges_to_check[1]
            else:
                logger.error("Unexpected condition (next color must always exists). Mario you'd better go back to paper")
                exit(-1)

            # Update current and next color
            current_color = next_color
            next_color = previous_color

            # Now: swap color of what now is the previous edge
            if is_multiedge(graph, previous_edge[0], previous_edge[1]):
                graph_delete_edge(graph, previous_edge[0], previous_edge[1], previous_color)
                graph_add_edge(graph, previous_edge[0], previous_edge[1], current_color)
            else:
                graph_set_edge_label(graph, previous_edge[0], previous_edge[1], current_color)

            # Update direction. This was tricky since tuples for multiple edges do not list vertices in order:
            # REAL: (1, 2, "red") and (1, 2, "green")
            # INSTEAD OF: (1, 2, "red") and (2, 1, "green")
            if current_edge[direction_fix] == previous_vertex:
                direction_fix = 1 - direction_fix

    return


def faces_by_vertices(graph):
    """
    Return a face as a list of ordered vertices. Used to create random graphs.\n
    Originally taken from Sage (http://trac.sagemath.org/ticket/6236).
    Adapted for NetworkX planar embedding.

    Parameters
    ----------
        graph: The graph (must have planar embedding set via check_planarity)

    Returns
    -------
        list_faces: Returns a face as a list of ordered vertices
    """
    # Get the planar embedding from NetworkX
    is_planar, embedding = nx.check_planarity(graph)
    if not is_planar:
        raise ValueError("Graph is not planar")
    
    # Use NetworkX's built-in method to get all faces
    # traverse_face returns the nodes of a face starting from a half-edge
    visited_edges = set()
    list_faces = []
    
    for u in embedding:
        for v in embedding.neighbors_cw_order(u):
            half_edge = (u, v)
            if half_edge not in visited_edges:
                # Get the face containing this half-edge
                face = []
                start_u, start_v = u, v
                curr_u, curr_v = u, v
                
                while True:
                    face.append(curr_u)
                    visited_edges.add((curr_u, curr_v))
                    # Get next half-edge in the face
                    next_half_edge = embedding.next_face_half_edge(curr_u, curr_v)
                    curr_u, curr_v = next_half_edge
                    if curr_u == start_u and curr_v == start_v:
                        break
                
                list_faces.append(face)

    return list_faces


def graph_dual_old(g):
    """
    Legacy O(F^2) implementation of graph_dual. Kept for reference/regression tests.
    Return the dual of a graph. Used to create random graphs.\n
    Originally taken from Sage (http://trac.sagemath.org/ticket/6236).
    Adapted for NetworkX.

    Parameters
    ----------
        g: The graph

    Returns
    -------
        dual: The dual of a graph
    """

    f = [tuple(face) for face in faces_by_vertices(g)]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]

    # Create dual graph using NetworkX
    dual = nx.MultiGraph()
    for i, f1 in enumerate(f_edges):
        for j, f2 in enumerate(f_edges):
            if i < j:
                # Check if f1 and f2 share an edge (reversed)
                f1_set = set(f1)
                f2_reversed = set((e[1], e[0]) for e in f2)
                if f1_set.intersection(f2_reversed):
                    dual.add_edge(f[i], f[j])

    return dual


def graph_dual(g):
    """
    Return the dual of a graph. Used to create random graphs.\n
    Originally taken from Sage (http://trac.sagemath.org/ticket/6236).
    Adapted for NetworkX.

    Optimized O(E) implementation: index each undirected primal edge to the
    faces that contain it, then derive adjacent face pairs in one pass.
    Preserves the original behavior (one dual edge per adjacent face pair,
    even when multiple primal edges are shared between them).

    Parameters
    ----------
        g: The graph

    Returns
    -------
        dual: The dual of a graph
    """

    faces = [tuple(face) for face in faces_by_vertices(g)]

    # Index each undirected primal edge to the set of face indices containing it.
    edge_to_faces = {}
    for i, face in enumerate(faces):
        n = len(face)
        for k in range(n):
            key = frozenset((face[k], face[(k + 1) % n]))
            bucket = edge_to_faces.get(key)
            if bucket is None:
                edge_to_faces[key] = {i}
            else:
                bucket.add(i)

    # Build the deduplicated set of adjacent face pairs.
    pairs = set()
    for face_indices in edge_to_faces.values():
        if len(face_indices) < 2:
            continue
        indices = sorted(face_indices)
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                pairs.add((indices[a], indices[b]))

    dual = nx.MultiGraph()
    for i, j in pairs:
        dual.add_edge(faces[i], faces[j])

    return dual


def print_graph(graph):
    """
    Print graph.

    Parameters
    ----------
        graph: The graph to print
    """
    if logger.isEnabledFor(logging.DEBUG):
        for vertex in iter(graph.nodes()):
            edges = graph_edges_incident(graph, vertex)
            logger.debug("vertex: %s, edges: %s, is well colored: %s, len(edges): %s", vertex, edges, are_incident_edges_well_colored(graph, vertex), len(edges))

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

    for vertex in graph.nodes():
        colors = set()
        adj = graph[vertex]
        degree = 0
        for neighbor, edges in adj.items():
            for key, data in edges.items():
                colors.add(data.get('color', None))
                degree += 1
        if degree != 3 or len(colors) != 3:
            if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_well_colored (False)")
            return False

    if logger.isEnabledFor(logging.DEBUG): logger.debug("END: is_well_colored (True)")

    return True


def are_incident_edges_well_colored(graph, vertex):
    """
    Check if the incident edges to a give vertex are well colored.

    Parameters
    ----------
        graph: The graph to check
        vertex: The vertex to check

    Returns
    -------
        are_incident_edges_well_colored_tmp: True or False if all edges of the given vertex are well colored
    """

    are_incident_edges_well_colored_tmp = False

    # I use a dictionaty of colors to see if each vertes has three colors = three keys (= 1 is just a dummy value)
    edges = graph_edges_incident(graph, vertex)
    test_three_elements_in_the_color_dictionary = {}
    test_three_elements_in_the_color_dictionary[edges[0][2]] = 1
    test_three_elements_in_the_color_dictionary[edges[1][2]] = 1
    test_three_elements_in_the_color_dictionary[edges[2][2]] = 1

    if len(test_three_elements_in_the_color_dictionary.keys()) == 3:
        are_incident_edges_well_colored_tmp = True

    return are_incident_edges_well_colored_tmp


def get_edge_color(graph, edge):
    """
    Get the color of an edge.\n
    In case of multiedge it will return the color of one of the two edges.\n
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

    # Direct O(1) dictionary lookup instead of scanning all edges
    edge_data = graph[v1][v2]
    first_key = next(iter(edge_data))
    color_to_return = edge_data[first_key].get('color', None)

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

    if not graph.has_edge(v1, v2):
        return False
    return len(graph[v1][v2]) > 1


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

    new_graph = nx.MultiGraph()
    for edge_to_add in flattened_egdes:
        new_graph.add_edge(edge_to_add[0], edge_to_add[1])

    return new_graph


def color_planar_representation(graph, faces):
    """Annotate the original ordered face boundaries without mutating them.

    The pair format has no keys for parallel edges. Assign their distinct
    colors to both directions, keeping consecutive face edges distinct.
    In a loop-free cubic graph there are at most three parallel edges, so
    checking their reverse assignments takes at most six permutations.
    """
    if not is_well_colored(graph) or graph_has_loops(graph):
        raise ValueError("Colored planar export requires a properly colored loop-free cubic graph")
    colored_faces = [[[u, v, None] for u, v in face] for face in faces]
    positions = defaultdict(list)
    for face in colored_faces:
        for i, (u, v, _) in enumerate(face):
            positions[(u, v)].append((face, i))

    for u, neighbors in graph.adjacency():
        for v, edges in neighbors.items():
            if u < v:
                forward = positions.pop((u, v), [])
                backward = positions.pop((v, u), [])
                colors = [data['color'] for data in edges.values()]
                if len(forward) != len(colors) or len(backward) != len(colors):
                    raise ValueError(f"Graph and planar embedding disagree on edge {(u, v)}")
                if any(color not in VALID_COLORS for color in colors):
                    raise ValueError(f"Invalid colors on edge {(u, v)}: {colors}")
                for (face, i), color in zip(forward, colors):
                    face[i][2] = color
                for reverse_colors in permutations(colors):
                    for (face, i), color in zip(backward, reverse_colors):
                        face[i][2] = color
                    if all(face[i][2] != face[i - 1][2]
                           and face[i][2] != face[(i + 1) % len(face)][2]
                           for face, i in forward + backward):
                        break
                else:
                    raise ValueError(f"Cannot match parallel edge colors to planar embedding at {(u, v)}")
    if positions:
        raise ValueError("Planar embedding contains edges missing from the colored graph")
    return colored_faces


def export_graph(graph_to_export, name_of_file_without_extension, *, planar_faces=None):
    """
    Export graph

    Parameters
    ----------
        graph_to_export: The graph to export
        name_of_file_without_extension: The name that will be used to export the graph
        planar_faces: Optional original embedding; also export colored triples in its original order
    """

    colored_faces = None
    if planar_faces is not None:
        colored_faces = color_planar_representation(graph_to_export, planar_faces)

    # Save: edgelist, dot
    #
    # Other possibilities: adjlist, gexf, gml, graphml, multiline_adjlist, pajek, yaml
    #
    # Additional note (17/Oct/2016): I decided to save the graph also as a .dot file
    # The problem with dot file is that you can write .dot files directly, but you cannot read them back if you don't install an additional package
    logger.info("-----------------------------")
    logger.info("BEGIN: Save the 4 colored map")
    logger.info("-----------------------------")
    
    # Export as edgelist using NetworkX
    nx.write_edgelist(graph_to_export, name_of_file_without_extension + ".edgelist")
    
    # Export as DOT file (custom implementation)
    with open(name_of_file_without_extension + ".orig.dot", 'w') as f:
        f.write("graph {\n")
        for u, v, key, data in graph_to_export.edges(keys=True, data=True):
            label = data.get('color', '')
            if label:
                f.write(f'    {u} -- {v} [label="{label}"];\n')
            else:
                f.write(f'    {u} -- {v};\n')
        f.write("}\n")
    
    logger.info("File saved: %s", name_of_file_without_extension)

    # Replace label with color. Just to be used from Gephy
    filedata = None
    with open(name_of_file_without_extension + ".orig.dot", 'r') as file:
        filedata = file.read()

    filedata = filedata.replace('label', 'color')

    with open(name_of_file_without_extension + ".dot", 'w') as file:
        file.write(filedata)

    if colored_faces is not None:
        with open(name_of_file_without_extension + ".colored.planar", 'w') as file:
            json.dump(colored_faces, file)
            file.write("\n")

    logger.info("---------------------------")
    logger.info("END: Save the 4 colored map")
    logger.info("---------------------------")

    return


def append_colored_planar_representation(graph, output_filename, planar_faces):
    """Append one colored planar embedding as a JSON Lines record."""
    colored_faces = color_planar_representation(graph, planar_faces)
    with open(output_filename, 'a') as file:
        json.dump(colored_faces, file)
        file.write("\n")


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
    # (v1, v2) If I search all incident edges to v2 I'll have (v2, vx) and (v2, vy). Next vertex to choose will be vx or vy ... depending on the next chain color
    direction = 1
    is_the_end_of_search_process = False
    while is_the_end_of_search_process is False:

        # Debug
        if logger.isEnabledFor(logging.DEBUG): logger.debug("Loop: current_edge: %s, current_color: %s, next_color: %s", current_edge, current_color, next_color)

        # From current edge, I'll search incident edges in one direction [0 or 1] - current_edge[direction] is a vertex
        temp_next_edges_to_check = graph_edges_incident(graph, current_edge[direction])  # Still need to remove current edge
        if logger.isEnabledFor(logging.DEBUG): logger.debug("temp_next_edges_to_check: %s", temp_next_edges_to_check)
        edges_to_check = [(v1, v2, l) for (v1, v2, l) in temp_next_edges_to_check if (v1, v2, l) != (current_edge[0], current_edge[1], current_color) and (v2, v1, l) != (current_edge[0], current_edge[1], current_color)]
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


class KempeSearchExhausted(RuntimeError):
    """Kempe repair exhausted its budget or class; this does not mean uncolorable."""


def find_kempe_repair(graph, first_edge, second_edge, max_states):
    """Search full labelled colorings for v17 section 8.2's CONDITION-1.

    Return (switches, endpoint_colors, working_pair, states_examined).
    Each switch is (color1, color2, keyed_cycle_edges), so parallel edges
    remain distinct. Search interleaves endpoint-cycle and remote-cycle
    expansions deterministically; it is not a shortest-path search and
    never mutates graph. A boundary word alone is NOT a search state.
    Exhausting the class and reaching the budget are distinct diagnostics;
    neither proves that another reduction/coloring class cannot work.
    """
    if max_states < 1:
        raise ValueError("Kempe search budget must be positive")
    if not is_graph_regular(graph, 3) or not is_well_colored(graph):
        raise ValueError("Kempe search requires a properly colored cubic graph")
    edges = sorted((min(u, v), max(u, v), key) for u, v, key in graph.edges(keys=True))
    incidence = {vertex: [] for vertex in graph}
    for i, (u, v, _) in enumerate(edges):
        incidence[u].append(i)
        incidence[v].append(i)
    first = {i for i, (u, v, _) in enumerate(edges) if (u, v) == tuple(sorted(first_edge))}
    second = {i for i, (u, v, _) in enumerate(edges) if (u, v) == tuple(sorted(second_edge))}
    if not first or not second or first & second:
        raise ValueError("Kempe repair requires two distinct existing edge positions")
    initial = bytes(VALID_COLORS.index(graph[u][v][key]['color']) for u, v, key in edges)
    distance = dict.fromkeys(first_edge + second_edge, 0)
    pending_vertices = deque(distance)
    while pending_vertices:
        vertex = pending_vertices.popleft()
        for neighbor in graph[vertex]:
            if neighbor not in distance:
                distance[neighbor] = distance[vertex] + 1
                pending_vertices.append(neighbor)
    edge_distance = [min(distance.get(u, len(graph)), distance.get(v, len(graph)))
                     for u, v, _ in edges]
    # The parent map doubles as an exact visited set, retaining full colors.
    parents = {initial: None}
    queue = deque([initial])
    remote_queue = deque()
    examined = 0
    budget_reached = False
    local_expansions = 0
    while queue or remote_queue:
        # A bounded local burst prevents a large endpoint orbit from starving
        # remote switches (v17 section 9.18). This is a scheduling heuristic.
        expand_remote = bool(remote_queue) and (not queue or local_expansions >= 8)
        if expand_remote:
            state = remote_queue.popleft()
            local_expansions = 0
        else:
            state = queue.popleft()
            remote_queue.append(state)
            examined += 1
            local_expansions += 1
        moves = []
        for c1, c2 in ((0, 1), (0, 2), (1, 2)):
            unseen = {i for i, color in enumerate(state) if color in (c1, c2)}
            # Use increasing edge index, not set iteration, for stable ties.
            for seed in range(len(edges)):
                if seed in unseen:
                    component = []
                    pending = [seed]
                    unseen.remove(seed)
                    while pending:
                        current = pending.pop()
                        component.append(current)
                        for vertex in edges[current][:2]:
                            for neighbor in incidence[vertex]:
                                if neighbor in unseen:
                                    unseen.remove(neighbor)
                                    pending.append(neighbor)
                    component.sort()
                    start = next((i for i in component if i in first), None)
                    end = next((i for i in component if i in second), None)
                    if start is not None and end is not None:
                        switches = []
                        cursor = state
                        while parents[cursor] is not None:
                            previous, a, b, cycle = parents[cursor]
                            switches.append((VALID_COLORS[a], VALID_COLORS[b],
                                             tuple(edges[i] for i in cycle)))
                            cursor = previous
                        switches.reverse()
                        colors = (VALID_COLORS[state[start]], VALID_COLORS[state[end]])
                        other = c2 if state[start] == c1 else c1
                        return switches, colors, (colors[0], VALID_COLORS[other]), examined
                    moves.append((not (start is not None or end is not None), c1, c2, component))
        if expand_remote:
            moves.sort(key=lambda move: (min(edge_distance[i] for i in move[3]), -len(move[3])))
        discovered = []
        for is_remote, c1, c2, component in moves:
            if is_remote != expand_remote:
                continue
            successor = bytearray(state)
            for i in component:
                successor[i] = c2 if state[i] == c1 else c1
            successor = bytes(successor)
            if successor not in parents:
                if len(parents) < max_states:
                    parents[successor] = (state, c1, c2, tuple(component))
                    discovered.append(successor)
                else:
                    budget_reached = True
        if expand_remote:
            queue.extendleft(reversed(discovered))
        else:
            queue.extend(discovered)
    if budget_reached:
        raise KempeSearchExhausted(
            f"Kempe search budget reached ({max_states} states); "
            f"split edges {first_edge}, {second_edge}. "
            "Increase --kempe-search-limit or try a different reduction.")
    raise KempeSearchExhausted(
        f"Kempe class exhausted ({examined} states) for split edges "
        f"{first_edge}, {second_edge}; a different reduction or coloring class is needed")


def apply_half_kempe_loop_color_switching(graph, ariadne_step, color_at_v1, color_at_v2, swap_c1, swap_c2):
    """
    Apply half Kempe loop color switching

    Parameters
    ----------
        graph: The graph
        ariadne_step: This step
        color_at_v1: Color at v1
        color_at_v2: Color at v1
        swap_c1: First color
        swap_c2: Second color
    """

    v1 = ariadne_step[1]
    v2 = ariadne_step[2]
    v1_on_the_face = ariadne_step[3]
    v2_on_the_face = ariadne_step[4]
    v1_not_on_the_face = ariadne_step[5]
    v2_not_on_the_face = ariadne_step[6]

    # I broke the cycle to apply the half Kempe chain color swapping
    # Removed from delete_edge the form with the (): delete_edge((vi, v2, color))
    graph_delete_edge(graph, v1_on_the_face, v1_not_on_the_face, color_at_v1)
    graph_delete_edge(graph, v2_on_the_face, v2_not_on_the_face, color_at_v2)
    graph_add_edge(graph, v1, v1_on_the_face, color_at_v1)
    graph_add_edge(graph, v2, v2_on_the_face, color_at_v2)

    # Half Kempe chain color swapping
    kempe_chain_color_swap(graph, (v1, v1_on_the_face), swap_c1, swap_c2)

    # Restore the other edges
    graph_add_edge(graph, v1, v1_not_on_the_face, color_at_v1)
    graph_add_edge(graph, v2, v2_not_on_the_face, color_at_v2)
    graph_add_edge(graph, v1, v2, get_the_other_colors([color_at_v1, swap_c2])[0])


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

    f1 = [(6, 1), (1, 2), (2, 7), (7, 6)]
    f2 = [(3, 8), (8, 7), (7, 2), (2, 3)]
    edge_to_remove_on_f1 = (2, 7))
    temp f1_plus_f2 = [(6, 1), (1, 2), (2, 3), (3, 8), (8, 7), (7, 6)]
    f1_plus_f2 = [(6, 1), (1, 3), (3, 8), (8, 6)]

    f1 = [(2, 7), (7, 6), (6, 1), (1, 2)]
    f2 = [(2, 3), (3, 8), (8, 7), (7, 2)]
    edge_to_remove_on_f1 = (2, 7))
    temp f1_plus_f2 = [(2, 3), (3, 8), (8, 7), (7, 6), (6, 1), (1, 2)]
    f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]

    f1 = [(1, 2), (2, 7), (7, 6), (6, 1)]
    f2 = [(7, 2), (2, 3), (3, 8), (8, 7)]
    edge_to_remove_on_f1 = (2, 7))
    temp f1_plus_f2 = [(1, 2), (2, 3), (3, 8), (8, 7), (7, 6), (6, 1)]
    f1_plus_f2 = [(1, 3), (3, 8), (8, 6), (6, 1)]

    f1 = [(1, 2), (2, 3), (3, 1)]
    f2 = [(2, 4), (4, 3), (3, 2)]
    edge_to_remove_on_f1 = (2, 3))
    temp f1_plus_f2 = [(1, 2), (2, 4), (4, 3), (3, 1)]
    f1_plus_f2 = [(1, 4), (4, 1)]

    f1 = [(2, 1), (1, 2)]
    f2 = [(2, 3), (3, 1), (1, 2)]
    edge_to_remove_on_f1 = (2, 1))
    temp f1_plus_f2 = [(2, 3), (3, 1), (1, 2)]
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

        # Same reverse-edge test in O(boundary length), including repeated
        # directed edges. Large Waterworld oceans made the list scan quadratic.
        seen = set()
        for u, v in face:
            if (v, u) in seen:
                is_the_graph_one_edge_connected = True
                break
            seen.add((u, v))

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

    return [x for x in VALID_COLORS if x not in colors]


def log_faces(g_faces):
    """
    Log faces (DEBUG)

    Parameters
    ----------
        faces: The faces of the map to print for debugging
    """

    if logger.isEnabledFor(logging.DEBUG):
        for face in g_faces:
            logger.debug("Face: %s", face)

    return


def log_faces_info(g_faces):
    """
    Log faces (DEBUG)

    Parameters
    ----------
        faces: The faces of the map to print for debugging
    """

    for face in g_faces:
        logger.info("Face: %s", face)

    return
