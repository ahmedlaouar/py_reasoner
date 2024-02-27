from multiprocessing import Pool
import sqlite3
from repair.owl_assertions_generator import generate_assertions
from repair.owl_supports import compute_all_supports_naive

def check_assertion(args):
    assertion, supports, assertions = args
    if assertion in supports[assertion]:
        for element in assertions:
            if assertion in supports[element]:
                return None
        return assertion
    return None

def compute_to_drop(assertions, ontology_path, cursor):
    to_remove = set()

    supports = compute_all_supports_naive(assertions,ontology_path, cursor)

    print(sum((len(val) for val in supports.values())))
    arguments = [(assertion, supports, (assertions-set([assertion]))) for assertion in assertions]
    
    with Pool() as pool:
        results = pool.map(check_assertion,arguments)
    
    to_remove = [result for result in results if result is not None]
    
    return to_remove

def drop_from_db(to_remove, cursor):
    for assertion in to_remove:
        table_name = assertion.get_assertion_name()
        ind1, ind2 = assertion.get_individuals()
        if ind2 == None:
            sql_query = f"DELETE FROM '{table_name}' WHERE individual0='{ind1}'"
        else:
            sql_query = f"DELETE FROM '{table_name}' WHERE individual0='{ind1}' AND individual1='{ind2}'"
        cursor.execute(sql_query)

if __name__ == "__main__":
    data_path = "bench_prepa/dataset_small_u1/University0.db"
    ontology_path = "ontologies/univ-bench/lubm-ex-20_disjoint.owl"
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    try:
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        assertions = generate_assertions(ontology_path,cursor)

        print(len(assertions))

        to_remove = compute_to_drop(assertions, ontology_path, cursor)

        print(len(to_remove))

        #drop_from_db(to_remove, cursor)

        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")