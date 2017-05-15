#!/usr/bin/env sage

import time

def rotate (l, n):
    return l[n:] + l[:n]

# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#
def checkIfOneEdgeConnected (face):

    # Return variable
    #
    isOneEdgeConnectedGraph = False

    # Search the list [(),(),...,()]
    #
    iEdge = 0
    while isOneEdgeConnectedGraph == False and iEdge < len(face):
        reverseEdge = rotate(face[iEdge], 1)

        # Start the search
        #
        if reverseEdge in face[iEdge + 1:]:
            isOneEdgeConnectedGraph = True
        else:

            # Move to the next edge
            #
            iEdge = iEdge + 1

    # Return
    #
    return isOneEdgeConnectedGraph

def checkIfOneEdgeConnectedNew (face):
    isOneEdgeConnected = False
    edgeFound = [edge for i, edge in enumerate(face) if rotate(edge, 1) in face[i:]]
    if len(edgeFound) > 0:
        isOneEdgeConnected = True
    return isOneEdgeConnected

def checkIfOneEdgeConnectedNew2 (face):
    isOneEdgeConnected = False
    edgeFound = next((edge for i, edge in enumerate(face) if rotate(edge, 1) in face[i:]),(-1,-1))
    if (edgeFound == (-1, -1)):
        isOneEdgeConnected = True

    return isOneEdgeConnected

def checkIfOneEdgeConnectedNew3 (face):
    isOneEdgeConnected = False

    iEdge = 0
    dictOfEdges = {}
    while isOneEdgeConnected == False and iEdge < len(face):
        edge = face[iEdge]
        reverseEdge = rotate(edge, 1)

        value = dictOfEdges.get(reverseEdge)
        if value == None:
            dictOfEdges[edge] = 1
            dictOfEdges[reverseEdge] = 1
        else:
            isOneEdgeConnected = True

        iEdge += 1

    return isOneEdgeConnected

def checkIfOneEdgeConnectedNew4 (face):
    isOneEdgeConnected = False

    iEdge = 0
    listOfEdges = []
    while isOneEdgeConnected == False and iEdge < len(face):
        edge = face[iEdge]
        reverseEdge = rotate(edge, 1)

        if reverseEdge not in listOfEdges:
            listOfEdges.append(edge)
            listOfEdges.append(reverseEdge)
        else:
            isOneEdgeConnected = True

        iEdge += 1

    return isOneEdgeConnected

print ("--- checkIfOneEdgeConnected")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnected (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnected")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnected (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew2")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew2 (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew2")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew2 (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew3")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew3 (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew3")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew3 (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew4")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew4 (f1)
end = time.time()
print(end - start)

print("--- checkIfOneEdgeConnectedNew4")
start = time.time()
for i in range(500000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew4 (f1)
end = time.time()
print(end - start)
