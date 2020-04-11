def f1(i_str, i_num):

    print("In:", i_str, i_num)

    i_concat = i_str + ":" + str(i_num)

    i_str = "Changed in f1"
    i_num = -1

    return i_str, i_num, i_concat


def f2(i_str_ref_of_value, i_num_ref_of_value):

    i_str_ref_of_value = "Changed in f2"
    i_num_ref_of_value = -2

    i_concat = i_str_ref_of_value + ":" + str(i_num_ref_of_value)

    return i_str_ref_of_value, i_num_ref_of_value, i_concat


i_str = "Test"
i_num = 0
i_concat = "Default"

i_str, i_num, i_concat = f1(i_str, i_num)
i_str_2, i_num_2, i_concat_2 = f1(i_str, i_num)

print("Out:", i_str, i_num, i_concat)
