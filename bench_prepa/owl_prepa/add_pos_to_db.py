import random
import sqlite3


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

if __name__ == "__main__":
    #data_path = "bench_prepa/dataset.01/University0_p_0.001_pos_50.db"
    #data_path = "bench_prepa/dataset.01/University0_p_0.001_pos_500.db"
    data_path = "bench_prepa/dataset.01/University0_p_0.001_pos_1000.db"
    #data_path = "bench_prepa/dataset.01/University0_p_0.001_pos_10000.db"

    #pos_path = "bench_prepa/dataset.01/pos50.txt"
    #pos_path = "bench_prepa/dataset.01/pos500.txt"
    pos_path = "bench_prepa/dataset.01/pos1000.txt"
    #pos_path = "bench_prepa/dataset.01/pos10000.txt"
    add_pos_to_db(data_path, pos_path)
    print(f"Added {pos_path} to {data_path}")
