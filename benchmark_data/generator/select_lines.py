import random

common_path = "benchmark_data/data/"
# Path to the input and output files
input_file_path = 'pre_dataset.txt'
output_file_path = 'dataset_meduim.txt'

# Read all lines from the input file
with open(common_path+input_file_path, 'r') as input_file:
    lines = input_file.readlines()

# Randomly select 50,000 lines
random_lines = random.sample(lines, k=50000)

# Write the randomly selected lines to the output file
with open(common_path+output_file_path, 'w') as output_file:
    output_file.writelines(random_lines)
