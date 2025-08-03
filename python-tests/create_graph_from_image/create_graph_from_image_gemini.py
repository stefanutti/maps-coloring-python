import cv2
import numpy as np
import networkx as nx
import os

def create_graph_from_image(image_path):
    """Creates a graph from an image of lines."""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

        # Skeletonization
        kernel = np.ones((3,3),np.uint8)
        skeleton = np.zeros(thresh.shape,np.uint8)
        while True:
            eroded = cv2.erode(thresh,kernel)
            temp = cv2.dilate(eroded,kernel)
            temp = cv2.subtract(thresh,temp)
            skeleton = cv2.bitwise_or(skeleton,temp)
            thresh = eroded.copy()
            if cv2.countNonZero(thresh)==0:
                break

        # Find endpoints and junctions
        endpoints = []
        junctions = []
        for i in range(1, skeleton.shape[0] - 1):
            for j in range(1, skeleton.shape[1] - 1):
                if skeleton[i, j] == 255:
                    neighborhood = skeleton[i-1:i+2, j-1:j+2]
                    count = np.sum(neighborhood) - 1
                    if count == 1:
                        endpoints.append((j, i))
                    elif count > 2:
                        junctions.append((j, i))
        
        vertices = junctions + endpoints
        vertices = list(set(vertices)) # Remove duplicates

        graph = nx.Graph()
        for i, vertex in enumerate(vertices):
            graph.add_node(i, pos=vertex)

        # Connect vertices using flood fill
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                path_exists = find_path_on_skeleton(skeleton, vertices[i], vertices[j])
                if path_exists:
                    graph.add_edge(i, j)

        num_vertices = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        return graph, num_vertices, num_edges

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def find_path_on_skeleton(skeleton, start, end):
    """Checks if a path exists between two points using flood fill."""
    start_x, start_y = start
    end_x, end_y = end
    if skeleton[end_y, end_x] == 0:
        return False

    mask = np.zeros_like(skeleton, dtype=np.uint8)
    cv2.circle(mask, start, 1, 255, -1)

    cv2.floodFill(skeleton.copy(), mask, start, 255)

    if mask[end_y, end_x] == 255:
        return True
    return False

def save_graph_to_dot(graph, image_path):
    """Saves the graph to a dot file."""
    if graph is None:
        return

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    dot_filename = base_name + ".dot"
    nx.drawing.nx_pydot.write_dot(graph, dot_filename)
    print(f"Graph saved to {dot_filename}")
å
if __name__ == "__main__":
    
    image_file = "test-4ct-1.jpg"  # Replace with your image file
    result = create_graph_from_image(image_file)
    if result:
        graph, num_vertices, num_edges = result
        print(f"Number of vertices: {num_vertices}")
        print(f"Number of edges: {num_edges}")
        save_graph_to_dot(graph, image_file)
    else:
        print("Graph creation failed.")