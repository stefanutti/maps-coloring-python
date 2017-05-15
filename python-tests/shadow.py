def print_data(data): # <-- Pass in a parameter called "data"
    data = [111]
    prova = 5
    print (data)  # <-- Note: You can access global variable inside your function, BUT for now, which is which? the parameter or the global variable? Confused, huh?

data = [4, 5, 6] #your global variable
print(data)
print_data(data)
print(data)  # <-- Note: You can access global variable inside your function, BUT for now, which is which? the parameter or the global variable? Confused, huh?
print(prova)  # <-- Note: You can access global variable inside your function, BUT for now, which is which? the parameter or the global variable? Confused, huh?

