import random

def generate_consistent_aboxes(input_file, output_file, size):
    """A simple function to get only consistent parts of an ABox for tests."""
    with open(input_file, 'r', encoding='utf-8') as infile:
        reservoir = []

        for i, line in enumerate(infile):
            if i < size:
                reservoir.append(line)
            else:
                j = random.randint(0, i)
                if j < size:
                    reservoir[j] = line

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(reservoir)

    return len(reservoir)

if __name__ == '__main__':

    for size in [1000, 10000, 50000, 100000]:

        input_file = 'dataset_preparation/instance-types_lang=en_specific_with_timestamps.csv'
        output_file = f'dataset_preparation/it_{size}.csv'
        sampled_count = generate_consistent_aboxes(input_file, output_file, size) 

        print(f"Sampled {sampled_count} rows.")