#############################
# Remove a vertex from a face
#############################
def remove_vertex_from_face(face, vertex):

    # The new face to return
    #
    new_face = face.copy()

    # Search the edge that contains the vertex as the second element of the tuple
    # new vA = first element of the edge found
    # Search the edge that contains the vertex as the first element of the tuple
    # new vB = second element of the edge found
    #
    tuple_a = next((v1a, v2a) for v1a, v2a in new_face if v2a == vertex)
    tuple_b = next((v1b, v2b) for v1b, v2b in new_face if v1b == vertex)
    new_edge = (tuple_a[0], tuple_b[1])
    new_face.remove(tuple_a)
    index_for_insert = new_face.index(tuple_b)
    new_face.remove(tuple_b)
    new_face.insert(index_for_insert, new_edge)

    return new_face

vertex = 6
face = [(6, 1), (1, 3), (3, 8), (8, 6)]
new_face = remove_vertex_from_face(face, vertex)
print ("face:", face, "vertex:", vertex, "new_face:", new_face)

vertex = 3
face = [(6, 1), (1, 3), (3, 8), (8, 6)]
new_face = remove_vertex_from_face(face, vertex)
print ("face:", face, "vertex:", vertex, "new_face:", new_face)

vertex = 1
face = [(6, 1), (1, 3), (3, 8), (8, 6)]
new_face = remove_vertex_from_face(face, vertex)
print ("face:", face, "vertex:", vertex, "new_face:", new_face)

vertex = 8
face = [(6, 1), (1, 3), (3, 8), (8, 6)]
new_face = remove_vertex_from_face(face, vertex)
print ("face:", face, "vertex:", vertex, "new_face:", new_face)