Hi all,

the Homepage where you can read the whole story is here: https://4coloring.wordpress.com

## Example of what the program does

This is an example of a graph colored with the Python program:
<p>
  <a href="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges.png">
    <img src="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges-small.png">
  </a>
</p>

The graph has 1996 vertices and 2994 edges and, starting from the planar representation of it, it took about 10 seconds to be colored:
- https://4coloring.wordpress.com/2017/07/09/four-color-theorem-a-fast-algorithm-2/

The input .dot file used can be downloaded here: <a href="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges.dot">Test-1996-Vertices-2994-Edges.dot</a>
- From an .edgelist graph (<a href="https://networkx.github.io/documentation/networkx-1.9.1/reference/readwrite.edgelist.html">networkx</a>) I generated an embedding of the graph on the plane. I used the Sage function is_planar(set_embedding = True)) 
- Then, from the planar representation of the original graph I used my algorithm

Note:
- The .dot file can be used to test other algorithms. If you know faster algorithms to color it please let me know

Definition of "planar embedding":
- A combinatorial embedding of a graph is a clockwise ordering of the neighbors of each vertex. From this information one can define the faces of the embedding, which is what this method returns
  - Planar representation example:
    - graphs.TetrahedralGraph().faces()
      - [[(0, 1), (1, 2), (2, 0)], [(3, 2), (2, 1), (1, 3)], [(2, 3), (3, 0), (0, 2)], [(0, 3), (3, 1), (1, 0)]]

## YouTube videos

Some videos of the running Python and Java programs:
- https://www.youtube.com/user/mariostefanutti/videos

## Pre-requìrements
- docker

## Download a pre-configured dockerized sage docker instance (I used sagemath latest = 9.0, python 3.7)
- docker run -it sagemath/sagemath:latest bash
  - sudo apt-get update
  - sudo apt-get install git
  - sudo apt-get install vim

### Download personal repo
- cd
- mkdir prj
- cd prj
- git clone https://github.com/stefanutti/maps-coloring-python.git

## Run 4ct.py
- cd
- cd prj
- cd maps-coloring-python
- cd ct
- sage 4ct.py --help
- sage 4ct.py -r 100
  - Random graph: dual of a triangulation of N vertices
- other parameters
  - -i <file .edgelist> (Load a .edgelist file - networkx)
  - -p <file .serialized> (Load a .serialized planar embedding of the graph)
  - -o <file name without extension> (Save a .edgelist file (networkx), plus a .dot file (networkx)

## Run ct_create_random_maps_from_2v.py
- cd
- cd prj
- cd maps-coloring-python
- cd ct
- python3 ct_create_random_maps_from_2v.py -v 100 -o new_map_test_100.planar
- sage 4ct.py -p new_map_test_100.planar

## Run ct_convert_planar_to_other.py
- Additional dependencies
  - pip3 install networkx
  - pip3 install pydot
- cd
- cd prj
- cd maps-coloring-python
- cd ct
- python3 ct_convert_planar_to_other.py -p new_map_test_100.planar -o new_map_test_100

## To be finished:
- What I've done that needs to be changed:
  - Generated a large planar triangulation using sage RandomTriangulation (fast)
  - Generated the dual of the planar triangulation, which is planar too (fast)
  - Now, to get the list of faces() sage needs to elaborate le planarity of the graph (very slow)
- I need other approaches, possibly not using sage
  - Implementation of the Bowyer-Watson algorithm to compute the Delaunay triangulation and the Voronoi diagram of a set o 2D points
    - https://github.com/jmespadero/pyDelaunay2D (to substitute the sage function)
  - By hand
    - Generate a large planar triangulation with libs that are not sage (fast)
    - Generate the dual of the planar triangulation, which is planar too (fast)
    - Manually compute the faces() representation of the graph

Bye
