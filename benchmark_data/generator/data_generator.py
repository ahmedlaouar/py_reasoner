import random
import string

def generate_names(prefix, number):
    names = []
    for _ in range(number):
        name_length = random.randint(3, 10)
        name = ''.join(random.choices(string.ascii_lowercase, k=name_length))
        names.append('{}{}'.format(prefix, name))
    return names

def generate_ontology(tbox_file_path, num_lines, concepts, roles):
    generated_tbox = set()
    with open(tbox_file_path+".txt", 'w') as file:
        types = ['two_concepts', 'two_roles', 'concept_and_role']
        for _ in range(num_lines):
            combination_type = random.choice(types)
            random_number = random.random()
            if combination_type == 'two_concepts':
                combination = random.sample(concepts, 2)
                if random_number < 0.5:
                    line = '{} < NOT {}\n'.format(combination[0],combination[1])
                else:
                    line = '{} < {}\n'.format(combination[0],combination[1])
            elif combination_type == 'two_roles':
                combination = random.sample(roles, k=2)
                if random_number < 0.5:
                    line = '{} < NOT {}\n'.format(combination[0],combination[1])
                else:
                    line = '{} < {}\n'.format(combination[0],combination[1])
            else:
                combination = [random.choice(concepts), random.choice(roles)]
                if random_number < 0.2:
                    line = '{} < NOT EXISTS INV {}\n'.format(combination[0],combination[1])
                elif random_number < 0.5:
                    line = '{} < NOT EXISTS {}\n'.format(combination[0],combination[1])
                elif random_number < 0.7:
                    line = '{} < EXISTS INV {}\n'.format(combination[0],combination[1])
                else:
                    line = '{} < EXISTS {}\n'.format(combination[0],combination[1])
            if (combination[0],combination[1]) not in generated_tbox and (combination[1],combination[0]) not in generated_tbox:
                generated_tbox.add((combination[0],combination[1]))
                file.write(line)

def generate_dataset(abox_file_path, tbox_file_path, num_lines, Ni, Nc, Nr):
    individuals = generate_names("Ind",Ni)
    concepts = generate_names("Concept",Nc)
    roles = generate_names("Role",Nr)
    generated_lines = set()

    with open(abox_file_path+".txt", 'w') as file:
        for _ in range(num_lines):
            random_number = random.random()
            if random_number < 0.6:
                individual = random.choice(individuals)
                concept = random.choice(concepts)
                line = '{}({});\n'.format(concept, individual)
            else:
                individual1, individual2 = random.sample(individuals, 2)
                role = random.choice(roles)
                line = '{}({},{});\n'.format(role, individual1, individual2)
            
            if line not in generated_lines:
                generated_lines.add(line)
                file.write(line)

    t_lines = [num_lines//10000, num_lines//1000, num_lines//100]
    for i in range(len(t_lines)):
        generate_ontology(tbox_file_path+str(i), t_lines[i], concepts, roles)
    

common_path = "benchmark_data/data/"
abox_file_path = common_path+"dataset"
tbox_file_path = common_path+"ontology"
num_lines = 1000000
Ni = 1000
Nc = 500
Nr = 200
generate_dataset(abox_file_path, tbox_file_path, num_lines, Ni, Nc, Nr)


print('Dataset generated successfully.')