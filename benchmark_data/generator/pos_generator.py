
import random

common_path = "benchmark_data/data/"
# POS for Partially Ordered Set
def generate_pos(size):
    pos = [x for x in range(1,size+1)]
    pos_order = {}
    while len(pos)>0 :
        current = pos.pop(0)
        num_successors = random.randint(0, 5)  # Choose a random number of successors
        if len(pos) < num_successors:
            pos_order[current] = random.sample(pos, len(pos))
        else:    
            pos_order[current] = random.sample(pos, num_successors)
    return pos_order

pos_order = generate_pos(50)

weighted_lines = []
# Read the dataset from the file
with open(common_path+'dataset_small.txt', 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        weight = random.choice(list(pos_order.keys()))
        weighted_lines.append(line+str(weight)+";\n")

# Write the partial order to a new file
with open(common_path+'dataset_small.txt', 'w') as file:
    for line in weighted_lines:
        file.write(line)

with open(common_path+'pos_dataset_small.txt', 'w') as file:
    for element in pos_order:
        to_write = [str(x) for x in pos_order[element]]
        if len(to_write) == 0:
            pos_line = str(element)+';\n'
        else:
            pos_line = str(element)+";"+";".join(to_write)+';\n'
        file.write(pos_line)

