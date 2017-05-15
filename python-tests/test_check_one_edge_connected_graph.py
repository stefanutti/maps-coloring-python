#!/usr/bin/env sage

import time
import sys

def rotate (l, n):
    return l[n:] + l[:n]

# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#
def checkIfOneEdgeConnected (face):

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    isOneEdgeConnectedGraph = False

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    iEdge = 0
    while isOneEdgeConnectedGraph == False and iEdge < len(face):
        reverseEdge = rotate (face[iEdge], 1)

        # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
        #
        if reverseEdge in face[iEdge:]:
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

print ("---")
start = time.time()
for i in range(50000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew (f1)
end = time.time()
print(end - start)

print ("---")
start = time.time()
for i in range(50000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnectedNew (f1)
end = time.time()
print(end - start)

print ("---")
start = time.time()
for i in range(50000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
    test = checkIfOneEdgeConnected (f1)
end = time.time()
print(end - start)

print ("---")
start = time.time()
for i in range(50000):
    f1 = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 10), (10, 5), (5, 7)]
    test = checkIfOneEdgeConnected (f1)
end = time.time()
print(end - start)