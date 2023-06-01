import os
from dl_lite.assertion import assertion    
import sqlite3

def empty_database(db_path):
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Drop all tables
        for table in tables:
            cursor.execute(f"DROP TABLE {table[0]}")

        conn.commit()
        cursor.close()
        conn.close()
        
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

def read_abox(file_path, cursor):
    with open(file_path, 'r') as file:
        co = 1
        for line in file:
            if line.strip() == "BEGINABOX" or line.strip() == "ENDABOX":
                continue
            new_assertion, weight = process_line(line) 
            # Insert values into the "assertions" table
            cursor.execute(f"INSERT INTO assertions (id, assertion_name, individual_1, individual_2, weight) VALUES ('{co}', '{new_assertion.get_assertion_name()}', '{new_assertion.get_individuals()[0]}', '{new_assertion.get_individuals()[1]}', '{weight}')")           
            co += 1


def abox_to_database(file_path, cursor):
    # Drop the assertions table if it exists
    cursor.execute("DROP TABLE IF EXISTS assertions;")
    
    # Create the assertions table
    cursor.execute('''
        CREATE TABLE assertions (
            id INT PRIMARY KEY,
            assertion_name VARCHAR(50),
            individual_1 VARCHAR(50),
            individual_2 VARCHAR(50),
            weight INT
        );''')

    read_abox(file_path, cursor)


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

