#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import time
from collections import defaultdict
import math
import os
from datetime import datetime
import argparse

class PlanarGraphBuilder:
    def __init__(self, target_faces=100, pause_duration=0.5):
        self.target_faces = target_faces
        self.pause_duration = pause_duration
        self.G = nx.MultiGraph()
        self.pos = {}
        self.step_count = 0
        self.vertex_counter = 2
        self.face_count = 3  # Start with 3 faces (including outer face)
        
        # Initialize the starting graph
        self._create_initial_graph()
        
    def _create_initial_graph(self):
        """Create the initial graph with 2 vertices and 3 parallel edges"""
        # Add vertices
        self.G.add_node(1)
        self.G.add_node(2)
        
        # Add three parallel edges
        self.G.add_edge(1, 2, key=0)
        self.G.add_edge(1, 2, key=1) 
        self.G.add_edge(1, 2, key=2)
        
        # Set initial positions
        self.pos[1] = (-1, 0)
        self.pos[2] = (1, 0)
        
    def _get_planar_faces(self):
        """Get actual faces from planar embedding"""
        # Special case for initial graph with 3 parallel edges
        if len(self.G.nodes()) == 2 and len(self.G.edges()) == 3:
            # 3 parallel edges between nodes 1,2 create 3 faces
            edge_list = list(self.G.edges(keys=True))
            print(f"DEBUG: Initial graph - found {len(edge_list)} edges: {edge_list}")
            return [
                [edge_list[0]],  # Face 1 (bounded by first edge)
                [edge_list[1]],  # Face 2 (bounded by second edge)  
                [edge_list[2]]   # Face 3 (bounded by third edge)
            ]
        
        # For more complex graphs, use fallback detection
        return self._fallback_face_detection()
    
    def _fallback_face_detection(self):
        """Fallback face detection for non-planar or problematic graphs"""
        # Special handling for multi-edges - each parallel edge creates its own "face"
        edge_groups = defaultdict(list)
        for u, v, key in self.G.edges(keys=True):
            pair = (min(u, v), max(u, v))
            edge_groups[pair].append((u, v, key))
        
        # Create pseudo-faces from individual edges or edge groups
        faces = []
        for pair, edges in edge_groups.items():
            if len(edges) >= 2:  # Multiple edges between same vertices
                # Each parallel edge becomes its own face
                for edge in edges:
                    faces.append([edge])
            else:
                # Single edge becomes a face
                faces.append(edges)
        
        print(f"DEBUG: Fallback detection found {len(faces)} faces")
        return faces

    def _choose_random_face_and_edges(self):
        """Choose a random face and two random edges from that face"""
        faces = self._get_planar_faces()
        
        print(f"DEBUG: Found {len(faces) if faces else 0} faces")
        if faces:
            print(f"DEBUG: First face: {faces[0]}")
        
        if not faces:
            print("No faces available for selection")
            return None, None, None
        
        # Choose a random face with uniform probability
        chosen_face = random.choice(faces)
        
        # Get edges of the chosen face - simplified logic for our use case
        face_edges = chosen_face  # Since our faces are already lists of edges
        
        if len(face_edges) < 1:
            print("No valid edges found in selected face")
            return None, None, None
        
        # Choose two edges uniformly at random (with replacement)
        edge1 = random.choice(face_edges)
        edge2 = random.choice(face_edges)
        
        return chosen_face, edge1, edge2

    def _subdivide_edge_once(self, u, v, key):
        """Subdivide an edge once by adding one new vertex"""
        # Verify edge exists before trying to remove it
        if not self.G.has_edge(u, v, key):
            print(f"Warning: Edge {u}-{v} with key {key} not found")
            return None, None, None
            
        self.vertex_counter += 1
        new_vertex = self.vertex_counter
        
        # Calculate position for new vertex (midpoint with small random offset)
        pos_u = np.array(self.pos[u])
        pos_v = np.array(self.pos[v])
        midpoint = (pos_u + pos_v) / 2

        # Add small random offset to avoid overlapping vertices
        offset = 0  # No offset; place new vertex exactly at midpoint
        self.pos[new_vertex] = (midpoint + offset).tolist()
        
        # Remove old edge
        self.G.remove_edge(u, v, key)
        
        # Get next available keys
        all_keys = [k for _, _, k in self.G.edges(keys=True)]
        next_key = max(all_keys, default=-1) + 1
        
        # Add two new edges
        self.G.add_edge(u, new_vertex, key=next_key)
        self.G.add_edge(new_vertex, v, key=next_key + 1)
        
        return new_vertex, next_key, next_key + 1
    
    def _subdivide_edge_twice(self, u, v, key):
        """Subdivide an edge twice by adding two new vertices"""
        # Verify edge exists before trying to remove it
        if not self.G.has_edge(u, v, key):
            print(f"Warning: Edge {u}-{v} with key {key} not found")
            return None, None, None, None, None, None
            
        self.vertex_counter += 2
        new_vertex1 = self.vertex_counter - 1
        new_vertex2 = self.vertex_counter
        
        # Calculate positions for new vertices (divide edge into thirds)
        pos_u = np.array(self.pos[u])
        pos_v = np.array(self.pos[v])
        
        # Position new vertices with slight perpendicular offset to create visible separation
        direction = pos_v - pos_u
        if np.linalg.norm(direction) > 0:
            perpendicular = np.array([-direction[1], direction[0]])
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            offset = perpendicular * 0.1  # Small perpendicular offset
        else:
            offset = np.array([0.1, 0.1])
        
        self.pos[new_vertex1] = (pos_u + (pos_v - pos_u) / 3 + offset * 0.5).tolist()
        self.pos[new_vertex2] = (pos_u + 2 * (pos_v - pos_u) / 3 + offset * 0.5).tolist()
        
        # Remove old edge
        self.G.remove_edge(u, v, key)
        
        # Get next available keys
        all_keys = [k for _, _, k in self.G.edges(keys=True)]
        next_key = max(all_keys, default=-1) + 1
        
        # Add three edges for the subdivided original edge
        self.G.add_edge(u, new_vertex1, key=next_key)
        self.G.add_edge(new_vertex1, new_vertex2, key=next_key + 1)
        self.G.add_edge(new_vertex2, v, key=next_key + 2)
        
        # Connect the two new vertices (this creates the face division)
        self.G.add_edge(new_vertex1, new_vertex2, key=next_key + 3)
        
        return new_vertex1, new_vertex2, next_key, next_key + 1, next_key + 2, next_key + 3
    
    def _perform_iteration_step(self):
        """Perform one iteration of the algorithm"""
        if self.face_count >= self.target_faces:
            return False
            
        self.step_count += 1
        
        # Step 1: Choose a random face and two random edges
        face, edge1, edge2 = self._choose_random_face_and_edges()
        
        if face is None:
            print("No valid face/edge selection available")
            return False
        
        print(f"Step {self.step_count}: Chosen face with {len(face) if hasattr(face, '__len__') else 'unknown'} elements")
        print(f"  Selected edges: {edge1}, {edge2}")
        
        # Step 3: Subdivide edges based on whether they're the same or different
        if edge1 == edge2:
            # Same edge chosen twice: subdivide in three parts and connect new vertices
            u, v, key = edge1
            result = self._subdivide_edge_twice(u, v, key)
            if result[0] is not None:
                print(f"  Subdivided edge {edge1} twice, added vertices {result[0]} and {result[1]}")
            else:
                return True  # Continue but skip this step
        else:
            # Different edges: subdivide each once and connect new vertices
            u1, v1, key1 = edge1
            u2, v2, key2 = edge2
            
            new_v1, _, _ = self._subdivide_edge_once(u1, v1, key1)
            if new_v1 is None:
                return True  # Continue but skip this step
                
            new_v2, _, _ = self._subdivide_edge_once(u2, v2, key2)
            if new_v2 is None:
                return True  # Continue but skip this step
            
            # Position the connecting edge to create a visible face
            pos1 = np.array(self.pos[new_v1])
            pos2 = np.array(self.pos[new_v2])
            
            # Adjust positions slightly to make the new face more visible
            rng = np.random.default_rng(42)
            center_offset = rng.normal(0, 0.08, 2)
            
            self.pos[new_v1] = (pos1 + center_offset * 0.5).tolist()
            self.pos[new_v2] = (pos2 + center_offset * 0.5).tolist()
            
            # Connect the two new vertices
            all_keys = [k for _, _, k in self.G.edges(keys=True)]
            connect_key = max(all_keys, default=-1) + 1
            self.G.add_edge(new_v1, new_v2, key=connect_key)
            
            print(f"  Subdivided edges {edge1} and {edge2}, added vertices {new_v1} and {new_v2}")
        
        # Step 4: Increment face count (each operation adds exactly one face)
        self.face_count += 1
        
        return True
    
    def _apply_spring_layout_adjustment(self):
        """Apply a spring layout to improve the visual appearance while maintaining structure"""
        # Use NetworkX spring layout but initialize with current positions
        try:
            # Create a simple graph for layout computation (remove multi-edges)
            simple_G = nx.Graph()
            for u, v in self.G.edges():
                simple_G.add_edge(u, v)
            
            # Apply spring layout with current positions as starting point
            new_pos = nx.spring_layout(simple_G, pos=self.pos, iterations=20, k=0.5, scale=2)
            
            # Update positions
            for node in new_pos:
                self.pos[node] = new_pos[node]
                
        except Exception as e:
            # If spring layout fails, keep current positions
            pass
    
    def _draw_multigraph(self, ax):
        """Draw the multigraph with separated parallel edges and better planar layout"""
        ax.clear()
        
        if not self.G.nodes():
            return
        
        # Apply spring layout adjustment every few steps for better visualization
        if self.step_count % 3 == 0 and self.step_count > 0:
            self._apply_spring_layout_adjustment()
            
        # Draw nodes
        node_positions = [self.pos[node] for node in self.G.nodes()]
        node_x = [pos[0] for pos in node_positions]
        node_y = [pos[1] for pos in node_positions]
        
        # Use different colors for different node types
        node_colors = []
        node_sizes = []
        for node in self.G.nodes():
            if node <= 2:  # Original vertices
                node_colors.append('red')
                node_sizes.append(400)
            else:  # Added vertices
                node_colors.append('lightblue')
                node_sizes.append(200)
        
        ax.scatter(node_x, node_y, c=node_colors, s=node_sizes, zorder=3, alpha=0.8, edgecolors='black', linewidths=1)
        
        # Label nodes
        for node, (x, y) in self.pos.items():
            ax.annotate(str(node), (x, y), xytext=(0, 0), 
                       textcoords='offset points', ha='center', va='center',
                       fontsize=7, fontweight='bold', zorder=4, color='white' if node <= 2 else 'black')
        
        # Draw edges with better separation for parallel edges
        edge_counts = defaultdict(int)
        for u, v in self.G.edges():
            edge_counts[(min(u,v), max(u,v))] += 1
        
        edge_drawn = defaultdict(int)
        
        # Draw edges with different colors and styles
        for u, v, key in self.G.edges(keys=True):
            u_pos = np.array(self.pos[u])
            v_pos = np.array(self.pos[v])
            
            # Calculate perpendicular offset for parallel edges
            edge_key = (min(u,v), max(u,v))
            total_edges = edge_counts[edge_key]
            edge_num = edge_drawn[edge_key]
            edge_drawn[edge_key] += 1
            
            # Choose edge color based on recency (newer edges are more colorful)
            edge_colors = ['black', 'blue', 'green', 'orange', 'purple', 'brown']
            edge_color = edge_colors[min(key % len(edge_colors), len(edge_colors)-1)]
            edge_alpha = 0.7
            edge_width = 1.5
            
            if total_edges > 1:
                # Create offset for parallel edges
                direction = v_pos - u_pos
                if np.linalg.norm(direction) > 0.001:  # Avoid division by zero
                    perpendicular = np.array([-direction[1], direction[0]])
                    perpendicular = perpendicular / np.linalg.norm(perpendicular)
                    
                    # Spread edges symmetrically
                    offset_distance = min(0.2, np.linalg.norm(direction) * 0.3)
                    if total_edges == 2:
                        offsets = [-0.7, 0.7]
                    elif total_edges == 3:
                        offsets = [-1, 0, 1]
                    elif total_edges == 4:
                        offsets = [-1.5, -0.5, 0.5, 1.5]
                    else:
                        offsets = np.linspace(-2, 2, total_edges)
                    
                    offset = offsets[edge_num] * offset_distance * perpendicular
                    
                    # Create curved path using quadratic Bezier curve
                    control_point = (u_pos + v_pos) / 2 + offset
                    
                    # Draw curved edge
                    t = np.linspace(0, 1, 30)
                    curve_points = []
                    for t_val in t:
                        point = (1-t_val)**2 * u_pos + 2*(1-t_val)*t_val * control_point + t_val**2 * v_pos
                        curve_points.append(point)
                    
                    curve_points = np.array(curve_points)
                    ax.plot(curve_points[:, 0], curve_points[:, 1], 
                           color=edge_color, alpha=edge_alpha, linewidth=edge_width, zorder=1)
                else:
                    # Fallback for very short edges
                    ax.plot([u_pos[0], v_pos[0]], [u_pos[1], v_pos[1]], 
                           color=edge_color, alpha=edge_alpha, linewidth=edge_width, zorder=1)
            else:
                # Straight line for single edges
                ax.plot([u_pos[0], v_pos[0]], [u_pos[1], v_pos[1]], 
                       color=edge_color, alpha=edge_alpha, linewidth=edge_width, zorder=1)
        
        ax.set_title(f'Step {self.step_count}: {self.face_count} faces, {len(self.G.nodes())} vertices, {len(self.G.edges())} edges', fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Adjust plot limits to show all nodes with padding
        if node_x and node_y:
            margin = 0.8
            ax.set_xlim(min(node_x) - margin, max(node_x) + margin)
            ax.set_ylim(min(node_y) - margin, max(node_y) + margin)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', label='Original vertices'),
            Patch(facecolor='lightblue', label='Added vertices'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    def save_graph_for_gephi(self, base_filename=None, output_dir="./graphs"):
        """Save the graph in multiple formats compatible with Gephi"""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename if not provided
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"planar_graph_{self.face_count}faces_{timestamp}"
        
        # Convert MultiGraph to Graph for better Gephi compatibility
        simple_graph = self._convert_to_simple_graph()
        
        # Prepare node and edge attributes for Gephi
        self._prepare_graph_attributes(simple_graph)
        
        saved_files = []
        
        try:
            # Save as GEXF (recommended for Gephi)
            gexf_path = os.path.join(output_dir, f"{base_filename}.gexf")
            nx.write_gexf(simple_graph, gexf_path)
            saved_files.append(gexf_path)
            print(f"Saved GEXF file: {gexf_path}")
        except Exception as e:
            print(f"Error saving GEXF: {e}")
        
        try:
            # Save as GraphML (alternative for Gephi)
            graphml_path = os.path.join(output_dir, f"{base_filename}.graphml")
            nx.write_graphml(simple_graph, graphml_path)
            saved_files.append(graphml_path)
            print(f"Saved GraphML file: {graphml_path}")
        except Exception as e:
            print(f"Error saving GraphML: {e}")
        
        try:
            # Save as GML (simple format)
            gml_path = os.path.join(output_dir, f"{base_filename}.gml")
            nx.write_gml(simple_graph, gml_path)
            saved_files.append(gml_path)
            print(f"Saved GML file: {gml_path}")
        except Exception as e:
            print(f"Error saving GML: {e}")
        
        try:
            # Save edge list with positions as CSV for manual import
            csv_path = os.path.join(output_dir, f"{base_filename}_edges.csv")
            self._save_edge_list_csv(simple_graph, csv_path)
            saved_files.append(csv_path)
            print(f"Saved CSV edge list: {csv_path}")
        except Exception as e:
            print(f"Error saving CSV: {e}")
        
        # Save node positions separately
        try:
            pos_path = os.path.join(output_dir, f"{base_filename}_positions.csv")
            self._save_positions_csv(pos_path)
            saved_files.append(pos_path)
            print(f"Saved positions CSV: {pos_path}")
        except Exception as e:
            print(f"Error saving positions CSV: {e}")
        
        # Save graph statistics
        try:
            stats_path = os.path.join(output_dir, f"{base_filename}_stats.txt")
            self._save_graph_statistics(stats_path)
            saved_files.append(stats_path)
            print(f"Saved statistics: {stats_path}")
        except Exception as e:
            print(f"Error saving statistics: {e}")
        
        return saved_files
    
    def _convert_to_simple_graph(self):
        """Convert MultiGraph to simple Graph for Gephi compatibility"""
        simple_G = nx.Graph()
        
        # Add all nodes with their positions
        for node in self.G.nodes():
            simple_G.add_node(node)
        
        # Add edges (collapse multiple edges between same nodes)
        edge_weights = defaultdict(int)
        for u, v, key in self.G.edges(keys=True):
            edge_weights[(u, v)] += 1
        
        for (u, v), weight in edge_weights.items():
            simple_G.add_edge(u, v, weight=weight, multiplicity=weight)
        
        return simple_G
    
    def _prepare_graph_attributes(self, graph):
        """Add node and edge attributes for better visualization in Gephi"""
        
        # Node attributes
        for node in graph.nodes():
            # Node type (original vs added)
            node_type = "original" if node <= 2 else "added"
            graph.nodes[node]['type'] = node_type
            
            # Position coordinates
            if node in self.pos:
                graph.nodes[node]['x'] = float(self.pos[node][0])
                graph.nodes[node]['y'] = float(self.pos[node][1])
                graph.nodes[node]['z'] = 0.0  # 2D graph
            
            # Node size based on degree
            degree = graph.degree(node)
            graph.nodes[node]['degree'] = degree
            graph.nodes[node]['size'] = max(10, degree * 5)
            
            # Color based on type
            if node_type == "original":
                graph.nodes[node]['color'] = "red"
                graph.nodes[node]['r'] = 255
                graph.nodes[node]['g'] = 0
                graph.nodes[node]['b'] = 0
            else:
                graph.nodes[node]['color'] = "lightblue"
                graph.nodes[node]['r'] = 173
                graph.nodes[node]['g'] = 216
                graph.nodes[node]['b'] = 230
        
        # Edge attributes
        for u, v, data in graph.edges(data=True):
            # Edge weight (number of original parallel edges)
            weight = data.get('weight', 1)
            graph.edges[u, v]['weight'] = weight
            graph.edges[u, v]['thickness'] = min(5, weight)
            
            # Edge color based on weight
            if weight == 1:
                graph.edges[u, v]['color'] = "gray"
            elif weight == 2:
                graph.edges[u, v]['color'] = "blue"
            else:
                graph.edges[u, v]['color'] = "red"
    
    def _save_edge_list_csv(self, graph, filepath):
        """Save edge list as CSV file"""
        with open(filepath, 'w') as f:
            f.write("Source,Target,Weight,Type\n")
            for u, v, data in graph.edges(data=True):
                weight = data.get('weight', 1)
                edge_type = "multiple" if weight > 1 else "single"
                f.write(f"{u},{v},{weight},{edge_type}\n")
    
    def _save_positions_csv(self, filepath):
        """Save node positions as CSV file"""
        with open(filepath, 'w') as f:
            f.write("NodeID,X,Y,Type\n")
            for node, pos in self.pos.items():
                node_type = "original" if node <= 2 else "added"
                f.write(f"{node},{pos[0]},{pos[1]},{node_type}\n")
    
    def _save_graph_statistics(self, filepath):
        """Save detailed graph statistics"""
        # Get analysis results
        analysis = self.check_graph_properties()
        
        with open(filepath, 'w') as f:
            f.write("Planar Graph Statistics\n")
            f.write("=======================\n\n")
            f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target Faces: {self.target_faces}\n")
            f.write(f"Steps Performed: {self.step_count}\n\n")
            
            f.write("Graph Properties:\n")
            f.write(f"- Vertices (V): {analysis['num_vertices']}\n")
            f.write(f"- Edges (E): {analysis['num_edges']}\n")
            f.write(f"- Faces (F): {analysis['num_faces']}\n")
            f.write(f"- Connected: {analysis['is_connected']}\n")
            f.write(f"- Components: {analysis['num_components']}\n")
            
            # Planarity
            f.write(f"\nPlanarity Analysis:\n")
            f.write(f"- Is Planar: {analysis['is_planar']}\n")
            if not analysis['is_planar'] and analysis['planarity_counterexample']:
                f.write(f"- Kuratowski Subgraph: {list(analysis['planarity_counterexample'].edges())}\n")
            
            # Euler characteristic
            f.write(f"\nEuler's Formula (V - E + F = 2):\n")
            f.write(f"- Euler Characteristic: {analysis['euler_characteristic']}\n")
            f.write(f"- Valid for Planar Graph: {analysis['euler_valid']}\n")
            
            # Regularity
            f.write(f"\nRegularity Analysis:\n")
            f.write(f"- Is 3-Regular: {analysis['is_3_regular']}\n")
            f.write(f"- Degree Range: {analysis['degree_distribution']['min']} - {analysis['degree_distribution']['max']}\n")
            f.write(f"- Unique Degrees: {analysis['degree_distribution']['unique_degrees']}\n")
            
            # Degree distribution
            degrees = [self.G.degree(node) for node in self.G.nodes()]
            f.write(f"\nDetailed Degree Distribution:\n")
            f.write(f"- Min degree: {min(degrees) if degrees else 0}\n")
            f.write(f"- Max degree: {max(degrees) if degrees else 0}\n")
            f.write(f"- Average degree: {np.mean(degrees) if degrees else 0:.2f}\n")
            
            # 4-coloring relevance
            f.write(f"\n4-Coloring Theorem Relevance:\n")
            if analysis['is_planar']:
                f.write(f"- 4-colorable: YES (planar graph)\n")
                if analysis['is_3_regular']:
                    f.write(f"- 3-colorable: YES (3-regular planar graph)\n")
                else:
                    f.write(f"- 3-colorable: UNKNOWN (not 3-regular)\n")
            else:
                f.write(f"- 4-colorable: UNKNOWN (not planar)\n")
            
            # Node types
            original_nodes = [n for n in self.G.nodes() if n <= 2]
            added_nodes = [n for n in self.G.nodes() if n > 2]
            f.write(f"\nNode Types:\n")
            f.write(f"- Original nodes: {len(original_nodes)} {original_nodes}\n")
            f.write(f"- Added nodes: {len(added_nodes)}\n")
            
            # Multi-edge information
            edge_multiplicities = defaultdict(int)
            for u, v in self.G.edges():
                edge_multiplicities[(min(u,v), max(u,v))] += 1
            
            f.write(f"\nEdge Multiplicities:\n")
            for mult in range(1, max(edge_multiplicities.values()) + 1 if edge_multiplicities else 1):
                count = sum(1 for m in edge_multiplicities.values() if m == mult)
                if count > 0:
                    f.write(f"- {count} edge pair(s) with {mult} parallel edge(s)\n")

    def check_graph_properties(self):
        """Check and report graph properties: planarity, regularity, connectivity"""
        results = {}
        
        # Convert to simple graph for planarity check
        simple_G = nx.Graph()
        for u, v in self.G.edges():
            if not simple_G.has_edge(u, v):
                simple_G.add_edge(u, v)
        
        # Check planarity on simple graph
        is_planar, counterexample = nx.check_planarity(simple_G, counterexample=True)
        results['is_planar'] = is_planar
        results['planarity_counterexample'] = counterexample if not is_planar else None
        
        # Check 3-regularity (all vertices have degree 3)
        degrees = dict(self.G.degree())
        degree_values = list(degrees.values())
        results['degrees'] = degrees
        results['is_3_regular'] = all(degree == 3 for degree in degree_values)
        results['degree_distribution'] = {
            'min': min(degree_values) if degree_values else 0,
            'max': max(degree_values) if degree_values else 0,
            'unique_degrees': sorted(set(degree_values))
        }
        
        # Check connectivity
        results['is_connected'] = nx.is_connected(self.G)
        results['num_components'] = nx.number_connected_components(self.G)
        
        # Additional graph properties
        results['num_vertices'] = len(self.G.nodes())
        results['num_edges'] = len(self.G.edges())
        results['num_faces'] = self.face_count
        
        # Euler characteristic
        V, E, F = results['num_vertices'], results['num_edges'], results['num_faces']
        results['euler_characteristic'] = V - E + F
        results['euler_valid'] = (V - E + F == 2)  # Should be 2 for connected planar graphs
        
        # Face distribution analysis
        try:
            faces = self._get_planar_faces()
            if faces:
                face_sizes = []
                for face in faces:
                    if isinstance(face[0], tuple):
                        # Fallback format
                        face_sizes.append(len(face))
                    else:
                        # Proper face format
                        face_sizes.append(len(face))
                
                results['face_sizes'] = face_sizes
                results['face_size_distribution'] = {
                    'min': min(face_sizes) if face_sizes else 0,
                    'max': max(face_sizes) if face_sizes else 0,
                    'avg': np.mean(face_sizes) if face_sizes else 0,
                    'unique_sizes': sorted(set(face_sizes))
                }
            else:
                results['face_sizes'] = []
                results['face_size_distribution'] = {'min': 0, 'max': 0, 'avg': 0, 'unique_sizes': []}
        except Exception as e:
            print(f"Error analyzing face sizes: {e}")
            results['face_sizes'] = []
            results['face_size_distribution'] = {'min': 0, 'max': 0, 'avg': 0, 'unique_sizes': []}
        
        return results
    
    def print_graph_analysis(self, results):
        """Print detailed analysis of graph properties"""
        print("\n" + "="*50)
        print("GRAPH PROPERTY ANALYSIS")
        print("="*50)
        
        # Basic properties
        print(f"Vertices (V): {results['num_vertices']}")
        print(f"Edges (E): {results['num_edges']}")
        print(f"Faces (F): {results['num_faces']}")
        print(f"Connected: {'✓' if results['is_connected'] else '✗'}")
        print(f"Components: {results['num_components']}")
        
        # Face analysis
        if 'face_size_distribution' in results:
            face_dist = results['face_size_distribution']
            print(f"\nFACE SIZE ANALYSIS:")
            print(f"Face count detected: {len(results.get('face_sizes', []))}")
            print(f"Face sizes: {face_dist['min']} - {face_dist['max']} (avg: {face_dist['avg']:.1f})")
            print(f"Unique face sizes: {face_dist['unique_sizes']}")
        
        # Planarity check
        print(f"\nPLANARITY CHECK:")
        if results['is_planar']:
            print("✓ Graph is PLANAR")
        else:
            print("✗ Graph is NOT PLANAR")
            if results['planarity_counterexample']:
                print(f"  Counterexample (Kuratowski subgraph): {list(results['planarity_counterexample'].edges())}")
        
        # Euler's formula check
        print(f"\nEULER'S FORMULA CHECK (V - E + F = 2):")
        euler_char = results['euler_characteristic']
        if results['euler_valid']:
            print(f"✓ Euler characteristic: {euler_char} = 2 (VALID)")
        else:
            print(f"✗ Euler characteristic: {euler_char} ≠ 2 (INVALID)")
            if results['is_planar'] and results['is_connected']:
                print("  Warning: Connected planar graph should have χ = 2")
        
        # 3-regularity check
        print(f"\n3-REGULARITY CHECK:")
        if results['is_3_regular']:
            print("✓ Graph is 3-REGULAR (all vertices have degree 3)")
        else:
            print("✗ Graph is NOT 3-regular")
            degrees = results['degrees']
            degree_dist = results['degree_distribution']
            print(f"  Degree range: {degree_dist['min']} - {degree_dist['max']}")
            print(f"  Unique degrees: {degree_dist['unique_degrees']}")
            
            # Show vertices that don't have degree 3
            non_regular = {v: d for v, d in degrees.items() if d != 3}
            if non_regular:
                print(f"  Vertices with degree ≠ 3: {dict(sorted(non_regular.items()))}")
        
        # Summary for 4-coloring relevance
        print(f"\n4-COLORING THEOREM RELEVANCE:")
        if results['is_planar']:
            print("✓ Graph is planar - 4-coloring theorem applies")
            if results['is_3_regular']:
                print("✓ Graph is 3-regular - additional constraints for coloring")
                print("  Note: 3-regular planar graphs are 3-colorable")
            else:
                print("  Graph is not 3-regular but still 4-colorable (planar)")
        else:
            print("✗ Graph is not planar - 4-coloring theorem does not apply")
            print("  Graph may require more than 4 colors")

    def run_algorithm(self, show_visualization=True, save_final=True, output_dir="./graphs"):
        """Run the complete algorithm with optional visualization and saving"""
        if show_visualization:
            plt.ion()
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Draw initial graph
            self._draw_multigraph(ax)
            plt.draw()
            plt.pause(self.pause_duration)
        
        print(f"Starting algorithm: Target = {self.target_faces} faces")
        print(f"Initial state: {self.face_count} faces, {len(self.G.nodes())} vertices, {len(self.G.edges())} edges")
        
        # Run iterations
        while self.face_count < self.target_faces:
            if not self._perform_iteration_step():
                break
                
            if show_visualization:
                self._draw_multigraph(ax)
                plt.draw()
                plt.pause(self.pause_duration)
            
            # Print progress every 5 steps
            if self.step_count % 5 == 0:
                print(f"Step {self.step_count}: {self.face_count} faces, {len(self.G.nodes())} vertices, {len(self.G.edges())} edges")
        
        print(f"\nAlgorithm completed!")
        print(f"Final state: {self.face_count} faces, {len(self.G.nodes())} vertices, {len(self.G.edges())} edges")
        print(f"Total steps: {self.step_count}")
        
        # Verify Euler's formula: V - E + F = 2 (for connected planar graph)
        V, E, F = len(self.G.nodes()), len(self.G.edges()), self.face_count
        euler_char = V - E + F
        print(f"Euler characteristic (V - E + F): {euler_char} (should be 2 for connected planar graph)")

        # Comprehensive graph property analysis
        analysis_results = self.check_graph_properties()
        self.print_graph_analysis(analysis_results)
        
        if show_visualization:
            self._draw_multigraph(ax)
            plt.title(f'Final Graph: {self.face_count} faces, {len(self.G.nodes())} vertices, {len(self.G.edges())} edges')
            plt.show()
        
        # Save the final graph
        if save_final:
            print(f"\nSaving final graph for Gephi...")
            saved_files = self.save_graph_for_gephi(output_dir=output_dir)
            print(f"Saved {len(saved_files)} files for Gephi import")
        
        return self.G, self.face_count, self.pos, analysis_results

def main():
    """Main function to run the planar graph builder"""
    parser = argparse.ArgumentParser(
        description="Generate a planar graph using face subdivision algorithm"
    )
    parser.add_argument(
        "target_faces",
        nargs="?",
        type=int,
        default=15,
        help="Target number of faces to generate (default: 15)"
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=1.0,
        help="Pause duration between visualization steps in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip visualization and run algorithm only"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip saving the final graph"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/python-tests/networkx/graphs",
        help="Output directory for saved graphs"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results"
    )
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    print("Planar Graph Builder")
    print("===================")
    print(f"Target faces: {args.target_faces}")
    print(f"Visualization: {'Disabled' if args.no_viz else 'Enabled'}")
    print(f"Save results: {'Disabled' if args.no_save else 'Enabled'}")
    if not args.no_save:
        print(f"Output directory: {args.output_dir}")
    print()
    
    # Create and run the algorithm
    builder = PlanarGraphBuilder(
        target_faces=args.target_faces, 
        pause_duration=args.pause
    )
    
    graph, final_faces, positions, analysis = builder.run_algorithm(
        show_visualization=not args.no_viz, 
        save_final=not args.no_save, 
        output_dir=args.output_dir
    )
    
    # Print final statistics
    print(f"\nFinal Graph Statistics:")
    print(f"- Vertices: {len(graph.nodes())}")
    print(f"- Edges: {len(graph.edges())}")
    print(f"- Faces: {final_faces}")
    print(f"- Planar: {'Yes' if analysis['is_planar'] else 'No'}")
    print(f"- 3-Regular: {'Yes' if analysis['is_3_regular'] else 'No'}")
    print(f"- 4-Colorable: {'Yes' if analysis['is_planar'] else 'Unknown'}")
    
    if not args.no_save:
        # Additional save option with custom filename
        print(f"\nFiles saved to: {args.output_dir}")
        print("You can now import these files into Gephi:")
        print("1. Use the .gexf file for best compatibility")
        print("2. Use the .graphml file as an alternative")
        print("3. The CSV files can be used for manual data import")

if __name__ == "__main__":
    main()