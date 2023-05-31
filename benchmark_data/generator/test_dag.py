import networkx as nx

common_path = "benchmark_data/data/"

def load_dag_from_file(filename):
    return nx.read_edgelist(filename, create_using=nx.DiGraph)

filename = "random_dag_2023053117.txt"

# Load DAG from the text file
loaded_dag = load_dag_from_file(common_path+filename)
print("DAG loaded from", filename)

source = 1
target = 152
link_exists = nx.has_path(loaded_dag, source, target)

if link_exists:
    print(f"A link exists between {source} and {target}.")
else:
    print(f"No link exists between {source} and {target}.")