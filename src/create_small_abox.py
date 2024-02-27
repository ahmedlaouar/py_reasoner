import random
import sqlite3
from repair.owl_assertions_generator import generate_assertions, get_all_abox_assertions
from repair.owl_supports import compute_all_supports_naive

def drop_from_db(to_remove, cursor):
    for assertion in to_remove:
        table_name = assertion.get_assertion_name()
        ind1, ind2 = assertion.get_individuals()
        if ind2 == None:
            sql_query = f"DELETE FROM '{table_name}' WHERE individual0='{ind1}'"
        else:
            sql_query = f"DELETE FROM '{table_name}' WHERE individual0='{ind1}' AND individual1='{ind2}'"
        cursor.execute(sql_query)

def get_table_row_counts(cursor):
    """Get the row counts for all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    table_row_counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        table_row_counts[table] = count
    return table_row_counts

def delete_random_rows(cursor, table, num_rows):
    """Delete a specified number of random rows from the specified table."""
    cursor.execute(f"SELECT ROWID FROM {table}")
    rowids = [row[0] for row in cursor.fetchall()]
    if rowids:
        random_rowids = random.sample(rowids, min(len(rowids), num_rows))
        cursor.executemany(f"DELETE FROM {table} WHERE ROWID = ?", [(rowid,) for rowid in random_rowids])

def reduce_database_size(db_path, target_row_count, batch_size=100):
    """Reduce the size of the database to the target row count by randomly deleting rows in batches."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        total_rows = sum(get_table_row_counts(cursor).values())
        while total_rows > target_row_count:
            table_row_counts = get_table_row_counts(cursor)
            # Choose a random table weighted by row count to delete rows from
            tables = list(table_row_counts.keys())
            weights = [table_row_counts[table] for table in tables]
            selected_table = random.choices(tables, weights=weights, k=1)[0]
            
            delete_random_rows(cursor, selected_table, batch_size)
            conn.commit()  # Commit after each batch for better performance
            
            # Update total_rows
            total_rows = sum(get_table_row_counts(cursor).values())
            print(f"Deleted rows from {selected_table}. Total rows now: {total_rows}")
    finally:
        conn.close()

def drop_not_participating_in_closure(data_path, ontology_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    try:
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        all_assertions = generate_assertions(ontology_path,cursor)

        abox_assertions = get_all_abox_assertions(tables,cursor)

        assertions = all_assertions - set(abox_assertions)

        print(len(assertions))

        supports = compute_all_supports_naive(assertions, ontology_path, cursor)
        print(sum((len(val) for val in supports.values())))

        all_supports = set()
        co = 0

        for assertion,supp_list in supports.items():
            if len(supp_list) >= 2:
                co += 1
                all_supports = all_supports.union(set(supp_list))
        
        print(f"the number of assertions with more than a single support: {co}.")

        print(len(all_supports))
        
        to_remove = set(abox_assertions) - all_supports

        print(len(to_remove))

        drop_from_db(to_remove, cursor)

        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")

def reset_table_ids(cursor, table_name):
    """
    Reset the IDs for the specified table.
    """
    # Fetching the column names except for the ID column
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall() if info[1].lower() != 'id']
    columns_joined = ', '.join(columns)
    
    # Creating a new table with the same schema but without data
    cursor.execute(f"CREATE TABLE {table_name}_new AS SELECT * FROM {table_name} WHERE 1=0")
    
    # Inserting data into the new table with resequenced IDs
    cursor.execute(f"INSERT INTO {table_name}_new ({columns_joined}) SELECT {columns_joined} FROM {table_name}")
    
    # Dropping the original table
    cursor.execute(f"DROP TABLE {table_name}")
    
    # Renaming the new table to the original table name
    cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")

def reset_all_ids(db_path):
    """
    Reset IDs for all tables in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Getting all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            print(f"Resetting IDs for {table}...")
            reset_table_ids(cursor, table)
            # Recreating the autoincrement property for the ID column, if necessary
            #cursor.execute(f"UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM {table}) WHERE name = '{table}'")
            print(f"Finished resetting IDs for {table}.")
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    data_path = "bench_prepa/dataset_small_u1/University0.db"
    ontology_path = "ontologies/univ-bench/lubm-ex-20_disjoint.owl"
    
    #drop_not_participating_in_closure(data_path, ontology_path)

    #target_row_count = 10000
    #batch_size = 1000  # Number of rows to delete per batch, adjust based on your needs
    #reduce_database_size(data_path, target_row_count, batch_size)

    data_paths = ["bench_prepa/dataset_small_u1/university0.5_p_0.000005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.00001.db", "bench_prepa/dataset_small_u1/university0.5_p_0.00005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.0005.db", "bench_prepa/dataset_small_u1/university0.5_p_0.001.db"]

    for db_path in data_paths:
        reset_all_ids(db_path)