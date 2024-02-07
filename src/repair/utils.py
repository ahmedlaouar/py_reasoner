import random
import sqlite3

def read_pos(file_path :str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        pos_dict = {}
        for line in lines:
            tokens = [token for token in line.split()]
            weight = int(tokens[0])
            successors = [int(x) for x in tokens[1:]]
            pos_dict[weight] = successors
    return pos_dict

def add_pos_to_db(data_path:str, pos_path:str):
    with open(pos_path, 'r') as file:
        lines_number = sum(1 for line in file)
    
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Get the list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        for i in range(1,count+1):
            degree = random.choice(range(lines_number))
            cursor.execute(f"UPDATE {table[0]} SET degree = ? WHERE id = ?", (degree, i))
    
    conn.commit()
    conn.close()