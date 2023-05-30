
import sys
import time
import psycopg2
from dl_lite_parser.parser_to_db import abox_to_database, read_pos
from repair.assertions_generator import generate_possible_assertions_rec, get_all_assertions
from repair.conflicts import conflict_set
from repair.cpi_repair import check_assertion_in_cpi_repair, compute_cpi_repair

#necessary global constants
database_name = "test_abox"
host = "localhost"
user = "py_reasoner"

def conflicts_helper(tbox,abox_path):
    try:  
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()

        conn = psycopg2.connect(
            host=host,
            database=database_name,
            user=user,
            password=user
        )

        cursor = conn.cursor()
        abox_to_database(abox_path,database_name,cursor)

        # Measure execution time
        start_time = time.time()
        conflicts = conflict_set(tbox,cursor)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        
        print(f"Size of the conflicts = {len(conflicts)}")

        conn.commit()
        cursor.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as e:
        print("An error occurred:", e)

def cpi_repair_helper(tbox,abox_path,pos_path):

    try:  
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()

        conn = psycopg2.connect(
            host=host,
            database=database_name,
            user=user,
            password=user
        )
        # Measure execution time
        start_time = time.time()
        
        cursor = conn.cursor()        
        abox_to_database(abox_path,database_name,cursor)
        
        conflicts = conflict_set(tbox,cursor)        
        print(f"Size of the conflicts = {len(conflicts)}")

        pos_order = read_pos(pos_path)

        check_list = generate_possible_assertions_rec(cursor, tbox.get_positive_axioms())
        check_list += get_all_assertions(cursor)

        cpi_repair = compute_cpi_repair(cursor, tbox, pos_order, conflicts, check_list)

        print(f"The size of the cpi_repair: {len(cpi_repair)}")
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        conn.commit()
        cursor.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as e:
        print("An error occurred:", e)

def check_in_cpi_repair_helper(tbox,abox_path,pos_path,check_assertion):
    try:  
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent, cannot proceed in this case, abort execution.")
            sys.exit()

        conn = psycopg2.connect(
            host=host,
            database=database_name,
            user=user,
            password=user
        )
        # Measure execution time
        start_time = time.time()
        
        cursor = conn.cursor()        
        abox_to_database(abox_path,database_name,cursor)
        pos_order = read_pos(pos_path)

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

    except (Exception, psycopg2.DatabaseError) as e:
        print("An error occurred:", e)