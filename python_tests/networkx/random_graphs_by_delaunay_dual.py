#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
Simple structured Delaunay triangulation in 2D with Bowyer-Watson algorithm.

Written by Jose M. Espadero ( http://github.com/jmespadero/pyDelaunay2D )
Based on code from Ayron Catteau. Published at http://github.com/ayron/delaunay

Just pretend to be simple and didactic. The only requisite is numpy.
Robust checks disabled by default. May not work in degenerate set of points.
"""

import numpy as np
from math import sqrt
import networkx as nx

#################################################################################################
# Return the dual of a graph. Used to create random graphs
# Taken on the internet: to make a dual of a triangulation (http://trac.sagemath.org/ticket/6236)
#################################################################################################
def graph_dual(faces_by_vertices):
    print("faces_by_vertices: ", faces_by_vertices)
    f = [tuple(face) for face in faces_by_vertices]
    f_edges = [tuple(zip(i, i[1:] + (i[0],))) for i in f]
    print ("f_edges: ", f_edges)
    xxx = [f_edges, lambda f1, f2: set(f1).intersection([(e[1], e[0]) for e in f2])]


    print ("xxx: ", xxx)

    g = lambda x, y: x ** 2 + y
    print ("xxx: ", g(8, 3))

    nums = range(2, 50)
    for i in range(2, 8):
        nums = filter(lambda x: x == i or x % i, nums)
        print ("nums: ", nums(8))

    # dual = nx.Graph()

    return xxx



class Delaunay2D:
    """
    Class to compute a Delaunay triangulation in 2D
    ref: http://en.wikipedia.org/wiki/Bowyer-Watson_algorithm
    ref: http://www.geom.uiuc.edu/~samuelp/del_project.html
    """

    def __init__(self, center=(0, 0), radius=9999):
        """ Init and create a new frame to contain the triangulation
        center -- Optional position for the center of the frame. Default (0,0)
        radius -- Optional distance from corners to the center.
        """
        center = np.asarray(center)
        # Create coordinates for the corners of the frame
        self.coords = [center+radius*np.array((-1, -1)),
                       center+radius*np.array((+1, -1)),
                       center+radius*np.array((+1, +1)),
                       center+radius*np.array((-1, +1))]

        # Create two dicts to store triangle neighbours and circumcircles.
        self.triangles = {}
        self.circles = {}

        # Create two CCW triangles for the frame
        T1 = (0, 1, 3)
        T2 = (2, 3, 1)
        self.triangles[T1] = [T2, None, None]
        self.triangles[T2] = [T1, None, None]

        # Compute circumcenters and circumradius for each triangle
        for t in self.triangles:
            self.circles[t] = self.circumcenter(t)

    def circumcenter(self, tri):
        """Compute circumcenter and circumradius of a triangle in 2D.
        Uses an extension of the method described here:
        http://www.ics.uci.edu/~eppstein/junkyard/circumcenter.html
        """
        pts = np.asarray([self.coords[v] for v in tri])
        pts2 = np.dot(pts, pts.T)
        A = np.bmat([[2 * pts2, [[1],
                                 [1],
                                 [1]]],
                      [[[1, 1, 1, 0]]]])

        b = np.hstack((np.sum(pts * pts, axis=1), [1]))
        x = np.linalg.solve(A, b)
        bary_coords = x[:-1]
        center = np.dot(bary_coords, pts)

        # radius = np.linalg.norm(pts[0] - center) # euclidean distance
        radius = np.sum(np.square(pts[0] - center))  # squared distance
        return (center, radius)

    def inCircleFast(self, tri, p):
        """Check if point p is inside of precomputed circumcircle of tri.
        """
        center, radius = self.circles[tri]
        return np.sum(np.square(center - p)) <= radius

    def inCircleRobust(self, tri, p):
        """Check if point p is inside of circumcircle around the triangle tri.
        This is a robust predicate, slower than compare distance to centers
        ref: http://www.cs.cmu.edu/~quake/robust.html
        """
        m1 = np.asarray([self.coords[v] - p for v in tri])
        m2 = np.sum(np.square(m1), axis=1).reshape((3, 1))
        m = np.hstack((m1, m2))    # The 3x3 matrix to check
        return np.linalg.det(m) <= 0

    def addPoint(self, p):
        """Add a point to the current DT, and refine it using Bowyer-Watson.
        """
        p = np.asarray(p)
        idx = len(self.coords)
        # print("coords[", idx,"] ->",p)
        self.coords.append(p)

        # Search the triangle(s) whose circumcircle contains p
        bad_triangles = []
        for T in self.triangles:
            # Choose one method: inCircleRobust(T, p) or inCircleFast(T, p)
            if self.inCircleFast(T, p):
                bad_triangles.append(T)

        # Find the CCW boundary (star shape) of the bad triangles,
        # expressed as a list of edges (point pairs) and the opposite
        # triangle to each edge.
        boundary = []
        # Choose a "random" triangle and edge
        T = bad_triangles[0]
        edge = 0
        # get the opposite triangle of this edge
        while True:
            # Check if edge of triangle T is on the boundary...
            # if opposite triangle of this edge is external to the list
            tri_op = self.triangles[T][edge]
            if tri_op not in bad_triangles:
                # Insert edge and external triangle into boundary list
                boundary.append((T[(edge+1) % 3], T[(edge-1) % 3], tri_op))

                # Move to next CCW edge in this triangle
                edge = (edge + 1) % 3

                # Check if boundary is a closed loop
                if boundary[0][0] == boundary[-1][1]:
                    break
            else:
                # Move to next CCW edge in opposite triangle
                edge = (self.triangles[tri_op].index(T) + 1) % 3
                T = tri_op

        # Remove triangles too near of point p of our solution
        for T in bad_triangles:
            del self.triangles[T]
            del self.circles[T]

        # Retriangle the hole left by bad_triangles
        new_triangles = []
        for (e0, e1, tri_op) in boundary:
            # Create a new triangle using point p and edge extremes
            T = (idx, e0, e1)

            # Store circumcenter and circumradius of the triangle
            self.circles[T] = self.circumcenter(T)

            # Set opposite triangle of the edge as neighbour of T
            self.triangles[T] = [tri_op, None, None]

            # Try to set T as neighbour of the opposite triangle
            if tri_op:
                # search the neighbour of tri_op that use edge (e1, e0)
                for i, neigh in enumerate(self.triangles[tri_op]):
                    if neigh:
                        if e1 in neigh and e0 in neigh:
                            # change link to use our new triangle
                            self.triangles[tri_op][i] = T

            # Add triangle to a temporal list
            new_triangles.append(T)

        # Link the new triangles each another
        N = len(new_triangles)
        for i, T in enumerate(new_triangles):
            self.triangles[T][1] = new_triangles[(i+1) % N]   # next
            self.triangles[T][2] = new_triangles[(i-1) % N]   # previous

    def exportTriangles(self):
        """Export the current list of Delaunay triangles
        """
        # Filter out triangles with any vertex in the extended BBox
        # return [[(a-4, b-4), (b-4, c-4), (c-4, a-4)] for (a, b, c) in self.triangles if a > 3 and b > 3 and c > 3]
        aaa = [[a-4, b-4, c-4] for (a, b, c) in self.triangles if a > 3 and b > 3 and c > 3]
        return aaa



# Create a random set of 2D points
seeds = np.random.random((10, 2))

# Create delaunay Triangulation
dt = Delaunay2D()
for s in seeds:
    dt.addPoint(s)

# Dump triangles
bbb = dt.exportTriangles()

ccc = graph_dual(bbb)
