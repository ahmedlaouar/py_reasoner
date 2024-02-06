import sqlite3
import time
from repair.owl_assertions_generator import generate_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_dominance import dominates
from repair.owl_supports import compute_all_supports
from multiprocessing import Pool
from repair.utils import read_pos

def check_assertion(args):
    i, all_assertions, conflicts, supports, pos = args
    accepted = True
    for conflict in conflicts:
        conflict_supported = False
        for support in supports[i]:
            if dominates(pos, [support], conflict):
                conflict_supported = True
                break
        if not conflict_supported:
            accepted = False    
    if accepted :
        return all_assertions[i]

def compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str):
    exe_results = []
    # read pos set from file
    pos_dict = read_pos(pos_path)
    pos_name = pos_path.split("/")[-1]
    ABox_name = data_path.split("/")[-1]
    TBox_name = ontology_path.split("/")[-1]
    print(f"Computing Cpi-repair for the ABox: {ABox_name} and the TBox: {TBox_name} with the POS: {pos_name}")
    
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
        print(f"Size of the ABox is {total_rows}.")
        exe_results.append(total_rows)
        
        # first, generate the possible assertions of (cl(ABox)), returns a list of dl_lite.assertion.w_assertion
        start_time = time.time()
        all_assertions = generate_assertions(ontology_path,cursor)
        inter_time0 = time.time()
        print(f"Number of the generated assertions: {len(all_assertions)}")
        print(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        exe_results.append(len(all_assertions))
        exe_results.append((inter_time0 - start_time))

        test_assertions = all_assertions#[:10000]
        print(f"testing with {len(test_assertions)} assertions")
        
        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time1 = time.time()
        print(f"Number of conflicts: {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results.append(len(conflicts))
        exe_results.append((inter_time1 - inter_time0))
        
        # browse assertions and compute supports
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [(table_name,id,degree)] 
        supports = compute_all_supports(test_assertions,ontology_path, cursor, pos_dict)
        inter_time2 = time.time()
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the computed supports: {supports_size}")
        print(f"Time to compute all the supports of all the assertions: {inter_time2 - inter_time1}")
        exe_results.append(supports_size)
        exe_results.append(inter_time2 - inter_time1)

        cpi_repair = []
        
        nbr_items = len(test_assertions)
        arguments = [(i, test_assertions, conflicts, supports, pos_dict) for i in range(nbr_items)]
        
        # calling check_assertion with pool here iterates over the range of nbr_items, each assertion is identified with its index i and added from test_assertions if accepted
        with Pool() as pool:
            results = pool.map(check_assertion,arguments)          

        cpi_repair = [result for result in results if result is not None]
        
        inter_time3 = time.time()
        print(f"Size of the cpi_repair: {len(cpi_repair)}")
        print(f"Time to compute the cpi_repair: {inter_time3 - inter_time2}")
        exe_results.append(len(cpi_repair))
        exe_results.append(inter_time3 - inter_time2)
        
        print(f"Total time of execution: {inter_time3 - start_time}")
        exe_results.append(inter_time3 - start_time)
        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")

    return exe_results