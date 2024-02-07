def read_pos(file_path :str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        pos_dict = {}
        for line in lines:
            tokens = [token for token in line.split()]
            weight = int(tokens[0])
            successors = [int(x) for x in tokens[1:]]
            pos_dict[weight] = successors
    return pos_dict

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
    input_filename = "bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos5000_prob_0.5.txt"
    output_filename = "bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos5000_prob_0.5.txt"
    incomplete_graph = read_pos(input_filename)
    graph = find_indirect_links_iterative(incomplete_graph)

    # Save DAG to a text file
    save_dag_to_file(graph, output_filename)
    print(f"DAG saved to {output_filename}")