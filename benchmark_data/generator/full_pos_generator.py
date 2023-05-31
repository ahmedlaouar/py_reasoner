import random

common_path = "benchmark_data/data/"

def generate_random_dag(num_nodes):
    graph = {}

    for i in range(num_nodes):
        graph[i] = []

        for j in range(i + 1, num_nodes):
            if random.random() < 0.5:
                graph[i].append(j)

    return graph

def save_dag_to_file(graph, filename):
    with open(filename, 'w') as file:
        for element in graph:
            to_write = [str(x) for x in graph[element]]
            if len(to_write) == 0:
                pos_line = str(element)+';\n'
            else:
                pos_line = str(element)+";"+";".join(to_write)+';\n'
            file.write(pos_line)


# Generate a random DAG with 10,000 nodes
num_nodes = 1000
dag = generate_random_dag(num_nodes)
# Save DAG to a text file
filename = "random_dag_2023053117.txt"
save_dag_to_file(dag, common_path+filename)
print("DAG saved to", filename)