
import os
import pathlib
import time
import psycopg2
from database_version.parser_to_db import abox_to_database, create_database, read_pos
from dl_lite.assertion import assertion, w_assertion
from dl_lite.new_repair import check_all_dominance, check_assertion_in_cpi_repair, compute_cpi_repair, compute_supports, conflict_set, generate_assertions_naive, generate_possible_assertions, get_all_assertions, is_strictly_preferred, new_check_assertion_in_cpi_repair
from dl_lite_parser.tbox_parser import read_tbox

database_name = "test_abox"
host = "localhost"
user = "py_reasoner"

project_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_directory, f"{database_name}.db")
create_database(host,database_name,user,user,db_path)

path = pathlib.Path().resolve()
common_path = "/benchmark_data/data/"
tbox = read_tbox(str(path)+common_path+"ontology0.txt")
#print(tbox)
print("-----------------------------------------------------")
tbox.negative_closure()
print(f"Size of the negative closure = {len(tbox.get_negative_axioms())}")
tbox.check_integrity()
try:  

    conn = psycopg2.connect(
        host=host,
        database=database_name,
        user=user,
        password=user
    )

    cursor = conn.cursor()
    file_path = str(path)+common_path+"dataset_small.txt"
    abox_to_database(file_path,database_name,cursor)
    
    pos_order = read_pos(str(path)+common_path+"pos_dataset_small.txt") 

    # Measure execution time
    start_time = time.time()
    conflicts = conflict_set(tbox,cursor)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    
    print(f"Size of the conflicts = {len(conflicts)}")
    
    print("The next part is for testing :")
    # Generate all possible assertions to compute the whole repair
    possible = generate_possible_assertions(cursor, tbox.get_positive_axioms())
    possible += get_all_assertions(cursor)

    verif_count = 0
    for check_assertion in possible:
        if (new_check_assertion_in_cpi_repair(cursor, tbox, pos_order, conflicts, check_assertion)):
            verif_count += 1
    print("The size of the cpi_repair using method 1: ",verif_count)

    check_list = generate_assertions_naive(cursor,tbox.get_positive_axioms())

    cpi_repair = compute_cpi_repair(cursor, tbox, pos_order, conflicts, check_list)
    print("The size of the cpi_repair using method 2: ",len(cpi_repair))


    conn.commit()
    cursor.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as e:
    print("An error occurred:", e)