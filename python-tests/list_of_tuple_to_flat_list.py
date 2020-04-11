list_of_tuple = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6)]

flat_list = [element for face in list_of_tuple for element in face]
# flat_list = sorted(set(flat_list))

print("flat_list =", flat_list)
