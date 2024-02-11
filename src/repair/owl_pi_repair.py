# in order to compute pi_repair it is enough to check if each assertion {f} is accepted by querying for conflicts with a condition of table.degree not in degrees strictly less than the degree of {f}
# A better way is to get all conflicts then check if at least one element of conflict is striclty less preferred to {f}
from multiprocessing import Pool
import sqlite3
import time
from repair.owl_assertions_generator import get_all_abox_assertions
from repair.owl_conflicts import compute_conflicts
from repair.utils import read_pos

def check_assertion(args):
    conflicts, pos_dict, assertion = args
    successors = pos_dict[assertion.get_assertion_weight()]
    for conflict in conflicts:
        if conflict[0][2] not in successors and conflict[1][2] not in successors:
            return
    return assertion

def compute_pi_repair(ontology_path: str, data_path: str, pos_path: str):
    exe_results = []

    # read pos set from file
    pos_dict = read_pos(pos_path)
    pos_name = pos_path.split("/")[-1]
    ABox_name = data_path.split("/")[-1]
    TBox_name = ontology_path.split("/")[-1]
    print(f"Computing pi-repair for the ABox: {ABox_name} and the TBox: {TBox_name} with the POS: {pos_name}")

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
        print(f"Size of the ABox: {total_rows}.")
        exe_results.append(total_rows)
        
        start_time = round(time.time(), 3)
        assertions = get_all_abox_assertions(tables,cursor)
        inter_time0 = round(time.time(), 3)
        print(f"Number of the generated assertions: {len(assertions)}")
        print(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        
        exe_results.append(inter_time0 - start_time)

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time1 = round(time.time(), 3)
        print(f"Number of the conflicts: {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results.append(len(conflicts))
        exe_results.append(inter_time1 - inter_time0)
        
        inter_time1 = round(time.time(), 3)

        pi_repair = compute_pi_repair_raw(assertions, conflicts, pos_dict)
        
        inter_time3 = round(time.time(), 3)
        print(f"Size of the pi_repair: {len(pi_repair)}")
        print(f"Time to compute the pi_repair: {inter_time3 - inter_time1}")
        exe_results.append(len(pi_repair))
        exe_results.append(inter_time3 - inter_time1)

        print(f"Total time of execution: {inter_time3 - start_time}")
        exe_results.append(inter_time3 - start_time)

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    
    return exe_results

def compute_pi_repair_raw(assertions, conflicts, pos_dict):
    arguments = [(conflicts, pos_dict, assertion) for assertion in assertions]
    with Pool() as pool:
        results = pool.map(check_assertion, arguments)
    pi_repair = set([result for result in results if result is not None])
    return pi_repair