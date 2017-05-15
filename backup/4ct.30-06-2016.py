#!/usr/bin/env sage

#######
#######
# 4CT : Four color method using Tait edge three coloring + Kempe face reduction method + Kempe (half) chain color switching
#######
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# History:
# - 10/Maj/2016 - Creation data
# - 27/Maj/2016 - Added the support to loops and multiple edges. Actually loops are not permitted at the beginning and are avoided during the reduction process
# - 31/Maj/2016 - Sage bug in the show() funtion? Respose: use flush() before the show() funtion
# - 16/Jun/2016 - Restart from scratch. The case F2-F3 that generates loops cannot be avoid with the technic used so far
#               - I need to proceed in a different way: remove these cases
#                 - At the beginning there will be:
#                   - RULE-01: no F1 (loops)
#                   - RULE-01: nor F2+F2 = 0:0 = an island of one or more regions, all surrounded by a single face
#                   - RULE-03: no edges that do not separate two different faces
#                 - F2+F2  - Does not have to happen (to avoid) - Raise an exception - RULE-03 garantees that this will not happen
#                 - F2+F3  - Does not have to happen (to avoid) - Raise an exception - RULE-03 garantees that this will not happen
#                 - F2+F4> - This case can be easily handle O:O:
#                 - F3-F3  - This case can be handles ---O:O---
#                 - F3+F4>
#
# Notes:
# - This program uses these approaches together
#   - It consider Tait edge coloring and the equivalency of the 3-edge-coloring (known as Tait coloring) and 4-face-coloring (the original four color theorem for maps)
#   - Uses a modified Kempe reduction method: it does not shrink a face (faces <= F5) down to a point, but removes a single edge from it (for faces <= F5)
#   - Uses a modifiled Kempe chain edge color switching: when restoring edges from the reduced graph, it will swap Half of the cycle of a color chain
#
# Todo:
# - Logging system
# - Why faces() need to run the embeding planarity algorithm for cubic planar graph?
#   - I mean, if I know that the graph is planar (because I built it so), why do i need to make it planar to have the faces()
#     - A face can be computed as the shortest path to return from a vertex of the face to itself. Actually this will return three faces and each face will be returned twice: clockwise and counterclockwise
#
# Done:
# - Sage doesn't handle multiple edges or loops when embedding is involved
#   - For example G.faces() executes an embedding and returns an error if the graph contains an F2 or a loop
#   - To handle it, this program avoid loops, removing first F2 faces (with care of F2 near F3 faces) and then handle F3, F4, F5 cases (unavoidable set)
#
#######

import sys

import logging
import logging.config
import logging.handlers

from sage.all import *

# This solves this issue: http://ask.sagemath.org/question/33727/logging-failing-after-a-while/
#
# Only when running the code in the cloud: https://cloud.sagemath.com/
# sage_server.MAX_OUTPUT_MESSAGES = 100000 # Needed for the cloud version of Sage

#######
#######
# 4CT : Funtions
#######
#######

###########################################################################
# Return a face as a list of ordered vertices. Used to create random graphs
# Taken on the internet (http://trac.sagemath.org/ticket/6236)
###########################################################################
def facesByVertices(g):
    d = {}
    for key, val in g.get_embedding().iteritems():
        d[key] = dict(zip(val, val[1:] + [val[0]]))
    list_faces = []
    for start in d:
        while d[start]:
            face = []
            prev = start
            _, curr = d[start].popitem()
            face.append(start)
            while curr != start:
                face.append(curr)
                prev, curr = (curr, d[curr].pop(prev))
            list_faces.append(face)
    return list_faces


################################################################################################
# Return the dual of a graph. Used to create random graphs
# Taken on the internet: to make a dual of a tringolation (http://trac.sagemath.org/ticket/6236)
################################################################################################
def graphDual(g):
    f = [tuple(face) for face in facesByVertices(g)]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]
    dual = Graph([f_edges, lambda f1, f2: set(f1).intersection([(e[1], e[0]) for e in f2])])
    return dual


##########################################################################################
# Check if I can work with this graph: has to be planar and 3 regular (planar cubic graph)
##########################################################################################
def checkGraphAtBeginning(g):
    # Check 3-regularity
    #
    if g.is_regular(3) == False:
        logger.info("Error: The graph is not 3-regular")
        quit()
    else:
        logger.info("Good. The graph is 3-regular")

    # Check loops
    #
    if (g.has_loops() == True):
        logger.error("ERROR: It seems that loops are difficult to handle during reduction and recoloring, so I'll start without them and avoid their creation during the reduction process")
        quit()
    else:
        logger.info("OK. The graph does not have loops. Consider that this program will avoid their creation during the reduction process")

    # Check multiple edges
    #
    if (g.has_multiple_edges() == True):
        logger.error("ERROR: The graph has multiple edges")
        quit()
    else:
        logger.info("OK. The graph does not have multiple edges. Consider that this program will also handle multiple edges during the reduction process")

    # Check if the graph is planar
    #
    if (g.is_planar() == False):
        logger.error("ERROR: The graph is not planar")
        quit()
    else:
        logger.info("OK. The graph is planar")

    logger.info("It has numberOfFaces = %s", len(g.faces()))

    return


#############################################
# Rotate elements (works for lists and tuple)
#############################################
def rotate(l, n):
    return l[n:] + l[:n]


###################################################################################################################################
# join two faces
#
# f1[:indexOfedgeToRemoveOnF1] + f2[indexOfedgeToRemoveOnF2 + 1:] + f2[:indexOfedgeToRemoveOnF2] + f1[indexOfedgeToRemoveOnF1 + 1:]
#
# f1 = [(6, 1), (1, 2), (2, 7), (7, 6)]
# f2 = [(3, 8), (8, 7), (7, 2), (2, 3)]
# edgeToRemoveOnF1 = (2, 7))
# temp f1PlusF2 = [(6, 1), (1, 2), (2, 3), (3, 8), (8, 7), (7, 6)]
# f1PlusF2 = [(6, 1), (1, 3), (3, 8), (8, 6)]
#
# f1 = [(2, 7), (7, 6), (6, 1), (1, 2)]
# f2 = [(2, 3), (3, 8), (8, 7), (7, 2)]
# edgeToRemoveOnF1 = (2, 7))
# temp f1PlusF2 = [(2, 3), (3, 8), (8, 7), (7, 6), (6, 1), (1, 2)]
# f1PlusF2 = [(1, 3), (3, 8), (8, 6), (6, 1)]
#
# f1 = [(1, 2), (2, 7), (7, 6), (6, 1)]
# f2 = [(7, 2), (2, 3), (3, 8), (8, 7)]
# edgeToRemoveOnF1 = (2, 7))
# temp f1PlusF2 = [(1, 2), (2, 3), (3, 8), (8, 7), (7, 6), (6, 1)]
# f1PlusF2 = [(1, 3), (3, 8), (8, 6), (6, 1)]
#
# f1 = [(1, 2), (2, 3), (3, 1)]
# f2 = [(2, 4), (4, 3), (3, 2)]
# edgeToRemoveOnF1 = (2, 3))
# temp f1PlusF2 = [(1, 2), (2, 4), (4, 3), (3, 1)]
# f1PlusF2 = [(1, 4), (4, 1)]
#
# f1 = [(2, 1), (1, 2)]
# f2 = [(2, 3), (3, 1), (1, 2)]
# edgeToRemoveOnF1 = (2, 1))
# temp f1PlusF2 = [(2, 3), (3, 1), (1, 2)]
# f1PlusF2 = [(3, 3)]
###################################################################################################################################
def joinFaces(f1, f2, edgeToRemoveOnF1):

    # You can only use this funtion if at least one face has lenght > 2
    #
    if len(f1) == 2 and len(f2) == 2:
        raise Exception('Cannot join faces both of len 2 - It would generare a single edge face, with no vertices')

    # The edge (v1, v2) on f1 is (v2, v1) on the f2 face
    #
    edgeToRemoveOnF2 = rotate(edgeToRemoveOnF1,1)
    indexOfedgeToRemoveOnF1 = f1.index(edgeToRemoveOnF1)
    indexOfedgeToRemoveOnF2 = f2.index(edgeToRemoveOnF2)

    # Join the face - After this there will still be vertices to remove
    #
    f1PlusF2 = f1[:indexOfedgeToRemoveOnF1] + f2[indexOfedgeToRemoveOnF2 + 1:] + f2[:indexOfedgeToRemoveOnF2] + f1[indexOfedgeToRemoveOnF1 + 1:]

    # Debug
    #
    logger.debug("f1 = %s", f1)
    logger.debug("f2 = %s", f2)
    logger.debug("edgeToRemoveOnF1 = %s", edgeToRemoveOnF1)
    logger.debug("indexOfedgeToRemoveOnF1 = %s", indexOfedgeToRemoveOnF1)
    logger.debug("indexOfedgeToRemoveOnF2 = %s", indexOfedgeToRemoveOnF2)
    logger.debug("Temporary f1PlusF2 = %s", f1PlusF2)

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex A
    #
    # Search the egde that contains v1 (edgeToRemoveOnF1[0]) as the second element of the tuple
    # new vA = first element of the edge found
    # Search the egde that contains v1 (edgeToRemoveOnF1[0]) as the first element of the tuple
    # new vB = second element of the edge found
    #
    listOfJustOneTupleA = [(v1a, v2a) for v1a, v2a in f1PlusF2 if v2a == edgeToRemoveOnF1[0]]
    listOfJustOneTupleB = [(v1b, v2b) for v1b, v2b in f1PlusF2 if v1b == edgeToRemoveOnF1[0]]
    tupleA = listOfJustOneTupleA[0]
    tupleB = listOfJustOneTupleB[0]
    newEdge = (tupleA[0], tupleB[1])
    f1PlusF2.remove(tupleA)
    indexForInsert = f1PlusF2.index(tupleB)
    f1PlusF2.remove(tupleB)
    f1PlusF2.insert(indexForInsert, newEdge)

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    # Search the egde that contains v2 (edgeToRemoveOnF1[1]) as the second element of the tuple
    # new vA = first element of the edge found
    # Search the egde that contains v2 (edgeToRemoveOnF1[1]) as the first element of the tuple
    # new vB = second element of the edge found
    #
    listOfJustOneTupleA = [(v1a, v2a) for v1a, v2a in f1PlusF2 if v2a == edgeToRemoveOnF1[1]]
    listOfJustOneTupleB = [(v1b, v2b) for v1b, v2b in f1PlusF2 if v1b == edgeToRemoveOnF1[1]]
    tupleA = listOfJustOneTupleA[0]
    tupleB = listOfJustOneTupleB[0]
    newEdge = (tupleA[0], tupleB[1])
    f1PlusF2.remove(tupleA)
    indexForInsert = f1PlusF2.index(tupleB)
    f1PlusF2.remove(tupleB)
    f1PlusF2.insert(indexForInsert, newEdge)

    logger.debug("f1PlusF2 = %s", f1PlusF2)

    return f1PlusF2


#################################################################################
# Check if 1-edge-connected
# face = [(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)]
# In this example (1, 2) is the edge that make to graph 1-edge-connected
#################################################################################
def checkIfOneEdgeConnected(face):

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    isOneEdgeConnectedGraph = False

    # Now I have to remove the two vertices at the end of the edge to remove - Vertex B
    #
    iEdge = 0
    while isOneEdgeConnectedGraph == False and iEdge < len(face):
        reverseEdge = rotate(face[iEdge], 1)

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

##############################################
##############################################
# 4CT : Constants and variables initialization
##############################################
##############################################

# Set logging facilities
#
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
loggingStreamHandler = logging.StreamHandler(sys.stdout)
loggingStreamHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(loggingStreamHandler)

# General plot options
#
plotOptions = {'vertex_size': 150,
               'vertex_labels': True,
               'layout': "spring",
               'edge_style': 'solid',
               'edge_color': 'black',
               'edge_colors': None,
               'edge_labels': False,
               'iterations': 50,
               'tree_orientation': 'down',
               'heights': None,
               'graph_border': False,
               'talk': False,
               'color_by_label': True,
               'partition': None,
               'dist': .075,
               'max_dist': 1.5,
               'loop_size': .075}

# General plot options
#
edgeColorByLabel = {'green': 'green', 'blue': 'blue', 'red': 'red'}

# It will contain items made of lists of values to find the way back to the original graph (Ariadne's String Myth)
#
ariadneString = []

###################################################################################################################
###################################################################################################################
# MAIN: 4CT - Create/upload the graph to color. it has to be planar and without loops. Multiple edges are permitted
###################################################################################################################
###################################################################################################################

logger.info("--------------------------------")
logger.info("BEGIN: Create the graph to color")
logger.info("--------------------------------")

# G = Graph(sparse=True)
# G.allow_multiple_edges(True)
# G.allow_loops(True)
# G.add_edge(1,2,"1-2")
# G.add_edge(2,3,"2-3")
# G.add_edge(3,4,"3-4")
# G.add_edge(4,5,"4-5")
# G.add_edge(5,1,"5-1")
# G.add_edge(1,6,"1-6")
# G.add_edge(2,10,"2-10")
# G.add_edge(3,12,"3-12")
# G.add_edge(4,11,"4-11")
# G.add_edge(5,7,"5-7")
# G.add_edge(6,7,"6-7")
# G.add_edge(6,8,"6-8")
# G.add_edge(8,10,"8-10")
# G.add_edge(10,12,"10-12")
# G.add_edge(12,11,"12-11")
# G.add_edge(7,9,"7-9")
# G.add_edge(8,9,"8-9")
# G.add_edge(9,11,"9-11")

# G = simplicial_complexes.RandomTwoSphere(100).flip_graph()
# G.allow_multiple_edges(True)
# G.allow_loops(True)
# G.relabel()

# Create a random graph: dual of a tringulation
#
numberOfVerticesForTheRandomTriangulation = 10
tmpG = graphs.RandomTriangulation(numberOfVerticesForTheRandomTriangulation) # Random tringulation on the surface of a sphere

void = tmpG.is_planar(set_embedding=True, set_pos=True) # Cannot calculate the dual if the graph has not been embedded
G = graphDual(tmpG) # The dual of a triangulation is a 3-regular planar graph
void = G.is_planar(set_embedding=True, set_pos=True)

G.allow_loops(False) # At the beginning and during the process I'll avoid this situation anyway
G.allow_multiple_edges(True) # During the reduction process the graph may have multiple edges - It is normal

G.relabel() # The dual of a triangulation will have vertices represented by lists - triangles (v1, v2, v3) instead of a single value

for face in G.faces():
    logger.info("Face: %s", face)

# Mage a copy of the original graph
#
GOriginal = copy(G)

logger.info("Edges: %s", G.edges())

logger.info("------------------------------")
logger.info("END: Create the graph to color")
logger.info("------------------------------")
logger.info("")

#######
#######
# 4CT : AT THE BEGINNING THE GRAPH HAS TO BE CUBIC AND PLANAR
#######
#######

logger.info("------------------------")
logger.info("BEGIN: Graph information")
logger.info("------------------------")

checkGraphAtBeginning(G)

logger.info("----------------------")
logger.info("END: Graph information")
logger.info("----------------------")
logger.info("")

#######
#######
# 4CT : Method similar to the Kempe reduction "patching" method: for each loop remove an edge from a face <= F5, until the graph will have only three faces (an island with two lands)
#######
#######

endOfReductionProcess = False

# If the graph was already reduced, it will be a graph of three faces (an island with two lands) and three edges ... easily 3-edge-colorable
#
if len(G.vertices()) == 2:
    # Graph already reduced
    #
    endOfReductionProcess = True
    logger.info("The graph is already reduced")

logger.info("----------------------")
logger.info("BEGIN: Reduction phase")
logger.info("----------------------")

# Start the reduction process
#
iGlobalCounter = 0
while endOfReductionProcess == False:

    # Do one thing at a time and return at the beginning of this top level loop
    #
    oneThingDone = False

    # Remove all F2 and continue the process up to no F2 faces are left
    # I moved the case with multiple edges before the case with loops to avoid the loops, becouse they are more difficult to handle when restoring and coloring the graph
    # This way loops should never happen during the whole process
    #
    if G.has_multiple_edges() == True and oneThingDone == False and endOfReductionProcess == False:

        logger.info("BEGIN %s: Remove a multiple edge", iGlobalCounter)

        # Get one random (with the exception of not being near an F3 face) edge to remove
        # Exception: the edge does not have to separate an F2 and an F3 ... or a loop will be created ... and this is bad. In any graph this condition always holds: at leat an F2 exists close to an F > F3
        #
        # All the next steps (remove loops and multiple edges) are needed because I have to use faces() (which doesn't work with multiple faces or loops) to check the neighboor of the F2 face
        #
        g2 = copy(G)
        if g2.has_loops() == True:
            g2.remove_loops()
        if g2.has_multiple_edges() == True:
            g2.remove_multiple_edges()

        # The edge to select does not have to be near an F3
        #
        possibleEdges = G.multiple_edges()
        iEdges = 0
        edgeToRemoveFound = False
        logger.debug("possibleEdges = %s", possibleEdges)

        while edgeToRemoveFound == False and iEdges < len(possibleEdges):
            possibleEdge = possibleEdges[iEdges]
            logger.debug("possibleEdge = %s (degree = %s, degree = %s)", possibleEdge, g2.degree(possibleEdge[0]),
                         g2.degree(possibleEdge[1]))

            # The edge to remove can be found in the list of faces() as (v1, v2) or (v2, v1)
            #
            tmp1Edge = (possibleEdge[0], possibleEdge[1])
            tmp2Edge = (possibleEdge[1], possibleEdge[0])

            # One edge separates two faces
            # Consider that the original F2 doesn't exist after remove_multiple_edges(), so the two faces that separate the edge don't have to be F3
            #
            nearbyFaces = [x for x in g2.faces() if tmp1Edge in x or tmp2Edge in x]
            logger.debug("nearbyFaces = %s", nearbyFaces)
            if len(nearbyFaces[0]) > 3 and len(nearbyFaces[1]) > 3:
                edgeToRemove = possibleEdge
                edgeToRemoveFound = True
                # xxx logger.debug("len(f) = %s, %s", len(nearbyFaces[0]), nearbyFaces[0])
                # xxx logger.debug("len(other f) = %s, %s", len(nearbyFaces[1]), nearbyFaces[1])
                logger.debug("edgeToRemove = %s", edgeToRemove)
            else:
                iEdges = iEdges + 1

        # At this point an F2 edge near to a face bigger than 3 edges had to be found. If not, my assumption was not ok and I'd better study math a bit longer
        #
        if edgeToRemoveFound == False:
            logger.error("ERROR: Unexpected condition. Mario you'd better study math a bit longer")
            exit()

        # Get the two vertices to join
        # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O
        #
        verticesToJoin = G.neighbors(edgeToRemove[0]) + G.neighbors(edgeToRemove[1])
        verticesToJoin.remove(edgeToRemove[0])
        verticesToJoin.remove(edgeToRemove[1])

        # Delete the vertices (and the incident edges)
        #
        G.delete_vertex(edgeToRemove[0])
        G.delete_vertex(edgeToRemove[1])

        # Add the edge
        #
        G.add_edge(verticesToJoin[0], verticesToJoin[1])
        # xxx logger.debug("New edge = %s, %s", verticesToJoin[0], verticesToJoin[1])

        # Ariadne ball of thread. First parameter == 2, will tell that it was a multiple edge that has been removed
        # [2, v1, v2, vertexToJoinNearV1, vertexToJoinNearV2]
        #
        item = [2, edgeToRemove[0], edgeToRemove[1], verticesToJoin[0], verticesToJoin[1]]
        ariadneString.append(item)
        logger.debug("ariadneString: %s", item)

        # Do one thing at a time and return at the beginning of the main loop
        #
        oneThingDone = True
        logger.info("END: Remove a multiple edge")

    # Remove one loop. This condition could occur anytime during the reduction process, as for example after a removal of an edge that separates an F2 and an F3: ---.C:D
    # I moved the case with multiple edges before the case with loops to avoid the loops, becouse they are more difficult to handle when restoring and coloring the graph
    # This way loops should never happen during the whole process
    #
    if G.has_loops() == True and oneThingDone == False and endOfReductionProcess == False:

        logger.info("BEGIN %s: remove a loop", iGlobalCounter)
        logger.error("ERROR: Unexpected condition. Mario you'd better study math a bit longer")
        exit()

        # Log info
        #
        logger.info("The graph has loops. I'm about to remove one loop")

        # Select one random (if more than one loop exist, the first virtex in the list is ok) vertex with loop: ---.O
        #
        vertexWithLoop = G.loop_vertices()[0]
        logger.debug("vertexWithLoop = %s", vertexWithLoop)

        # Remove the looped edge ... or the next neighbors() funtion will return also the vertexWithLoop itself ---.
        #
        G.delete_edge(vertexWithLoop, vertexWithLoop)

        # Get the other vertex to remove: .---.
        #
        otherVertexToRemove = G.neighbors(vertexWithLoop)[0]

        # Remove the vertexWithLoop and its adjacent edges (the looped edge has been removed before)
        #
        G.delete_vertex(vertexWithLoop)

        # Get the two vertices to join
        # Consider also the case of this particular initial condition: ---.O.---.O (F2 ---.O.--- followed by a loop ---.O)
        #
        if len(G.neighbors(otherVertexToRemove)) == 2:
            oneEnd = G.neighbors(otherVertexToRemove)[0]
            otherEnd = G.neighbors(otherVertexToRemove)[1]
        else:
            oneEnd = G.neighbors(otherVertexToRemove)[0]
            otherEnd = G.neighbors(otherVertexToRemove)[0]

        # Delete the vertex and join together its neighbours
        # As said in the previous comment, this may create a loop
        #
        G.delete_vertex(otherVertexToRemove)

        # Add the new edge. It may even create a multiple edged face or a looped face. In this case I will handle during the next loop (do one thing at a time!)
        #
        logger.debug("New edge = %s, %s", oneEnd, otherEnd)
        G.add_edge(oneEnd, otherEnd)

        # Ariadne ball of thread. First parameter == 1, will tell that it was a loop that has been removed
        # [1, vertexWithLoop, otherVertexToRemove, vertexToJoin, otherVertexToJoin]
        #
        item = [1, vertexWithLoop, otherVertexToRemove, oneEnd, otherEnd]
        ariadneString.append(item)
        logger.debug("ariadneString: %s", item)

        # Do one thing at a time and return at the beginning of the main loop
        #
        oneThingDone = True

        logger.info("END: remove a loop")

    # Remove an F3 or F4 or F5. At this point they exist for sure (unavoidable set)
    #
    # 2016-06-09 05:49:44,752 - INFO --- BEGIN: Remove an F3, F4 or F5
    # 2016-06-09 05:49:44,765 - DEBUG --- Face <= 5: [(16, 17), (17, 71), (71, 16)]
    # 2016-06-09 05:49:44,765 - DEBUG --- edgeToRemove: (16, 17)
    # 2016-06-09 05:49:44,767 - DEBUG --- ariadneString: [3, 17, 16, 71, 71, 14, 15]
    # 2016-06-09 05:49:44,767 - INFO --- END: Remove an F3, F4 or F5
    #
    # 2016-06-09 05:49:44,781 - INFO --- BEGIN: Remove an F3, F4 or F5
    # 2016-06-09 05:49:44,792 - DEBUG --- Face <= 5: [(59, 55), (55, 49), (49, 52), (52, 59)]
    # 2016-06-09 05:49:44,792 - DEBUG --- edgeToRemove: (59, 55)
    # 2016-06-09 05:49:44,793 - DEBUG --- ariadneString: [4, 59, 55, 49, 52, 39, 45]
    # 2016-06-09 05:49:44,794 - INFO --- END: Remove an F3, F4 or F5
    #
    # 2016-06-09 05:49:44,652 - INFO --- BEGIN: Remove an F3, F4 or F5
    # 2016-06-09 05:49:44,667 - DEBUG --- Face <= 5: [(6, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    # 2016-06-09 05:49:44,667 - DEBUG --- edgeToRemove: (6, 2)
    # 2016-06-09 05:49:44,668 - DEBUG --- ariadneString: [5, 6, 2, 3, 5, 10, 75]
    # 2016-06-09 05:49:44,668 - INFO --- END: Remove an F3, F4 or F5
    #
    # v1 = [0][1]
    # v2 = [0][0]
    # v3 = [1][1]
    # v4 = [-1][0]
    #
    if oneThingDone == False and endOfReductionProcess == False:
        logger.info("BEGIN %s: Remove an F3, F4 or F5", iGlobalCounter)

        # Find the first face (index [0]) with len <= 5. It always exists: unavoidable set
        #
        faceToReduce = [x for x in G.faces() if len(x) <= 5][0]
        logger.debug("Face <= 5: %s", faceToReduce)
        lenOfTheFaceToReduce = len(faceToReduce)
        logger.debug("lenOfTheFaceToReduce: %s", lenOfTheFaceToReduce)

        # Take a random edge of the face (0 index is just fine)
        #
        edgeToRemove = faceToReduce[0]
        logger.debug("edgeToRemove: %s", edgeToRemove)

        # Get the vertices at the ends of the edge to remove
        # And find the other four neigbours :>---<: (If the --- is the removed edge, the four dots represent the vertices I'm looking for)
        #
        v1 = faceToReduce[0][1]
        v2 = faceToReduce[0][0]
        vertexToJoinNearV1OnTheFace = faceToReduce[1][1]
        vertexToJoinNearV2OnTheFace = faceToReduce[-1][0]
        # xxx logger.debug("v1, v2, vertexToJoinNearV1OnTheFace, vertexToJoinNearV2OnTheFace: %s, %s, %s, %s", v1, v2, vertexToJoinNearV1OnTheFace, vertexToJoinNearV2OnTheFace)

        # First delete the edge ... or it will be returned during the next calls when not needed
        #
        G.delete_edge(edgeToRemove)

        # Find the other four neigbours :>---<: ( If the --- is the removed edge, the four dots represent the vertices I'm looking for)
        #
        # TODO: For the restoring process, I need to consider the ordering (clockwise) to know which vertex is "left" and which is "right" (looking it with the edge to remove as the base)
        #
        neighborsOfTheFirstVertex = G.neighbors(v1)
        neighborsOfTheSecondVertex = G.neighbors(v2)

        neighborsOfTheFirstVertex.remove(vertexToJoinNearV1OnTheFace)
        vertexToJoinNearV1NotOnTheFace = neighborsOfTheFirstVertex[0]
        neighborsOfTheSecondVertex.remove(vertexToJoinNearV2OnTheFace)
        vertexToJoinNearV2NotOnTheFace = neighborsOfTheSecondVertex[0]

        # Now that I know the neighbors, I can remove the vertices of the edge to remove. Also the edges will be automatically removed ... which is good
        #
        G.delete_vertex(v1)
        G.delete_vertex(v2)

        # Create two new connections
        #
        # xxx logger.debug("New edge: %s, %s", vertexToJoinNearV1OnTheFace, vertexToJoinNearV1NotOnTheFace)
        # xxx logger.debug("New edge: %s, %s", vertexToJoinNearV2OnTheFace, vertexToJoinNearV2NotOnTheFace)
        G.add_edge(vertexToJoinNearV1OnTheFace, vertexToJoinNearV1NotOnTheFace)
        G.add_edge(vertexToJoinNearV2OnTheFace, vertexToJoinNearV2NotOnTheFace)

        # Ariadne ball of thread
        # First parameter == lenOfTheFaceToReduce, will tell that it was a Fx face that has been removed (x = 3, 4 or 5)
        # [x, v1, v2, vertexToJoinNearV1OnTheFace, vertexToJoinNearV2OnTheFace, vertexToJoinNearV1NotOnTheFace, vertexToJoinNearV2NotOnTheFace]
        #
        item = [lenOfTheFaceToReduce, v1, v2, vertexToJoinNearV1OnTheFace, vertexToJoinNearV2OnTheFace, vertexToJoinNearV1NotOnTheFace, vertexToJoinNearV2NotOnTheFace]
        ariadneString.append(item)
        logger.debug("ariadneString: %s", item)

        # Do one thing at a time and return at the beginning of the main loop
        #
        oneThingDone = True

        logger.info("END: Remove an F3, F4 or F5")

    # Something has been done! Plot it
    #
    if endOfReductionProcess == False:
        iGlobalCounter += 1
        # G.plot()
        # show(G)

    # If the graph has been completely reduced, it will be a graph of three faces (an island with two lands) and three edges ... easily 3-edge-colorable
    #
    if len(G.vertices()) == 2:
        # Graph reduced
        #
        endOfReductionProcess = True
        logger.debug("The graph has been reduced")

logger.info("--------------------")
logger.info("END: Reduction phase")
logger.info("--------------------")
logger.info("")

logger.info("-----------------------------------")
logger.info("BEGIN: Ariadne's string information")
logger.info("-----------------------------------")

# Log Ariadne's string information
#
for i in ariadneString:
    logger.info("ariadneString: %s", i)

logger.info("---------------------------------")
logger.info("END: Ariadne's string information")
logger.info("---------------------------------")
logger.info("")

exit()

#######
#######
# 4CT : Restore the edges one at a time and apply the half Kempe-cycle color switching method
# 4CT : Depending if the restored face is an F2, F3, F4, F5, different actions will be taken to be able to apply, at the end, the half Kempe-cycle color switching
#######
#######

logger.info("---------------------------")
logger.info("BEGIN: Reconstruction phase")
logger.info("---------------------------")

# At this point the graph has three faces (an island with two lands) and three edges ... easily 3-edge-colorable
# Since the color of the edges of a multi edge graph cannot be changed, I need to remove and recreate the edges with the right colors
#
G.delete_edges(G.edges())
v1 = G.vertices()[0]
v2 = G.vertices()[1]
G.add_edge(v1, v2, "red")
G.add_edge(v1, v2, "green")
G.add_edge(v1, v2, "blu")

# G.show()

endOfRebuildProcess = False
while endOfRebuildProcess == False:

    # Get the edge to restore
    #
    ariadneStep = ariadneString.pop()
    logger.info("ariadneStep: %s", ariadneStep)

    # Example:
    # ('ariadneString', [4, 4, 0, 5, 7, 1, 8])
    # ('ariadneString', [4, 1, 0, 8, 3, 2, 14])
    # ('ariadneString', [5, 9, 10, 12, 5, 0, 6])
    # ('ariadneString', [3, 8, 0, 10, 11, 10, 15])
    # ('ariadneString', [5, 2, 0, 14, 6, 0, 12])
    # ('ariadneString', [4, 13, 12, 14, 15, 10, 14])
    # ('ariadneString', [3, 10, 0, 12, 14, 0, 12]) --> Firt pop() retrieve this element (the last appended)
    #
    # Other example:
    # ('ariadneString', [5, 1, 0, 2, 12, 8, 14])
    # ('ariadneString', [4, 2, 0, 14, 3, 4, 15])
    # ('ariadneString', [3, 9, 8, 13, 10, 11, 13])
    # ('ariadneString', [5, 4, 0, 15, 6, 7, 11])
    # ('ariadneString', [2, 7, 11, 5, 13])
    # ('ariadneString', [4, 13, 5, 8, 15, 0, 14])
    # ('ariadneString', [2, 0, 14, 5, 8]) --> Firt pop() retrieve this element (the last appended)
    #
    # [1, vertexWithLoop, otherVertexToRemove, vertexToJoin, otherVertexToJoin] --> Don't consider this case. It will never happen with this reduction procedure
    # [2, v1, v2, vertexToJoinNearV1, vertexToJoinNearV2]
    # [3, 4 or 5, v1, v2, vertexToJoinNearV1OnTheFace, vertexToJoinNearV2OnTheFace, vertexToJoinNearV1NotOnTheFace, vertexToJoinNearV2NotOnTheFace]
    #
    if ariadneStep[0] == 1:
        logger.info("BEGIN: restore a loop")
        logger.error("ERROR: Unexpected condition. Mario you'd better study math a bit longer")
        exit()
    if ariadneStep[0] == 2:
        logger.info("BEGIN: restore a multiedge")
        edgeTemp = G.edges(ariadneString[3], ariadneString[4])
        logger.info("END: restore a multiedge")
    if ariadneStep[0] == 3:
        logger.info("BEGIN: restore an F3")
        edgeTemp = G.edges(ariadneString[3], ariadneString[4])
        logger.info("END: restore an F3")
    if ariadneStep[0] == 4:
        logger.info("BEGIN: restore an F4")
        edgeTemp = G.edges(ariadneString[3], ariadneString[4])
        logger.info("END: restore an F4")
    if ariadneStep[0] == 5:
        logger.info("BEGIN: restore an F5")
        edgeTemp = G.edges(ariadneString[3], ariadneString[4])
        logger.info("END: restore an F5")

    # If no other edges are to be restored, then I've done
    #
    if len(ariadneString) == 0:
        endOfRebuildProcess = True

logger.info("-------------------------")
logger.info("END: Reconstruction phase")
logger.info("-------------------------")
logger.info("")

#######
#######
# 4CT : Show the restored and 4 colored map
#######
#######

show(G)
