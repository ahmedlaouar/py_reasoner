import time
import sqlite3
from dl_lite.assertion import w_assertion
from repair.owl_conflicts import compute_conflicts, compute_conflicts_naive
from repair.owl_cpi_repair import check_assertion
from repair.owl_supports import compute_all_supports
from repair.utils import read_pos

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
        conflicts = compute_conflicts_naive(ontology_path,cursor)
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    end_time = time.time()

    for conflict in conflicts:
        print(conflict)

    print(f"Size of the conflicts is {len(conflicts)}")

    print(f"Time to compute conflicts is {end_time - start_time}")

    print(f"Percent of conflicts w.r.t. the size of the ABox: {len(conflicts)*100/total_rows}")

    conn.commit()
    conn.close()

def read_assertion(line: str):
    splitted = line.split(';')
    names = splitted[0].split('(')
    assertion_name = names[0]
    if ',' in names[1]:
        individuals = names[1].split(',')
        individual_1 = individuals[0]
        individual_2 = individuals[1].replace(")", "")
        return  w_assertion(assertion_name,individual_1,individual_2)
    else:
        individual_1 = names[1].replace(")", "")
        return  w_assertion(assertion_name,individual_1)

def check_in_cpi_repair_helper(tbox_path,abox_path,pos_path,assertion):
    pos_dict = read_pos(pos_path)
    
    conn = sqlite3.connect(abox_path)
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
        print(f"Size of the ABox: {total_rows}.")
        
        ABox_name = abox_path.split("/")[-1]
        print(f"Checking if: {assertion} is in the cpi-repair of ABox: {ABox_name}.")

        # compute the conflicts, conflicts are of the form ((table1name, id, degree),(table2name, id, degree))
        conflicts = compute_conflicts(tbox_path,cursor,pos_dict)
        
        # compute supports of the assertion
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [(table_name,id,degree)] 
        supports = compute_all_supports([assertion], tbox_path, cursor, pos_dict)
        supports_size = sum((len(val) for val in supports.values()))
        print(f"Number of all the supports: {supports_size}")
        
        args = assertion, conflicts, supports[assertion], pos_dict
        
        if check_assertion(args) != None:
            print(f"The assertion {assertion} belongs to the cpi_repair")
        else:
            print(f"The assertion {assertion} does not belong to the cpi_repair") 

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")
    
    return