import psycopg2
from dl_lite.assertion import assertion    

def create_database(host,database_name,user,password,db_path):
    
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password
    )
    # Disable autocommit mode to avoid error: DROP DATABASE cannot run inside a transaction block
    conn.autocommit = True

    cursor = conn.cursor()
    # Drop the database if it exists
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")

    # Commit the drop database statement
    conn.commit()

    #see how to fix this later
    #table_space_query = f"CREATE TABLESPACE test_abox LOCATION '{db_path}';"
    #cursor.execute(table_space_query)

    create_database_query = f"CREATE DATABASE {database_name} OWNER py_reasoner TEMPLATE template0;" # TABLESPACE {database_name};"
    cursor.execute(create_database_query)

    conn.commit()
    cursor.close()
    conn.close()

    return

def process_line(line):
    splitted = line.split(';')
    names = splitted[0].split('(')
    assertion_name = names[0]
    if ',' in names[1]:
        individuals = names[1].split(',')
        individual_1 = individuals[0]
        individual_2 = individuals[1].replace(")", "")
        weight = int(splitted[1])
        return  assertion(assertion_name,individual_1,individual_2),weight
    else:
        individual_1 = names[1].replace(")", "")
        weight = int(splitted[1])
        return  assertion(assertion_name,individual_1),weight

def read_abox(file_path: str, cursor):
    with open(file_path, 'r') as file:
        co = 1
        for line in file:
            if line.strip() == "BEGINABOX" or line.strip() == "ENDABOX":
                continue
            new_assertion,weight = process_line(line) 
            # Insert values into the "assertions" table
            cursor.execute(f"INSERT INTO assertions (id, assertion_name, individual_1, individual_2, weight) VALUES ('{co}', '{new_assertion.get_assertion_name()}', '{new_assertion.get_individuals2()[0]}', '{new_assertion.get_individuals2()[1]}', '{weight}')")           
            co += 1
    return

def abox_to_database(file_path: str,database_name,cursor):

    drop_query = f"drop schema if exists {database_name} cascade;"
    
    cursor.execute(drop_query)

    create_query = f"CREATE schema {database_name};"
    set_query = f"SET search_path to {database_name};"
    cursor.execute(create_query)
    cursor.execute(set_query)
    
    cursor.execute('''
        CREATE TABLE assertions (
            id INT PRIMARY KEY,
            assertion_name VARCHAR(50),
            individual_1 VARCHAR(50),
            individual_2 VARCHAR(50),
            weight INT
        );''')

    read_abox(file_path,cursor)

def read_pos(file_path: str):
    pos_order = {}
    with open(file_path, 'r') as file:
        for line in file:
            splitted = line.split(";")
            weight = int(splitted[0])
            successors = [int(x) for x in splitted[1:-1]]
            pos_order[weight] = successors
    return pos_order

def is_preferred(pos,i,j) -> bool:
    check = False
    if j in pos[i]: return True
    else: 
        for successor in pos[i]:
            check = is_preferred(pos,successor,j)
    return check

def read_pos_to_adj_matrix(file_path: str):
    pos_set = read_pos(file_path)
    n = len(pos_set.keys())
    pos_matrix = [[0 for _ in range(n+1)] for _ in range(n+1)]
    for i in range(1,n+1):
        for j in range(1,n+1):
            if is_preferred(pos_set,i,j):
                pos_matrix[i][j] = 1
    return pos_matrix

def read_full_pos(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        n = len(lines)

        # Create an n x n matrix of zeros
        pos_matrix = [[0 for _ in range(n+1)] for _ in range(n+1)]

        # Assign 1 to specific indices
        for line in lines:
            splitted = line.split(";")
            weight = int(splitted[0])
            successors = [int(x) for x in splitted[1:-1]]
            
            for successor in successors:
                pos_matrix[weight][successor] = 1

    return pos_matrix

