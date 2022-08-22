#!/usr/bin/python

def main(x, y):
    v, w = -1, -1
    global a
    a = 10
    print('main: ', str(a), str(x), str(y))
    x = 5
    print('main: ', str(a), str(x), str(y))
    y = 5
    print('main: ', str(a), str(x), str(y))
    print('main: ', str(a), str(v), str(w))
    g(x, y)


def g(x, y):
    print('g: ', str(a), str(x), str(y))
    x = 7
    print('g: ', str(a), str(x), str(y))
    y = 7
    print('g: ', str(a), str(x), str(y))
    # print('g: ', str(a), str(v), str(w))


if __name__ == '__main__':

    a = 2
    main(3, a)
    print('global: ', str(a))
    print('global: ', str(a), str(x), str(y))
