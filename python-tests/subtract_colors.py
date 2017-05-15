######################
# Get the other colors
######################
def get_the_other_colors(colors):
    return [x for x in ["red", "green", "blu"] if x not in colors]

print (get_the_other_colors(["red", "blu"]))
print (get_the_other_colors(["blu"]))
print (get_the_other_colors(["red", "green", "blu"]))
print (get_the_other_colors(["red", "green", "blu", "a"]))
