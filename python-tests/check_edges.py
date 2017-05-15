######################################
# Check if two edges are the same edge
# (v1, v2) == (v2, v1)
# (v1, v2, color) == (v1, v2)
# (v1, v2, color) == (v2, v1)
######################################
def check_edges(e1, e2):
    return (e1[0] in e2 and e1[1] in e2)

e1 = (1, 3, 'red')
e2 = (3, 1)

print (e1[0] in e2)

