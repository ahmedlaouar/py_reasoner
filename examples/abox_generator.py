import random
import string

def generate_dataset(file_path, num_lines):
    elements = []
    individuals = set()

    with open(file_path, 'w') as file:
        for _ in range(num_lines):
            element = random.choice(['A', 'R'])
            elements.append(element)

            if element == 'A':
                concept = generate_name('Concept')
                individuals.add(concept)
                line = '{}({})\n'.format(concept, generate_individual())
            else:
                role = generate_name('Role')
                individuals.add(role)
                line = '{}({},{})\n'.format(role, generate_individual(), generate_individual())
            file.write(line)

    # Add more instances of existing names
    individuals = list(individuals)
    for _ in range(num_lines // 10):
        element = random.choice(elements)
        if element == 'A':
            concept = random.choice(individuals)
            line = '{}({})\n'.format(concept, generate_individual())
        else:
            role = random.choice(individuals)
            line = '{}({},{})\n'.format(role, generate_individual(), generate_individual())
        file.write(line)

def generate_name(prefix):
    name_length = random.randint(1, 10)
    name = ''.join(random.choices(string.ascii_lowercase, k=name_length))
    return '{}{}'.format(prefix, name)

def generate_individual():
    individual_length = random.randint(1, 10)
    individual = ''.join(random.choices(string.ascii_lowercase, k=individual_length))
    return individual

file_path = 'dataset.txt'
num_lines = 100#0000

generate_dataset(file_path, num_lines)
print('Dataset generated successfully.')
