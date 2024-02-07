from multiprocessing import Pool
import sqlite3
import time
from repair.owl_assertions_generator import generate_assertions, generate_not_abox_assertions, get_all_abox_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_pi_repair import compute_pi_repair_raw
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
        exe_results.append(total_rows)
        
        start_time = time.time()
        abox_assertions = get_all_abox_assertions(tables,cursor)
        inter_time0 = time.time()
        print(f"Number of the ABox assertions: {len(abox_assertions)}")
        print(f"Time to load the ABox assertions: {inter_time0 - start_time}")
        exe_results.append(len(abox_assertions))
        exe_results.append((inter_time0 - start_time))

        all_assertions = generate_assertions(ontology_path, cursor)
        print(f"Number of the generated assertions: {len(all_assertions)}")

        remaining_assertions2 = list(set(all_assertions) - set(abox_assertions))
        inter_time1 = time.time()
        print(f"Number of the generated assertions: {len(remaining_assertions2)}")
        print(f"Time to compute the generated assertions: {inter_time1 - inter_time0}")

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time1 = time.time()
        print(f"Number of the conflicts: {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results.append(len(conflicts))
        exe_results.append((inter_time1 - inter_time0))

        # compute the pi_repair
        pi_repair = compute_pi_repair_raw(abox_assertions, conflicts, pos_dict)
        inter_time2 = time.time()
        print(f"Size of the pi_repair: {len(pi_repair)}")
        print(f"Time to compute the pi_repair: {inter_time2 - inter_time1}")
        exe_results.append(len(pi_repair))
        exe_results.append(inter_time2 - inter_time1)


    

    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    
    return exe_results