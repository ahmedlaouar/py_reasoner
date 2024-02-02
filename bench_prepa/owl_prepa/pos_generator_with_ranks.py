import random

def generate_DAG(nbr_nodes, min_per_rank, max_per_rank, p):
    graph = {}
    nodes = list(range(nbr_nodes))
    random.shuffle(nodes)
    while len(nodes) > 0:
        per_rank = random.randint(min_per_rank, max_per_rank)
        if len(nodes) <= per_rank:
            rank_nodes = nodes
        else:
            rank_nodes = random.choices(nodes, k=per_rank)
        nodes = [node for node in nodes if node not in rank_nodes]
        for sup_node in rank_nodes:
            graph[sup_node] = []
            for inf_node in nodes:
                if random.random() < p:
                    graph[sup_node].append(inf_node)
    return graph

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

def find_indirect_links(graph):
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

def main():
    NBR_NODES = 1000
    MIN_PER_RANK = NBR_NODES // 100  # Nodes/Rank: How 'fat' the DAG should be.
    MAX_PER_RANK = NBR_NODES // 10
    P = 0.9    # Chance of having an Edge.
    file_name = "bench_prepa/dataset.01/DAGs_with_ranks/pos_ranks_1000.txt"

    random.seed()  # Initialize the random number generator
    graph = generate_DAG(NBR_NODES, MIN_PER_RANK, MAX_PER_RANK, P)
    all_links = find_indirect_links(graph)
    # Save DAG to a text file
    
    save_dag_to_file(all_links, file_name)
    print(f"DAG saved to {file_name}")

if __name__ == "__main__":
    main()
