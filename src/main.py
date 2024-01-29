import sqlite3
import time
from dl_lite.assertion import w_assertion
from repair.owl_assertions_generator import generate_assertions
from repair.owl_conflicts import compute_conflicts
from repair.owl_cpi_repair import compute_cpi_repair

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
    
    pos_path = "bench_prepa/dataset.01/pos1000.txt"

    compute_cpi_repair(ontology_path,data_path,pos_path)