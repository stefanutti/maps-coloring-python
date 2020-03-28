list_test = [(114, 476, 'blue'), (114, 476, 'red'), (476, 526, 'green')]

edge_test = (114, 476)
color_test = 'red'
print("list_test", list_test)
print("to remove", (edge_test[0], edge_test[1], color_test))


edges_left = [(v1, v2, l) for (v1, v2, l) in list_test if (v1, v2, l) != (edge_test[0], edge_test[1], color_test) and (v2, v1, l) != (edge_test[0], edge_test[1], color_test)]

print(edges_left)
