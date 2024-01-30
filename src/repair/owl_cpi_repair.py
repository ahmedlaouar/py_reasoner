import sqlite3
import sys
import time
from repair.owl_assertions_generator import generate_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_supports import compute_all_supports
from multiprocessing import Pool

def read_pos(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        n = len(lines)

        # Create an n x n matrix of zeros
        pos_matrix = [[0 for _ in range(n+1)] for _ in range(n+1)]

        # Assign 1 to specific indices
        for line in lines:
            tokens = [token for token in line.split()]
            weight = int(tokens[0])
            successors = [int(x) for x in tokens[1:-1]]
            
            for successor in successors:
                pos_matrix[weight][successor] = 1

    return pos_matrix

def is_strictly_preferred(pos_mat, support, conflict_member) -> bool:
    # a test if support is strictly preferred to conflict_member
    if pos_mat[support][conflict_member[2]] == 1 and pos_mat[conflict_member[2]][support] != 1:
        return True

def print_progress_bar(iteration, total, bar_length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(bar_length * iteration // total)
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length - 1)

    sys.stdout.write('\rProgress: |%s| %s%%' % (bar, percent))
    sys.stdout.flush()

def check_assertion(args):
    i, all_assertions, conflicts, supports, pos = args
    accepted = True
    for conflict in conflicts:
        conflict_supported = False
        for support in supports[i]:
            if is_strictly_preferred(pos, support, conflict[0]) or is_strictly_preferred(pos, support, conflict[1]):
                conflict_supported = True
                break
        if not conflict_supported:
            accepted = False    
    if accepted :
        return all_assertions[i]

def compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str):
    
    # read pos set from file
    pos = read_pos(pos_path)
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    try:
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # Count rows in each table and sum them
        total_rows = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            total_rows += count

        print(f"The size of the ABox is {total_rows}.")
        # first, generate the possible assertions of (cl(ABox))
        # returns a list of dl_lite.assertion.w_assertion
        start_time = time.time()
        all_assertions = generate_assertions(ontology_path,cursor)
        inter_time0 = time.time()
        print(f"Number of the generated assertions = {len(all_assertions)}")
        print(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        
        test_assertions = all_assertions#[-1000:]
        #print("testing with the first 1000 assertions")
        # compute the conflicts 
        # conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor)
        inter_time1 = time.time()
        print(f"Number of the conflicts = {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")

        # browse assertions and compute supports
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [degree], it was [(table_name,id,degree)] but I think that table_name and id are useless here
        supports = compute_all_supports(test_assertions,ontology_path, cursor)
        inter_time2 = time.time()
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the computed supports: {supports_size}")
        print(f"Time to compute all the supports of all the assertions: {inter_time2 - inter_time1}")

        cpi_repair = []
        
        all_items = len(test_assertions)
        arguments = [(i, test_assertions, conflicts, supports, pos) for i in range(all_items)]
        # calling check_assertion with pool here iterates over the range of all_items, each assertion is identified with its index i and added from test_assertions if accepted
        with Pool() as pool:
            results = pool.map(check_assertion,arguments)
        cpi_repair = [result for result in results if result is not None]
        """for i in range(all_items):            
            accepted = True
            #if all(any(is_strictly_preferred(pos, support, conflict_member) for support in supports[i] for conflict_member in conflict) for conflict in conflicts): cpi_repair.append(all_assertions[i])
            for conflict in conflicts:
                conflict_supported = False
                for support in supports[i]:
                    if is_strictly_preferred(pos, support, conflict[0]) or is_strictly_preferred(pos, support, conflict[1]):
                        conflict_supported = True
                        break
                if not conflict_supported:
                    accepted = False
                    break
            if accepted :
                cpi_repair.append(all_assertions[i])
            print_progress_bar(i + 1, all_items)"""

        print("\n")
        inter_time3 = time.time()
        print(f"Size of the cpi_repair = {len(cpi_repair)}")
        print(f"Time to compute the cpi_repair: {inter_time3 - inter_time2}")
        #for assertion in cpi_repair:
        #    print(assertion)
        print(f"Total time of execution = {inter_time3 - start_time}")
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")