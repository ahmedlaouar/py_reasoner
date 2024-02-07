from multiprocessing import Pool
import sqlite3
import time
from repair.owl_assertions_generator import generate_assertions, get_all_abox_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_cpi_repair import compute_cpi_repair_raw
from repair.owl_pi_repair import compute_pi_repair_raw
from repair.owl_supports import compute_all_supports, compute_all_supports_check
from repair.utils import read_pos

def compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str):
    exe_results = {}
    # read pos set from file
    pos_dict = read_pos(pos_path)
    pos_name = pos_path.split("/")[-1]
    ABox_name = data_path.split("/")[-1]
    TBox_name = ontology_path.split("/")[-1]
    print(f"Computing cpi-repair for the ABox: {ABox_name} and the TBox: {TBox_name} with the POS: {pos_name}")

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
        exe_results["Abox size"] = total_rows
        
        start_time = time.time()
        abox_assertions = get_all_abox_assertions(tables,cursor)
        inter_time0 = time.time()
        print(f"Number of the ABox assertions: {len(abox_assertions)}")
        print(f"Time to load the ABox assertions: {inter_time0 - start_time}")

        all_assertions = generate_assertions(ontology_path, cursor)

        generated_assertions = all_assertions - abox_assertions
        inter_time1 = time.time()
        print(f"Number of new generated assertions: {len(generated_assertions)}")
        print(f"Time to compute the generated assertions: {inter_time1 - inter_time0}")
        exe_results["New assertions size"] = len(generated_assertions)
        exe_results["Time to new assertions"] = inter_time1 - inter_time0

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time2 = time.time()
        print(f"Number of the conflicts: {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results["Conflict set size"] = len(conflicts)
        exe_results["Time to conflicts"] = (inter_time2 - inter_time1)

        # compute the pi_repair
        pi_repair = compute_pi_repair_raw(abox_assertions, conflicts, pos_dict)
        inter_time2 = time.time()
        print(f"Size of the pi_repair: {len(pi_repair)}")
        print(f"Time to compute the pi_repair: {inter_time2 - inter_time1}")
        

        # check if the rest is in cpi-repair
        left_to_check = all_assertions - pi_repair
        print(f"The number of assertions left to check: {len(left_to_check)}")

        # browse assertions and compute supports
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [(table_name,id,degree)] 
        supports, cl_pi_repair = compute_all_supports_check(left_to_check, ontology_path, cursor, pos_dict, pi_repair)
        inter_time3 = time.time()
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the computed supports: {supports_size}")
        print(f"Time to compute all the supports of all the assertions: {inter_time3 - inter_time2}")
        exe_results["Supports size"] = supports_size
        exe_results["Time to all supports"] = inter_time3 - inter_time2

        left_to_check = left_to_check - cl_pi_repair

        print(f"Size of cl_pi_repair: {len(cl_pi_repair)}")
        exe_results["cl_pi_repair size"] = len(cl_pi_repair)

        cpi_repair = compute_cpi_repair_raw(left_to_check, conflicts, supports, pos_dict)
        inter_time4 = time.time()
        print(f"Size of the cpi_repair: {len(cpi_repair) + len(pi_repair) + len(cl_pi_repair)}")
        print(f"Time to compute the cpi_repair: {inter_time4 - inter_time3}")
        exe_results["cpi_repair size"] = len(cpi_repair) + len(pi_repair) + len(cl_pi_repair)
        exe_results["Time to cpi_repair"] = inter_time4 - inter_time3

        print(f"Total time of execution: {inter_time4 - start_time}")
        exe_results["cpi_repair total time"] = inter_time4 - start_time

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    
    return exe_results