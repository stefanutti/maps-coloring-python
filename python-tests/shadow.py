
def print_data1(data): # <-- Pass in a parameter called "data"
    print (data)  # <-- Note: You can access global variable inside your function, BUT for now, which is which? the parameter or the global variable? Confused, huh?
    data = [111]
    print (data)  # <-- Note: You can access global variable inside your function, BUT for now, which is which? the parameter or the global variable? Confused, huh?

def print_data2():
    data = [3]
    print (data)

data = [4, 5, 6] # your global variable
print("---")
print_data2()
print("---")
print_data1(data)
print("---")

