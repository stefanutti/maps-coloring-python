############################
# Check if vertex is in face
############################


def check_if_vertex_is_in_face(face, vertex):
    return any([edge for edge in face if edge[0] == vertex or edge[1] == vertex])


face_to_search = [(6, 1), (1, 3), (3, 8), (8, 6)]
print(check_if_vertex_is_in_face(face_to_search, 1))
print(check_if_vertex_is_in_face(face_to_search, 10))
print(check_if_vertex_is_in_face(face_to_search, 4))
print(check_if_vertex_is_in_face(face_to_search, 3))
print(check_if_vertex_is_in_face(face_to_search, 6))
print(check_if_vertex_is_in_face(face_to_search, 5))
