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

## Installation

You can decide to use a pre-configured Docker container or create a Docker container and then install the software in it or just install the software needed to execute the program.

## Pre-configured docker container (skip all next steps up to "Run 4ct.py")
- https://hub.docker.com/r/stefanutti/4ct

## Prepare a docker machine
- https://github.com/stefanutti/unix-utils

### Next steps will build a container made of (+ all dependencies):
- Ubuntu 16.04 LTS from https://store.docker.com/images/ubuntu
- https://github.com/tensorflow/tensorflow 1.1.0 (needed to use ai against the 4cp)
- http://www.sagemath.org (not installed because too large: read the instructions on github)
- git clone https://github.com/stefanutti/maps-coloring-python (read the instructions on github)

### Install - ubuntu docker container
- docker run -it --name 4ct-temp ubuntu:16.04 bash
- docker commit 4ct-temp stefanutti/4ct:1.0 (commit the container to create a personal new image to work with)
- docker tag 4ct-temp stefanutti/4ct:latest
- docker rm 4ct-temp
- docker run -it -p 8888:8888 -p 6006:6006 --name 4ct -e PASSWORD=4ct -v /tmp/.X11-unix:/tmp/.X11-unix -v /docker-mounts:/docker-mounts -e DISPLAY=unix$DISPLAY --device /dev/dri --device /dev/snd stefanutti/4ct:latest bash
  - /docker-mounts/SageMath is a dir in the hosting machine that contains the sage product
    - This is done to avoid the re-installation of sage everytime I need to rebuild the docker container

### Install - utilities
- apt-get update
- apt-get install vim
- apt-get install git
- apt-get upgrade

### Install - Python
- apt-get install python-pip python-dev

### Install - Sage (sage download is about 1.3 GB compressed and more than 4 GB when uncompressed)
- Note:
  - The python project needs sage to make the embedding of a graph. This dependency will be removed in the future
- Read the installation info from here: http://www.sagemath.org/
  - tar xvf <sage file name>.tar in /docker-mounts
- Into the Docker container
  - ln -s /docker-mounts/SageMath/sage /usr/local/bin/sage
  - ./sage to test it (the first execution will configure sage)
    - If ERROR: ImportError: libgfortran.so.3: cannot open shared object file: No such file or directory
      - apt-get update
      - apt-get install build-essential
      - apt-get upgrade
      - apt-get install libgfortran3
    
### Download personal repo
- cd
- mkdir prj
- cd prj
- git clone https://github.com/stefanutti/maps-coloring-python.git
- git clone https://github.com/stefanutti/unix-utils.git

## Run 4ct.py
- cd
- source ./prj/maps-coloring-python/set_environment.sh
- cd prj
- cd maps-coloring-python
- sage 4ct.py --help
- sage 4ct.py -r 100 (Random graph: dual of a triangulation of N vertices)
- other parameters
  - -i <file .edgelist> (Load a .edgelist file - networkx)
  - -p <file .serialized> (Load a .serialized planar embedding of the graph)
  - -o <file name without extension> (Save a .edgelist file (networkx), plus a .dot file (networkx)

## To be finished:
- Now I have:
  - Generated a large planar triangulation using sage RandomTriangulation (fast)
  - Generated the dual of the planar triangulation, which is planar too (fast)
  - Now, to get the list of faces() sage needs to elaborate le planarity of the graph (very slow)
- I need other approaches, possibly not using sage
  - Implementation of the Bowyer-Watson algorithm to compute the Delaunay triangulation and the Voronoi diagram of a set o 2D points
    - https://github.com/jmespadero/pyDelaunay2D (to substitute the safe function)
  - By hand
    - Generate a large planar triangulation with libs that are not sage (fast)
    - Generate the dual of the planar triangulation, which is planar too (fast)
    - Manually compute the faces() representation of the graph

Bye
