
import os
import pathlib
import time
import psycopg2
from database_version.parser_to_db import abox_to_database, create_database
from dl_lite.assertion import assertion, w_assertion
from dl_lite.new_repair import check_all_dominance, check_assertion_in_cpi_repair, compute_supports, conflict_set, is_strictly_preferred
from dl_lite_parser.tbox_parser import read_tbox

database_name = "test_abox"
host = "localhost"
user = "py_reasoner"

project_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_directory, f"{database_name}.db")
create_database(host,database_name,user,user,db_path)

path = pathlib.Path().resolve()

tbox = read_tbox(str(path)+"/src/first_tbox.txt")
print(tbox)
print("-----------------------------------------------------")
tbox.negative_closure()
print(f"Size of the negative closure = {len(tbox.get_negative_axioms())}")
try:  

    conn = psycopg2.connect(
        host=host,
        database=database_name,
        user=user,
        password=user
    )

    cursor = conn.cursor()
    file_path = str(path)+"/src/first_abox.txt"
    abox_to_database(file_path,database_name,cursor)
    
    # Measure execution time
    start_time = time.time()
    conflicts = conflict_set(tbox,cursor)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    
    print(f"Size of the conflicts = {len(conflicts)}")
    for c in conflicts:
        print(c[0],c[1])
    print("-----------------------------------------------------")
    with open(str(path)+"/src/conflicts_first_dataset_sql.txt", 'w') as file:
        for conf in conflicts :
            s = "({}),({})".format(conf[0],conf[1])
            file.write(s+'\n')
    
    check_assertion = assertion("Staff","Bob")
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    print(f"Size of the supports = {len(supports)}")
    
    print(check_all_dominance(cursor,conflicts,supports))

    check_assertion_in_cpi_repair(cursor, tbox, check_assertion)
    
    check_assertion_2 = assertion("Reports","F78")
    supports_2 = compute_supports(check_assertion_2, tbox.get_positive_axioms(),cursor)
    print(f"Size of the supports = {len(supports_2)}")
    
    print(check_all_dominance(cursor,conflicts,supports_2))

    check_assertion_in_cpi_repair(cursor, tbox, check_assertion_2)

    check_assertion_3 = assertion("Manager","Bob")
    supports_3 = compute_supports(check_assertion_3, tbox.get_positive_axioms(),cursor)
    print(f"Size of the supports = {len(supports_3)}")
    
    print(check_all_dominance(cursor,conflicts,supports_3))

    check_assertion_in_cpi_repair(cursor, tbox, check_assertion_3)

    conn.commit()
    cursor.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as e:
    print("An error occurred:", e)