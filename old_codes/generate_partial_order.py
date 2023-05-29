import random

def generate_successors(total_lines):
    num_successors = random.randint(0, total_lines//10)  # Choose a random number of successors
    successors = random.sample(range(1, total_lines+1), num_successors) # Randomly select successors
    return successors

generated = {}
# Read the dataset from the file
with open('examples/data_example.txt', 'r') as file:
    lines = file.read().splitlines()

    for line in lines:
        successors = generate_successors(len(lines))
        generated[line] = [str(x) for x in successors]

# Write the partial order to a new file
with open('examples/partial_order.txt', 'w') as file:
    for line in lines:
        if len(generated[line]) == 0:
            successors_line = line+';\n'
        else:
            successors_line = line+';'+';'.join(generated[line])+';\n'
        file.write(successors_line)
