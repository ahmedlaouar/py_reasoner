import sys
import time
from dl_lite_parser.parser_to_db import abox_to_database, empty_database, read_full_pos
from repair.assertions_generator import generate_possible_assertions_rec
from repair.conflicts import conflict_set, reduced_conflict_set
from repair.cpi_repair import check_assertion_in_cpi_repair, compute_cpi_repair_bis
import sqlite3

def conflicts_helper(tbox, abox_path, db_path):
    try:
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()

        empty_database(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        abox_to_database(abox_path, cursor)

        # Measure execution time
        start_time = time.time()
        conflicts = conflict_set(tbox, cursor)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        print(f"Size of the conflicts = {len(conflicts)}")

        for conf in conflicts:
            print(conf[0], conf[1])

        conn.commit()
        cursor.close()
        conn.close()

    except sqlite3.Error as e:
        print("An error occurred:", e)

def cpi_repair_helper(tbox, abox_path, pos_path, db_path):
    try:
        # Measure execution time
        start_time = time.time()
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()
        inter_time0 = time.time()
        print(f"Time to compute negative closure of TBox: {inter_time0 - start_time}")

        empty_database(db_path)
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("-------------- Reading ABox to database -------------")
        abox_to_database(abox_path, cursor)
        
        # Query to get ABox size
        cursor.execute("SELECT COUNT(*) FROM assertions")
        abox_size = cursor.fetchone()[0]
        
        pos_matrix = read_full_pos(pos_path)
        print(f"Reading done, size of the ABox: {abox_size}, POS size: {len(pos_matrix)-1}")
        inter_time1 = time.time()
        print(f"Time to read: {inter_time1 - inter_time0}")
        
        # Compute the conflicts without dominance check
        conflicts = conflict_set(tbox, cursor)
        print(f"Size of the conflicts without dominance check: {len(conflicts)}")
        inter_time2 = time.time()
        print(f"Time to compute conflicts without dominance check: {inter_time2 - inter_time1}")
        
        # Compute the conflicts with dominance check
        reduced_conflicts = reduced_conflict_set(tbox, cursor, pos_matrix)
        print(f"Size of the conflicts with dominance check: {len(reduced_conflicts)}")
        inter_time3 = time.time()
        print(f"Time to compute conflicts with dominance check: {inter_time3 - inter_time2}")

        check_list = generate_possible_assertions_rec(cursor, tbox.get_positive_axioms())
        inter_time4 = time.time()
        print(f"Size of assertions to test: {len(check_list) + abox_size}")
        print(f"Time to generate additional assertions to test: {inter_time4 - inter_time3}")

        for elt in check_list:
            print(elt)

        cpi_repair = compute_cpi_repair_bis(cursor, tbox, pos_matrix, check_list, reduced_conflicts)

        print(f"The size of the cpi_repair: {len(cpi_repair)}")
        
        for elt in cpi_repair:
            print(elt)

        inter_time5 = time.time()
        cp_repair_time = inter_time5 - inter_time3
        print(f"Time to compute cpi_repair: {cp_repair_time}")

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        conn.commit()
        cursor.close()
        conn.close()

        return tbox.tbox_size(), abox_size, len(pos_matrix) - 1, len(conflicts), len(cpi_repair), cp_repair_time

    except sqlite3.Error as e:
        print("An error occurred:", e)

def check_in_cpi_repair_helper(tbox, abox_path, pos_path, check_assertion, db_path):
    try:
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()

        empty_database(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        abox_to_database(abox_path, cursor)
        pos_order = read_full_pos(pos_path)

        # Measure execution time
        start_time = time.time()

        if check_assertion_in_cpi_repair(cursor, tbox, pos_order, check_assertion):
            print(f"{check_assertion} is in the Cpi-repair of the abox")
        else:
            print(f"{check_assertion} is not in the Cpi-repair of the abox")

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        conn.commit()
        cursor.close()
        conn.close()

    except sqlite3.Error as e:
        print("An error occurred:", e)
