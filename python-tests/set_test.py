def f1(seq):
   for e in seq:
       reverse = (e[1], e[0])
       if reverse in seq:
           seq.remove(reverse)
   return seq

g_faces = [[(0, 1), (1, 0), (30, 23)], [(28, 26), (26, 32), (23, 30)]]
print("A: ", g_faces)

flattened_egdes = [edge for face in g_faces for edge in face]
print("B: ", flattened_egdes)

new_flattened_egdes = f1(flattened_egdes)
print("C: ", new_flattened_egdes)