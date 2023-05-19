
import os
import pathlib
import time
import psycopg2
from database_version.parser_to_db import abox_to_database, create_database
from dl_lite.assertion import assertion
from dl_lite.new_repair import compute_supports, conflict_set
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
        print(c)
    print("-----------------------------------------------------")
    with open(str(path)+"/src/conflicts_first_dataset_sql.txt", 'w') as file:
        for conf in conflicts :
            file.write(str(conf)+'\n')
    
    check_assertion = assertion("Staff","Bob")
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    print(f"Size of the supports = {len(supports)}")
    for support in supports:
        print(support)

    conn.commit()
    cursor.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as e:
    print("An error occurred:", e)