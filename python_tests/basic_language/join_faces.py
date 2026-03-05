import logging.handlers
import sys

# Set logging facilities
#
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)


def join_faces(f1, f2, edge_to_remove_on_f1):

    # You can only use this function if at least one face has length > 2
    #
    if len(f1) == 2 and len(f2) == 2:
        raise Exception('Cannot join g_faces both of len 2 - It would generate a single edge face, with no vertices')

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
    list_of_just_one_tuple_a = [(v1a, v2a) for v1a, v2a in f1_plus_f2 if v2a == edge_to_remove_on_f1[0]]
    list_of_just_one_tuple_b = [(v1b, v2b) for v1b, v2b in f1_plus_f2 if v1b == edge_to_remove_on_f1[0]]
    tuple_a = list_of_just_one_tuple_a[0]
    tuple_b = list_of_just_one_tuple_b[0]
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
    list_of_just_one_tuple_a = [(v1a, v2a) for v1a, v2a in f1_plus_f2 if v2a == edge_to_remove_on_f1[1]]
    list_of_just_one_tuple_b = [(v1b, v2b) for v1b, v2b in f1_plus_f2 if v1b == edge_to_remove_on_f1[1]]
    tuple_a = list_of_just_one_tuple_a[0]
    tuple_b = list_of_just_one_tuple_b[0]
    new_edge = (tuple_a[0], tuple_b[1])
    f1_plus_f2.remove(tuple_a)
    index_for_insert = f1_plus_f2.index(tuple_b)
    f1_plus_f2.remove(tuple_b)
    f1_plus_f2.insert(index_for_insert, new_edge)

    logger.info("f1_plus_f2 = %s", f1_plus_f2)

    return f1_plus_f2


def join_faces2(f1, f2, edge_to_remove_on_f1):
    # You can only use this function if at least one face has length > 2
    #
    if len(f1) == 2 and len(f2) == 2:
        raise Exception('Cannot join g_faces both of len 2 - It would generate a single edge face, with no vertices')

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

    logger.info("f1_plus_f2 = %s", f1_plus_f2)

    return f1_plus_f2


def rotate(l, n):
    return l[n:] + l[:n]


f1 = [(55, 20), (20, 55)]
f2 = [(20, 55), (55, 6), (6, 4), (4, 3), (3, 18), (18, 20)]
f1PlusF2 = join_faces(f1, f2, (55, 20))
print("---")

f1 = [(2, 1), (1, 3), (3, 4), (4, 2)]
f2 = [(3, 4), (4, 3)]
f1PlusF2 = join_faces(f1, f2, (3, 4))
f1PlusF2 = join_faces2(f1, f2, (3, 4))
print("---")

f1 = [(6, 1), (1, 2), (2, 7), (7, 6)]
f2 = [(3, 8), (8, 7), (7, 2), (2, 3)]
f1PlusF2 = join_faces(f1, f2, (2, 7))
f1PlusF2 = join_faces2(f1, f2, (2, 7))
print("---")

f1 = [(2, 7), (7, 6), (6, 1), (1, 2)]
f2 = [(2, 3), (3, 8), (8, 7), (7, 2)]
f1PlusF2 = join_faces(f1, f2, (2, 7))
f1PlusF2 = join_faces2(f1, f2, (2, 7))
print("---")

f1 = [(1, 2), (2, 7), (7, 6), (6, 1)]
f2 = [(7, 2), (2, 3), (3, 8), (8, 7)]
f1PlusF2 = join_faces(f1, f2, (2, 7))
f1PlusF2 = join_faces2(f1, f2, (2, 7))
print("---")

f1 = [(1, 2), (2, 3), (3, 1)]
f2 = [(2, 4), (4, 3), (3, 2)]
f1PlusF2 = join_faces(f1, f2, (2, 3))
f1PlusF2 = join_faces2(f1, f2, (2, 3))
print("---")

f1 = [(2, 1), (1, 2)]
f2 = [(2, 3), (3, 1), (1, 2)]
f1PlusF2 = join_faces(f1, f2, (2, 1))
f1PlusF2 = join_faces2(f1, f2, (2, 1))
print("---")

f1 = [(2, 1), (1, 2)]
f2 = [(4, 5), (5, 3), (3, 1), (1, 2), (2, 4)]
f1PlusF2 = join_faces(f1, f2, (2, 1))
f1PlusF2 = join_faces2(f1, f2, (2, 1))
print("---")

f1 = [(2, 1), (1, 2)]
f2 = [(4, 5), (5, 3), (3, 1), (1, 2), (2, 4)]
f1PlusF2 = join_faces(f1, f2, (2, 1))
f1PlusF2 = join_faces2(f1, f2, (2, 1))
print("---")
