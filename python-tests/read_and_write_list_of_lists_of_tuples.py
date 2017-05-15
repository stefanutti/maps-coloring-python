import json

g_faces = [[(3,2), (3,5)],[(2,4), (1,3), (1,3)],[(1,2), (3,4), (6,7)]]

for i in range(len(g_faces)):
	print ("gface: ", g_faces[i])

json.dump(g_faces, open('test.json', 'w'))

g_faces = json.load(open('test.json'))

# cast back to tuples
g_faces = [[tuple(l) for l in L] for L in g_faces]

for i in range(len(g_faces)):
	print ("gface: ", g_faces[i])
