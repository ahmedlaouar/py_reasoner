import random

common_path = "benchmark_data/data/"

def generate_successors(current_value,total_lines):
    num_successors = random.randint(0, 10)  # Choose a random number of successors
    po_successors = random.sample(range(1, total_lines+1), num_successors) # Randomly select successors
    successors = list(filter(lambda a: a != current_value, po_successors))
    return successors

generated = {}
# Read the dataset from the file
with open(common_path+'dataset_micro.txt', 'r') as file:
    lines = file.read().splitlines()

    for i in range(len(lines)):
        successors = generate_successors(i+1,len(lines))
        generated[lines[i]] = [str(x) for x in successors]

# Write the partial order to a new file
with open(common_path+'dataset_micro.txt', 'w') as file:
    for line in lines:
        if len(generated[line]) == 0:
            successors_line = line+'\n'
        else:
            successors_line = line+';'.join(generated[line])+';\n'
        file.write(successors_line)
