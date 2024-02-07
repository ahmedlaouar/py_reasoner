import sqlite3
import time
from bench_prepa.owl_prepa.add_pos_to_db import add_pos_to_db
from repair.owl_conflicts import compute_conflicts
from repair.owl_cpi_repair import compute_cpi_repair
from repair.owl_cpi_repair_enhanced import compute_cpi_repair_enhanced
from repair.owl_pi_repair import compute_pi_repair

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
    
    data_path = "bench_prepa/dataset.01/University0_p_0.001_pos_1000.db"

    results_path = "bench_prepa/dataset.01/execution_results.txt"
    
    pos_list = ["bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos1000_prob_1.txt","bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos1000_prob_0.75.txt","bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos1000_prob_0.5.txt","bench_prepa/dataset.01/DAGs_with_bnlearn/ordered_method/pos1000_prob_0.25.txt"]

    for pos_path in pos_list:
        add_pos_to_db(data_path, pos_path)

        results1 = compute_pi_repair(ontology_path,data_path,pos_path)

        results2 = compute_cpi_repair(ontology_path,data_path,pos_path)

        results3 = compute_cpi_repair_enhanced(ontology_path,data_path,pos_path)

        pos_name = pos_path.split("/")[-1]
        ABox_name = data_path.split("/")[-1]
        TBox_name = ontology_path.split("/")[-1]

        with open(results_path, 'a') as file:
            file.write('\n')
            file.write(f"Execution with: the ABox: {ABox_name} and the TBox: {TBox_name} with the POS: {pos_name}")

        for result in [results1, results2, results3]:
            for key,value in result.items():
                with open(results_path, 'a') as file:
                    file.write('\n')
                    file.write(key+" : "+value)