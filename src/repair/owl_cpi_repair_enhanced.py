from multiprocessing import Pool
import sqlite3
import time
from repair.owl_assertions_generator import generate_assertions, get_all_abox_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_cpi_repair import compute_cpi_repair_raw
from repair.owl_pi_repair import compute_pi_repair_raw
from repair.owl_supports import compute_all_supports_enhanced, compute_cl_pi_repair
from repair.utils import read_pos

def compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str):
    exe_results = []
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
        
        start_time = round(time.time(), 3)
        abox_assertions = get_all_abox_assertions(tables,cursor)
        inter_time0 = round(time.time(), 3)
        print(f"Number of the ABox assertions: {len(abox_assertions)}")
        print(f"Time to load the ABox assertions: {inter_time0 - start_time}")

        all_assertions = generate_assertions(ontology_path, cursor)

        generated_assertions = all_assertions - set(abox_assertions)
        inter_time1 = round(time.time(), 3)
        print(f"Number of new generated assertions: {len(generated_assertions)}")
        print(f"Time to compute the generated assertions: {inter_time1 - inter_time0}")
        exe_results.append(len(generated_assertions))
        exe_results.append(inter_time1 - inter_time0)

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time2 = round(time.time(), 3)
        print(f"Number of the conflicts: {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")

        # compute the pi_repair
        pi_repair = compute_pi_repair_raw(abox_assertions, conflicts, pos_dict)
        inter_time2 = round(time.time(), 3)
        print(f"Size of the pi_repair: {len(pi_repair)}")
        print(f"Time to compute the pi_repair: {inter_time2 - inter_time1}")
        

        # check if the rest is in cpi-repair
        left_to_check = all_assertions - pi_repair
        print(f"The number of assertions left to check: {len(left_to_check)}")

        cl_pi_repair = compute_cl_pi_repair(ontology_path, pi_repair)
        print(f"Size of cl_pi_repair: {len(cl_pi_repair)}")
        exe_results.append(len(cl_pi_repair))
        
        left_to_check = left_to_check - cl_pi_repair
        
        # browse assertions and compute supports
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [(table_name,id,degree)] 
        supports = compute_all_supports_enhanced(left_to_check, ontology_path, cursor, pos_dict)
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the computed supports before filtering: {supports_size}")
        supports = {key: value for key, value in supports.items() if len(value) > 1}

        inter_time3 = round(time.time(), 3)
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the computed supports: {supports_size}")
        print(f"Time to compute all the supports of all the assertions: {inter_time3 - inter_time2}")        
        
        left_to_check = set(supports.keys())
        cpi_repair = compute_cpi_repair_raw(left_to_check, conflicts, supports, pos_dict)
        inter_time4 = round(time.time(), 3)
        print(f"Size of the cpi_repair: {len(cpi_repair) + len(pi_repair) + len(cl_pi_repair)}")
        print(f"Time to compute the cpi_repair: {inter_time4 - inter_time3}")
        exe_results.append(len(cpi_repair) + len(pi_repair) + len(cl_pi_repair))
        exe_results.append(inter_time4 - inter_time3)
        
        print(f"Total time of execution: {inter_time4 - start_time}")
        exe_results.append(inter_time4 - start_time)

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    
    return exe_results