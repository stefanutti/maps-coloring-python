###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti, Italy, Rome, 12/Feb/1969
# Website: https://4coloring.wordpress.com/
#
# 4CT: Generate random planar graphs without using graphs library and most important without using complex algotithms, as the planarity embedding or testing functions
#
# I directly use the planar graph representation of a map, as described here:
#
# http://doc.sagemath.org/html/en/reference/graphs/sage/graphs/generic_graph.html#sage.graphs.generic_graph.GenericGraph.faces
# graphs.TetrahedralGraph().faces()
# [[(0, 1), (1, 2), (2, 0)],
#  [(3, 2), (2, 1), (1, 3)],
#  [(3, 0), (0, 2), (2, 3)],
#  [(3, 1), (1, 0), (0, 3)]]
#
# A combinatorial embedding of a graph is a clockwise ordering of the neighbors of each vertex.
#
# This is the base map
# g_faces = [[(1, 2), (2, 1)], [(1, 2), (2, 1)], [(1, 2), (2, 1)]]
# A circle with its diameter
#
# Faces are represented "clockwise"
# Last face is always the ocean. The ocean is represented "counter-clockwise"
#
# History:
# - 19/Mar/2018 - Creation data
#
# TODOs:
# - Fix docstring for each function
#
# Done:
#
###

__author__ = "Mario Stefanutti <mario.stefanutti@gmail.com>"
__credits__ = "Mario Stefanutti <mario.stefanutti@gmail.com>, someone_who_would_like_to_help@nowhere.com"

import argparse
import sys
import logging
import random
import json
from time import perf_counter


def parse_args():

    parser = argparse.ArgumentParser(description='4ct args')

    parser.add_argument("-f", "--faces", help="Stop at f faces", type=int, required=True)
    parser.add_argument("-o", "--output", help="Save a json", required=False)
    parser.add_argument("--log_level", default="DEBUG", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], help="Logging level.")
    parser.add_argument("--fast", action="store_true", help="Use faster generation algorithm (edge index + in-place updates).")
    parser.add_argument("--show_graph", action="store_true", help="Visualize the generated graph (Plotly static if --no_html).")
    return parser.parse_args()


def save_to_file(data, output_file):
    if output_file is not None:
        with open(output_file, "w") as fp:
            json.dump(data, fp)
    else:
        print(data)


class PlanarGraphGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def rotate(l, n):
        """
        Rotate elements (works for lists and tuple)

        Parameters
        ----------
            l: The list to rotate
            n: Index for rotating the list and tuple

        Returns
        -------
            The modified list or tuple
        """

        return l[n:] + l[:n]

    def _log_faces(self, faces):
        if self.logger.isEnabledFor(logging.DEBUG):
            for face in faces:
                self.logger.debug("Face: %s", face)

    def _split_face(self, selected_face, index_of_the_first_selected_edge, index_of_the_second_selected_edge, new_vertex_id):
        """
        Split a face by inserting a new edge whose endpoints are two new vertices.

        Parameters
        ----------
            selected_face: The face to split
            index_of_the_first_selected_edge: Index of first selected edge
            index_of_the_second_selected_edge: Index of second selected edge
            new_vertex_id: Id of the first of the two new vertices (the second is new_vertex_id + 1)

        Returns
        -------
            [face1, face2]: The two new faces
        """
        if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("BEGIN: split_face")

        new_first_face = (
            selected_face[:index_of_the_first_selected_edge]
            + [(selected_face[index_of_the_first_selected_edge][0], new_vertex_id)]
            + [(new_vertex_id, new_vertex_id + 1)]
            + [(new_vertex_id + 1, selected_face[index_of_the_second_selected_edge][1])]
            + selected_face[index_of_the_second_selected_edge + 1:]
        )

        if index_of_the_first_selected_edge != index_of_the_second_selected_edge:
            new_second_face = (
                [(new_vertex_id, selected_face[index_of_the_first_selected_edge][1])]
                + selected_face[index_of_the_first_selected_edge + 1:index_of_the_second_selected_edge]
                + [(selected_face[index_of_the_second_selected_edge][0], new_vertex_id + 1)]
                + [(new_vertex_id + 1, new_vertex_id)]
            )
        else:
            new_second_face = [(new_vertex_id, new_vertex_id + 1), (new_vertex_id + 1, new_vertex_id)]

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("new_first_face: %s", new_first_face)
            self.logger.debug("new_second_face: %s", new_second_face)
            self.logger.debug("END: split_face")

        return [new_first_face, new_second_face]

    def _add_vertex_to_face(self, face_to_update, edge_to_search, vertex_to_insert):
        """
        Add a vertex to a face

        Parameters
        ----------
            face_to_update: The face to update
            edge_to_search: The edge to search
            vertex_to_insert: The vertex to insert

        Returns
        -------
            new_face_to_return: Returns the new face
        """

        if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("BEGIN: add_vertex_to_face")

        # Insert the new vertex
        index_where_to_insert_the_new_vertex = face_to_update.index(edge_to_search)
        new_face_to_return = face_to_update[:index_where_to_insert_the_new_vertex] + [(face_to_update[index_where_to_insert_the_new_vertex][0], vertex_to_insert)] + [(vertex_to_insert, face_to_update[index_where_to_insert_the_new_vertex][1])] + face_to_update[index_where_to_insert_the_new_vertex + 1:]

        # Return the new face
        if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("END: add_vertex_to_face: %s", new_face_to_return)
        return new_face_to_return

    def print_map_statistics(self, g_faces):
        """
        Print the statistics of the map

        Parameters
        ----------
            g_faces: The faces to print
        """

        # Print the statistics of the map
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info("Statistics up to F6, of the created map with %s faces:", len(g_faces))

            for i in range(2, 7):
                self.logger.info("- F%s: %s", i, sum(len(face) == i for face in g_faces))

    def generate(self, number_of_faces_to_generate):
        """
        Create a planar graph from a base graph

        Parameters
        ----------
            args: The args from the command line
        """

        # This is the base map - See drawing: 07/Apr/2018, pag 0
        g_faces = [[(1, 2), (2, 1)], [(1, 2), (2, 1)], [(1, 2), (2, 1)]]

        # Main loop: up to the number of requested faces to be created (1 new face = 2 new vertices = 3 new edges)
        i_face = 4
        i_vertex = 3
        last_log_time = perf_counter()
        if self.logger.isEnabledFor(logging.DEBUG): self._log_faces(g_faces)
        while i_face <= number_of_faces_to_generate:

            # Choose a random face
            # -2 will exclude the ocean (the last face). Valid for all the loops below. Last face is always the ocean
            i_selected_face = random.randint(0, len(g_faces) - 2)
            selected_face = g_faces[i_selected_face]
            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("Selected face: %s", selected_face)

            # Choose two random edges of the previously selected face. The two random edges may be the same edge
            # From the middle of these two selected edges, a new edge is going to be created
            # See drawing: 07/Apr/2018, pag 2
            # Notes: Using this method, too many F2 faces are created

            # TODO: Why if STRANGE_BEHAVIOUR = 2, the_graph.is_isomorphic(the_colored_graph) is very slow? I was trying to avoid too many F2 faces
            STRANGE_BEHAVIOUR = 1
            if STRANGE_BEHAVIOUR == 1:
                index_of_the_first_selected_edge = random.randint(0, len(selected_face) - 1)
                index_of_the_second_selected_edge = random.randint(index_of_the_first_selected_edge, len(selected_face) - 1)
            else:
                index_of_the_first_selected_edge = 0
                index_of_the_second_selected_edge = len(selected_face) // 2

            first_selected_edge = selected_face[index_of_the_first_selected_edge]
            second_selected_edge = selected_face[index_of_the_second_selected_edge]
            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("Selected edges: %s at index = %s, %s at index = %s", first_selected_edge, index_of_the_first_selected_edge, second_selected_edge, index_of_the_second_selected_edge)

            # Split the selected face into two new faces 
            # Add the new edge from the first_selected_edge to the second_selected_edge (may be the same edge)
            the_two_new_faces = self._split_face(selected_face, index_of_the_first_selected_edge, index_of_the_second_selected_edge, i_vertex)
            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("the_two_new_faces = %s", the_two_new_faces)

            ####
            # STEP: Start adjusting the two faces (may be also just one face) touched by the new edge that has been created
            ####
            #
            # Depending on the situation, one or two faces may be found (touched)
            # See drawing: 07/Apr/2018, pag 1
            #
            # Edge to find
            edge_to_find = self.rotate(first_selected_edge, 1)

            # Search the map
            faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]

            # If the selected face is a F2 face, for sure one of the faces_that_have_been_found is the selected face
            if (len(selected_face) == 2):
                faces_that_have_been_found.remove(selected_face)

            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)

            # Depending on the situation, some checks need to be done
            if (len(faces_that_have_been_found) == 1):
                face_to_adjust = faces_that_have_been_found[0]
                adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[0], edge_to_find,i_vertex)
            elif (len(faces_that_have_been_found) == 2):
                if (len(faces_that_have_been_found[0]) == 2):
                    face_to_adjust = faces_that_have_been_found[0]
                    adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex)
                else:
                    face_to_adjust = faces_that_have_been_found[1]
                    adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_vertex)
            else:
                self.logger.error("Unexpected condition. Mario you'd better go back to paper (1)")
                exit(-1)

            # Adjust the list of faces
            # The else case it to have the ocean always as the last face
            if (g_faces.index(face_to_adjust) == (len(g_faces) - 1)):
                if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("HERE (1) - %d - %d", g_faces.index(face_to_adjust), (len(g_faces) - 1))
                g_faces.remove(face_to_adjust)
                g_faces.append(adjusted_face)
            else:
                if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("HERE (2) - %d - %d", g_faces.index(face_to_adjust), (len(g_faces) - 1))
                g_faces.remove(face_to_adjust)
                g_faces.insert(-1, adjusted_face)

            ####
            # STEP: Adjust the second face. See drawing: 07/Apr/2018, pag 1
            ####
            #
            # Edge to find: in case of the new edge starts and ends at the same edge ... and since I've already updated the face, I'll adjust the search accordingly
            if (index_of_the_first_selected_edge == index_of_the_second_selected_edge):
                edge_to_find = (second_selected_edge[1], i_vertex)
            else:
                edge_to_find = self.rotate(second_selected_edge, 1)

            # Search the map
            faces_that_have_been_found = [face for face in g_faces if edge_to_find in face]

            # There is a particular case here to consider. If the starting face was a F2 and if the new edge starts and ends at the same edge
            #
            # if (len(selected_face) == 2):
            if ((len(selected_face) == 2) and (index_of_the_first_selected_edge != index_of_the_second_selected_edge)):
                if selected_face in faces_that_have_been_found:
                    faces_that_have_been_found.remove(selected_face)

            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("edge_to_find = %s, faces_that_have_been_found = %s", edge_to_find, faces_that_have_been_found)

            # Depending on the situation, some checks need to be done: same as above, but with vertex number = (i_vertex + 1)
            if (len(faces_that_have_been_found) == 1):
                face_to_adjust = faces_that_have_been_found[0]
                adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex + 1)
            elif (len(faces_that_have_been_found) == 2):
                if (len(faces_that_have_been_found[0]) == 2):
                    face_to_adjust = faces_that_have_been_found[0]
                    adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[0], edge_to_find, i_vertex + 1)
                else:
                    face_to_adjust = faces_that_have_been_found[1]
                    adjusted_face = self._add_vertex_to_face(faces_that_have_been_found[1], edge_to_find, i_vertex + 1)
            else:
                self.logger.error("Unexpected condition. Mario you'd better go back to paper (2)")
                exit(-1)

            # Adjust the list of faces
            if (g_faces.index(face_to_adjust) == (len(g_faces) - 1)):
                g_faces.remove(face_to_adjust)
                g_faces.append(adjusted_face)
            else:
                g_faces.remove(face_to_adjust)
                g_faces.insert(-1, adjusted_face)

            # Adjust the list of all faces
            # Insert is used to leave the ocean as the last face
            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("remove the selected face = %s", selected_face)
            if self.logger.isEnabledFor(logging.DEBUG): self.logger.debug("new fases = %s, %s", the_two_new_faces[0], the_two_new_faces[1])
            g_faces.remove(selected_face)
            g_faces.insert(-1, the_two_new_faces[0])
            g_faces.insert(-1, the_two_new_faces[1])

            # Let's move to the next face (a new edge introduces 2 additional vertices, and 3 additional edges)
            i_face += 1
            i_vertex += 2

            # Logging time
            if self.logger.isEnabledFor(logging.DEBUG): self._log_faces(g_faces)
            if (i_face % 1000) == 0:
                now = perf_counter()
                delta = now - last_log_time
                if self.logger.isEnabledFor(logging.INFO): self.logger.info("Loop: %s (%.3f s)", i_face, delta)
                last_log_time = now

        # Return the generated faces so caller can use them
        return g_faces


def main():
    try:
        # Parse the arguments
        args = parse_args()

        # Setup logging
        logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

        # Create the planar graph
        generator = PlanarGraphGenerator()
        g_faces = generator.generate(args.faces)

        # Save to file if requested
        if args.output is not None:
            save_to_file(g_faces, args.output)

        # Print statistics
        generator.print_map_statistics(g_faces)

        # Print the planar graph
        logging.info("Planar graph: %s", g_faces)
    except ValueError as value_error:
        logging.error("Error: %s", value_error)
        sys.exit(2)
    except Exception as exception:
        logging.exception("Unexpected error: %s", exception)
        sys.exit(1)


if __name__ == "__main__":

    logger = logging.getLogger()
    main()
