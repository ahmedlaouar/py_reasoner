
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
common_path = "/benchmark_data/data/"
tbox = read_tbox(str(path)+common_path+"ontology0.txt")
print(tbox)
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
    
    check_assertion1 = w_assertion("Rolehwpfy","Indzddswizuc","Indqjeuypinp",105)
    check_assertion2 = w_assertion("Conceptjbzexayzs","Indfxwo",weight=201)
    check_assertion3 = w_assertion("Conceptguzqweq","Indqgjv",weight=888)
    
    print(is_strictly_preferred(cursor, check_assertion1, check_assertion2))
    print(is_strictly_preferred(cursor, check_assertion1, check_assertion3))
    print(is_strictly_preferred(cursor, check_assertion2, check_assertion3))
    # Measure execution time
    """start_time = time.time()
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
            file.write(s+'\n')"""
    


    conn.commit()
    cursor.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as e:
    print("An error occurred:", e)