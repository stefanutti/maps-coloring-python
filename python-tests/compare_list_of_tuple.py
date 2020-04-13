# Python3 code to demonstrate working of
# Check if two list of tuples are identical
# using == operator

# initialize list of tuples
test_list1 = [(10, 4), (2, 5)]
test_list2 = [(10, 4), (2, 5)]
test_list3 = [(2, 5), (10, 4)]

# printing original tuples lists
print("The original list 1:", test_list1)
print("The original list 2:", test_list2)
print("The original list 3:", test_list3)

# printing result
print("Are tuple lists test_list1 == test_list2 identical?:", test_list1 == test_list2)
print("Are tuple lists test_list1 == test_list3 identical?:", test_list1 == test_list3)
