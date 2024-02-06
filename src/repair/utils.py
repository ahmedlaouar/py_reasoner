def read_pos(file_path :str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        pos_dict = {}
        for line in lines:
            tokens = [token for token in line.split()]
            weight = int(tokens[0])
            successors = [int(x) for x in tokens[1:]]
            pos_dict[weight] = successors
    return pos_dict