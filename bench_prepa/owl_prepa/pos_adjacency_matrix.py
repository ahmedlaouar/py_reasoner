import numpy as np
import networkx as nx

def random_dag(vertex_count, edge_count):
    if edge_count >= vertex_count * (vertex_count - 1) / 2:
        raise ValueError("Invalid input: edgeCount must be less than vertexCount*(vertexCount-1)/2.")

    elems = np.random.permutation(np.pad(np.ones(edge_count), (0, vertex_count * (vertex_count - 1) // 2 - edge_count)))
    adjacency_matrix = np.tril(np.array([np.roll(elems, i) for i in range(vertex_count - 1)]), -1)
    
    return nx.DiGraph(adjacency_matrix)

# This Python function uses NumPy for array operations and NetworkX for graph representation. 
# It generates a random directed acyclic graph (DAG) with the specified number of vertices (vertex_count) and edges (edge_count). 
# The function ensures that edge_count is less than the maximum possible number of edges in a complete graph with vertex_count vertices. 
# The resulting graph is represented as a directed graph using NetworkX.