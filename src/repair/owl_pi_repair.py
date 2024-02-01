# in order to compute pi_repair it is enough to check if each assertion {f} is accepted by querying for conflicts with a condition of table.degree not in degrees strictly less than the degree of {f}
# A better way is to get all conflicts then check if at least one element of conflict is striclty less preferred to {f}
from multiprocessing import Pool
import sqlite3
import sys
import time
from repair.owl_assertions_generator import get_all_abox_assertions
from repair.owl_conflicts import check_conflicting_subset, compute_conflicts, get_all_row_queries
from repair.owl_cpi_repair import read_pos

def print_progress_bar(iteration, total, bar_length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(bar_length * iteration // total)
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length - 1)

    sys.stdout.write('\rProgress: |%s| %s%%' % (bar, percent))
    sys.stdout.flush()
    
def check_in_pi_repair(all_queries, cursor, successors):
    if check_conflicting_subset(all_queries, cursor, successors):
         return False
    return True

def check_assertion(args):
    conflicts, pos_dict, assertion = args
    successors = pos_dict[assertion.get_assertion_weight()]
    for conflict in conflicts:
        if conflict[0][2] not in successors and conflict[1][2] not in successors:
            return
    return assertion

def compute_pi_repair(ontology_path: str, data_path: str, pos_path: str):
    # read pos set from file
    pos_dict = read_pos(pos_path)
    ABox_name = data_path.split("/")[-1]
    TBox_name = ontology_path.split("/")[-1]
    print(f"Computing Cpi-repair for the ABox: {ABox_name} and the TBox: {TBox_name}")

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
        start_time = time.time()
        assertions = get_all_abox_assertions(tables,cursor)
        inter_time0 = time.time()
        print(f"Number of the generated assertions = {len(assertions)}")
        print(f"Time to compute the generated assertions: {inter_time0 - start_time}")

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(ontology_path,cursor,pos_dict)
        inter_time1 = time.time()
        print(f"Number of the conflicts = {len(conflicts)}")
        print(f"Time to compute the conflicts: {inter_time1 - inter_time0}")

        test_assertions = assertions#[:1000]
        print(f"testing with {len(test_assertions)} assertions")
        inter_time1 = time.time()

        # The following checking way is supposed to be improved and can be parallelized
        arguments = [(conflicts, pos_dict, assertion) for assertion in test_assertions]
        with Pool() as pool:
            results = pool.map(check_assertion, arguments)
        pi_repair = [result for result in results if result is not None]

        """for assertion in test_assertions:
            accepted = True
            successors = pos_dict[assertion.get_assertion_weight()]
            for conflict in conflicts:
                if conflict[0][2] not in successors and conflict[1][2] not in successors:
                    accepted = False
                    break
            if accepted:
                pi_repair.append(assertion)
            print_progress_bar(test_assertions.index(assertion),len(test_assertions))"""     
        
        """all_queries = get_all_row_queries(ontology_path)
        inter_time2 = time.time()
        print(f"Time to generate and rewrite all conflict CQ queries {inter_time2 - inter_time1}")
        
        pi_repair = []

        for assertion in test_assertions:
            successors = pos_dict[assertion.get_assertion_weight()]
            if check_in_pi_repair(all_queries, cursor, successors):
                pi_repair.append(assertion)
            print_progress_bar(test_assertions.index(assertion),len(test_assertions))"""

        inter_time3 = time.time()
        print()
        print(f"Size of the pi_repair = {len(pi_repair)}")
        print(f"Time to compute the pi_repair: {inter_time3 - inter_time1}")

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")