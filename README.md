Hi all,

the Homepage where you can read the whole story is here: https://4coloring.wordpress.com

## Example

This is an example of graph colored with the Python program:
<p>
  <a href="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges.png">
    <img src="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges-small.png">
  </a>
</p>

The graph has 1996 vertices and 2994 edges and, starting from the planar representation of it, it took about 20 seconds to be colored.

The dot file is here: <a href="https://github.com/stefanutti/maps-coloring-python/blob/master/graphs_created_and_colored/Test-1996-Vertices-2994-Edges.dot">Test-1996-Vertices-2994-Edges.dot</a>
- From a .edgeList graph (https://networkx.github.io/documentation/networkx-1.9.1/reference/readwrite.edgelist.html) I generate an embedding of the graph sSage function is_planar(set_embedding = True)) in the plane and save it as the 
- From the planar representation of the original graph I use my algorithm

Definition: A combinatorial embedding of a graph is a clockwise ordering of the neighbors of each vertex. From this information one can define the faces of the embedding, which is what this method returns

Example:
- graphs.TetrahedralGraph().faces()
- [[(0, 1), (1, 2), (2, 0)], [(3, 2), (2, 1), (1, 3)], [(2, 3), (3, 0), (0, 2)], [(0, 3), (3, 1), (1, 0)]]

And some videos of the running Python and Java programs:
- https://www.youtube.com/user/mariostefanutti/videos

## Installation

For the installation (docker version) of the environment to run the python 4ct program, read this page:
- https://github.com/stefanutti/docker-utils/tree/master/dockerization/4ct

Bye
