

import sqlite3

def fix_broken(data_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    try:
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:            
            table_name = table[0]
            print(table_name)
            results = []
            sql_query = f"SELECT * FROM '{table_name}'"
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if len(rows) != 0:
                for row in rows:                
                    if len(row) == 3:
                        results.append([row[1]])
                    if len(row) == 4:
                        results.append([row[1], row[2]])
            print(len(results))
            id = 1
            for result in results:
                if len(result) == 1:
                    sql_query = f"UPDATE '{table_name}' SET id = '{id}' WHERE individual0 = '{result[0]}'"

                else:
                    sql_query = f"UPDATE '{table_name}' SET id = '{id}' WHERE individual0 = '{result[0]}' AND individual1 = '{result[1]}'"
                cursor.execute(sql_query)
                id += 1

        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")


if __name__ == "__main__":
    data_paths = ["bench_prepa/dataset_small_u1/university0.5_p_0.000005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.00001.db", "bench_prepa/dataset_small_u1/university0.5_p_0.00005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.0005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.001.db"]

    for data_path in data_paths:
        fix_broken(data_path)
    