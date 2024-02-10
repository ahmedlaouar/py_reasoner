import sqlite3
import time
from dl_lite.assertion import w_assertion
from repair.owl_conflicts import compute_conflicts
from repair.owl_cpi_repair import compute_cpi_repair
from repair.owl_cpi_repair_enhanced import compute_cpi_repair_enhanced
from repair.owl_pi_repair import compute_pi_repair
from repair.utils import add_pos_to_db

def conflicts_helper(ontology_path,data_path) :
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

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

    start_time = time.time()
    try:
        conflicts = compute_conflicts(ontology_path,cursor)
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    end_time = time.time()

    print(f"Size of the conflicts is {len(conflicts)}")

    print(f"Time to compute conflicts is {end_time - start_time}")

    #for conflict in conflicts:
    #    print(conflict)

    conn.commit()
    conn.close()

if __name__ == "__main__":

    ontology_path = "ontologies/univ-bench/lubm-ex-20_disjoint.owl"
    
    data_path = "bench_prepa/dataset.01/University0_p_0.005.db"

    results_path = "bench_prepa/dataset.01/execution_results_0.1.txt"

    pos_dir_path = "bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos500/"
    pos_list = ["pos500_prob_0.5.txt", "pos500_prob_0.6.txt", "pos500_prob_0.7.txt", "pos500_prob_0.8.txt", "pos500_prob_0.9.txt", "pos500_prob_1.0.txt"]

    for pos in pos_list:
        pos_path = pos_dir_path + pos

        add_pos_to_db(data_path, pos_path)

        results1 = compute_pi_repair(ontology_path,data_path,pos_path)

        results2 = compute_cpi_repair(ontology_path,data_path,pos_path)

        results3 = compute_cpi_repair_enhanced(ontology_path,data_path,pos_path)

        pos_name = pos_path.split("/")[-1]
        ABox_name = data_path.split("/")[-1]
        TBox_name = ontology_path.split("/")[-1]

        result = results1 + results2 + results3
        result_str = ",".join(str(e) for e in result)

        with open(results_path, 'a') as file:
            file.write('\n')
            file.write(f"Execution with: the ABox: {ABox_name} and the TBox: {TBox_name} with the POS: {pos_name}")
            file.write('\n')
            file.write(result_str)
