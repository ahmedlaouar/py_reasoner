import random
import networkx as nx

common_path = "benchmark_data/data/"

def generate_random_dag(num_nodes):
    graph = nx.DiGraph()

    for i in range(num_nodes):
        graph.add_node(i)

        for j in range(i + 1, num_nodes):
            if random.random() < 0.5:
                graph.add_edge(i, j)

    return graph

def save_dag_to_file(graph, filename):
    nx.write_edgelist(graph, filename)

def load_dag_from_file(filename):
    return nx.read_edgelist(filename, create_using=nx.DiGraph)

# Generate a random DAG with 10,000 nodes
num_nodes = 1000
dag = generate_random_dag(num_nodes)

# Save DAG to a text file
filename = "random_dag_2023053117.txt"
save_dag_to_file(dag, common_path+filename)
print("DAG saved to", filename)

# Load DAG from the text file
loaded_dag = load_dag_from_file(common_path+filename)
print("DAG loaded from", filename)

# Check if a link exists between two elements
"""source = 0
target = 9999
link_exists = nx.has_path(loaded_dag, source, target)

if link_exists:
    print(f"A link exists between {source} and {target}.")
else:
    print(f"No link exists between {source} and {target}.")
"""
dataset_name = "dataset_2023053117.txt"
weighted_lines = []
# Read the dataset from the file
with open(common_path+dataset_name, 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        weight = random.choice(range(num_nodes))
        weighted_lines.append(line+str(weight)+";\n")

# Write the partial order to a new file
with open(common_path+dataset_name, 'w') as file:
    for line in weighted_lines:
        file.write(line)