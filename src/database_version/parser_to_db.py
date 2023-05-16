import psycopg2
import os

database_name = "test_abox"
project_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_directory, f"{database_name}.db")

conn = psycopg2.connect(
    host="localhost",
    user="py_reasoner",
    password="py_reasoner"
)
# Disable autocommit mode to avoid error: DROP DATABASE cannot run inside a transaction block
conn.autocommit = True

cursor = conn.cursor()
# Drop the database if it exists
cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")

# Commit the drop database statement
conn.commit()

#see how to fix this later
#table_space_query = f"CREATE TABLESPACE test_abox LOCATION '/Documents/Phd_work/Cpi-repair_impl/py_reasoner/';"
#cursor.execute(table_space_query)

create_database_query = f"CREATE DATABASE {database_name} OWNER py_reasoner TEMPLATE template0;" # TABLESPACE {database_name};"
cursor.execute(create_database_query)

conn.commit()
cursor.close()
conn.close()

conn = psycopg2.connect(
    host="localhost",
    database=database_name,
    user="py_reasoner",
    password="py_reasoner"
)

cursor = conn.cursor()

cursor.execute(f'''
    drop schema if exists {database_name} cascade;
    CREATE schema {database_name};
    SET search_path to {database_name};
''')

conn.commit()
cursor.close()
conn.close()