# First step: with or without multiedge
# Vertex = 2
previous_vertex = 1

lot_normal = [(1, 2, 'red'), (2, 3, 'green'), (2, 4, 'blu')]
lot_multiedge = [(1, 2, 'red'), (2, 3, 'green'), (2, 3, 'blu')]

f_lot_normal = [(v1, v2, l) for (v1, v2, l) in lot_normal if previous_vertex not in (v1, v2)]
f_lot_multiedge = [(v1, v2, l) for (v1, v2, l) in lot_multiedge if previous_vertex not in (v1, v2)]

print(lot_normal)
print(lot_multiedge)
print(f_lot_normal)
print(f_lot_multiedge)

# Next step (previous was a multiedge)
# Vertex = 3
previous_vertex = 2
lot_multiedge = [(2, 3, 'green'), (2, 3, 'blu'), (3, 4, "red")]

f_lot_multiedge = [(v1, v2, l) for (v1, v2, l) in lot_multiedge if previous_vertex not in (v1, v2)]

print(lot_multiedge)
print(f_lot_multiedge)
