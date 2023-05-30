import os
import pathlib
import time
import psycopg2
from dl_lite_parser.parser_to_db import abox_to_database, create_database
from repair.conflicts import conflict_set
from dl_lite_parser.tbox_parser import read_tbox

database_name = "test_abox"
host = "localhost"
user = "py_reasoner"

project_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_directory, f"{database_name}.db")
create_database(host,database_name,user,user,db_path)

path = pathlib.Path().resolve()
print("---------- Reading the TBox from file ----------")
tbox = read_tbox(str(path)+"/examples/ontology.txt")
print(f"Size of the TBox = {len(tbox.get_negative_axioms())+len(tbox.get_positive_axioms())}")
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
    file_path = str(path)+"/examples/dataset.txt"
    abox_to_database(file_path,database_name,cursor)
    
    # Measure execution time
    start_time = time.time()
    conflicts = conflict_set(tbox,cursor)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Size of the conflicts = {len(conflicts)}")
    print("---------------------------------------------------------")
    with open(str(path)+"/examples/conflicts_set_SQL.txt", 'w') as file:
        for conf in conflicts :
            s = "({}),({})".format(conf[0],conf[1])
            file.write(s+'\n')
    print("-----------------------------------------------------")
except (Exception, psycopg2.DatabaseError) as e:
    print("An error occurred:", e)