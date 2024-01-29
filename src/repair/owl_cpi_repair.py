import sqlite3
import time
from repair.owl_assertions_generator import generate_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_supports import compute_supports

def read_pos(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        n = len(lines)

        # Create an n x n matrix of zeros
        pos_matrix = [[0 for _ in range(n+1)] for _ in range(n+1)]

        # Assign 1 to specific indices
        for line in lines:
            splitted = line.split(";")
            weight = int(splitted[0])
            successors = [int(x) for x in splitted[1:-1]]
            
            for successor in successors:
                pos_matrix[weight][successor] = 1

    return pos_matrix

def is_strictly_preferred(pos_mat, support, conflict_member) -> bool:
    # a test if support is strictly preferred to conflict_member
    if pos_mat[support[2]][conflict_member[2]] == 1 and pos_mat[conflict_member[2]][support[2]] != 1:
        return True

def compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str):
    
    # read pos set from file
    pos = read_pos(pos_path)
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    try:
        # first, generate the possible assertions of (cl(ABox))
        # returns a list of dl_lite.assertion.w_assertion
        start_time = time.time()
        all_assertions = generate_assertions(ontology_path,cursor)
        inter_time0 = time.time()
        print(f"Number of the generated assertions = {len(all_assertions)}")
        print(f"Time to compute the conflicts: {inter_time0 - start_time}")

        # compute the conflicts 
        # conflicts are of the form (table1name, id, degree),(table2name, id, degree)
        conflicts = compute_conflicts(ontology_path,cursor)
        inter_time1 = time.time()
        print(f"Size of the conflicts = {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")

        cpi_repair = []
        # browse assertions and compute supports
        # returns a list of supports with the form (table_name,id,degree)
        for assertion in all_assertions:
            accepted = True
            supports = compute_supports(assertion,ontology_path,cursor)
            #if all(any(is_strictly_preferred(pos, support, conflict_member) for support in supports for conflict_member in conflict) for conflict in conflicts):
            #    cpi_repair.append(assertion)
            for conflict in conflicts:
                conflict_supported = False
                for support in supports:
                    if is_strictly_preferred(pos, support, conflict[0]) or is_strictly_preferred(pos, support, conflict[1]):
                        conflict_supported = True
                        break
                if not conflict_supported:
                    accepted = False
                    break
            if accepted :
                cpi_repair.append(assertion)
        inter_time2 = time.time()
        print(f"Size of the cpi_repair = {len(cpi_repair)}")
        print(f"Time to compute the cpi_repair: {inter_time2 - inter_time1}")

    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")