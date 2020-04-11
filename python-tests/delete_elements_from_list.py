def rotate(l, n):
    return l[n:] + l[:n]


my_list = [(1, 2), (3, 5), (6, 8), (2, 7)]
my_list.sort(key=len)
print("aaa = ", my_list)

test = (5, 3)
if test in my_list:
    my_list.remove(test)
else:
    my_list.remove(rotate(test, 1))

my_list.sort(key=len)
print("aaa = ", my_list)

my_list.append((0, 1))
my_list.sort(key=len)
print("aaa = ", my_list)

tmp_colors = ["red", "green", "blu"]
tmp_colors.remove("green")
tmp_colors.remove("blu")
left_color = tmp_colors[0]
print("tmp_colors = ", tmp_colors)
print("left_color = ", left_color)
