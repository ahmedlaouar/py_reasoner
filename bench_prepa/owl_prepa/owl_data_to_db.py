import os
from rdflib import Graph, RDF, OWL
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
        
def parse_ontology(owl_file):
    g = Graph()
    g.parse(owl_file)
    return g

def create_database(graph, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tables for classes
    for class_uri in graph.subjects(predicate=RDF.type, object=OWL.Class):
        table_name = class_uri.split('#')[-1]
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, individual0 TEXT, degree INT)")

    # Create tables for properties
    for prop_uri in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty):
        table_name = prop_uri.split('#')[-1]
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, individual0 TEXT, individual1 TEXT, degree INT)")

    # Create tables for data properties
    for data_uri in graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty):
        table_name = data_uri.split('#')[-1]
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, individual0 TEXT, individual1 TEXT, degree INT)")

    conn.commit()
    conn.close()



def parse_data(owl_data_file):
    g = Graph()
    g.parse(owl_data_file)
    return g

def insert_data(graph, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    co = 0
    # Insert data for classes and properties
    for s, p, o in graph.triples((None, None, None)):
        try:
            if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                #Class parsing
                table_name = str(o).split('#')[-1]
                
                cursor.execute(f"INSERT INTO {table_name} (individual0) VALUES (?)", (str(s),))
            else:
                #ObjectProperty parsing
                table_name = str(p).split('#')[-1]
                cursor.execute(f"INSERT INTO {table_name} (individual0, individual1) VALUES (?, ?)", (str(s), str(o)))
        except sqlite3.OperationalError as e:
            co += 1
            print(f"Error: {e}.")

    print(f"Number of absent tables: {co}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    owl_file = "ontologies/univ-bench/lubm-ex-80_disjoint.owl"
    db_file = "bench_prepa/dataset.1.0/university1_lubm-ex-80.db"
    owl_data_file = "bench_prepa/dataset.1.0/university1_lubm-ex-80.owl"

    empty_database(db_file)
    graph = parse_ontology(owl_file)
    create_database(graph, db_file)

    graph_data = parse_data(owl_data_file)
    insert_data(graph_data, db_file)
