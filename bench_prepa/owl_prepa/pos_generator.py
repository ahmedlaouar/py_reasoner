import random
import sys

sys.setrecursionlimit(10000)

def generate_random_dag(num_nodes):
    graph = {}

    for i in range(num_nodes):
        graph[i] = []

        for j in range(i+1, num_nodes):
            if random.random() < 0.1 :
                graph[i].append(j)

    return graph

def dfs(graph, start, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(start)
    path.append(start)

    for next_node in graph[start]:
        if next_node not in visited:
            dfs(graph, next_node, visited, path)

    return visited

def find_indirect_links(graph):
    all_links = {}
    for node in graph:
        # Subtract 1 to exclude the node itself from its indirect links
        all_links[node] = dfs(graph, node) - {node}
    return all_links

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            # Add unvisited adjacent nodes; reverse is used to maintain order similar to recursion
            stack.extend(reversed([node for node in graph[vertex] if node not in visited]))
    return visited

def find_indirect_links_iterative(graph):
    indirect_links = {}
    for node in graph:
        # Subtract 1 to exclude the node itself from its indirect links
        indirect_links[node] = dfs_iterative(graph, node) - {node}
    return indirect_links

def save_dag_to_file(graph, filename):
    with open(filename, 'w') as file:
        for element in graph:
            to_write = [str(x) for x in graph[element]]
            if len(to_write) == 0:
                pos_line = str(element)+" \n"
            else:
                pos_line = str(element)+" "+" ".join(to_write)+" \n"
            file.write(pos_line)

if __name__ == '__main__':
    # Generate a random DAG with "50", "500", "1000", "10000" nodes
    num_nodes = 1000
    dag = generate_random_dag(num_nodes)
    all_links = find_indirect_links(dag)
    # Save DAG to a text file
    save_dag_to_file(all_links, "bench_prepa/dataset.01/pos1000.txt")
    print("DAG saved to bench_prepa/dataset.01/pos1000.txt")