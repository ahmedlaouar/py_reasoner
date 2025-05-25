import argparse
import time
from logzero import logger
from rdflib import Graph, RDF, OWL, RDFS
import psycopg2
from psycopg2 import sql
from handlers.abox_handler import ABoxHandler
from handlers.ontology_handler import OntologyHandler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def empty_database(conn):
    """
    Empties all user-defined tables in the PostgreSQL database.
    """
    logger.debug("Emptying database...")

    cursor = conn.cursor()
    try:
        # Get all tables in the 'public' schema (user-defined tables)
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()

        # Drop all tables
        for table in tables:
            cursor.execute(f'DROP TABLE "{table[0]}" CASCADE;')

        logger.debug("Successfully dropped all tables.")

    except psycopg2.Error as e:
        logger.debug(f"Error: {e}")

    conn.commit()
    cursor.close()
        
def create_database(ontologyHandler, conn):
    """
    Creates a PostgreSQL database schema from an OWL ontology.
    """
    logger.debug(f"Creating a connection to database, Creating tables from ontology...")
    
    cursor = conn.cursor()
    try:
        # Create tables for OWL classes
        logger.debug("Creating tables for OWL classes")
        for class_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.Class):
            table_name = class_uri
            query = sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name))
            cursor.execute(query)

        # Create tables for OWL object properties
        logger.debug("Creating tables for OWL object properties")
        for prop_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty):
            table_name = prop_uri
            query = sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    individual1 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name))
            cursor.execute(query)

        # Create tables for OWL datatype properties
        logger.debug("Creating tables for OWL datatype properties")
        for data_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty):
            table_name = data_uri
            query = sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    individual1 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name))
            cursor.execute(query)

        """Some classes are not declared with RDF.type triples, but they're only present with rdfs:subClassOf, owl:equivalentClass or owl:disjointWith axioms
        Also some classes have a different namespace, so carefully cope with every prefix!"""

        logger.debug("Creating tables for subclass, equivalent, and disjoint class relations")
        for _, _, class_uri in ontologyHandler.graph.triples((None, RDFS.subClassOf, None)):
            table_name = class_uri
            cursor.execute(sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name)))
            #cursor.execute(query)

        for _, _, class_uri in ontologyHandler.graph.triples((None, OWL.equivalentClass, None)):
            table_name = class_uri
            cursor.execute(sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name)))
            #cursor.execute(query)

        for _, _, class_uri in ontologyHandler.graph.triples((None, OWL.disjointWith, None)):
            table_name = class_uri
            cursor.execute(sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name)))
            #cursor.execute(query)

        # Handle sub-properties
        logger.debug("Creating tables for sub-properties")
        for _, _, prop_uri in ontologyHandler.graph.triples((None, RDFS.subPropertyOf, None)):
            table_name = prop_uri
            cursor.execute(sql.SQL('''
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    individual0 TEXT,
                    individual1 TEXT,
                    derivationTimestamp TIMESTAMP WITH TIME ZONE,
                    wikiTimestamp TIMESTAMP WITH TIME ZONE,
                    source TEXT,
                    degree INT
                )
            ''').format(sql.Identifier(table_name)))
            #cursor.execute(query)
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        logger.debug(f"Error: {e}")

def safe_uri(uri):
    if uri:
        # Replace all problematic characters
        return f"{uri.replace(',', '%2C').replace('(', '%28').replace(')', '%29').replace("\'", '%27')}"
    return None

def insert_data(ttl_file, conn):
    """
    Reads RDF triples from a TTL file and inserts them into a PostgreSQL database.
    """
    cursor = conn.cursor()
    co = 0  # Counter for tables not found
    tab_num = 0
    not_inserted = 0

    logger.debug(f"Processing data file {ttl_file}...")

    with open(ttl_file, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                continue  # Skip comments

            try:
                # process each line: exmaple of line <http://dbpedia.org/resource/I_Could_Use_Another_You>|<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>|<http://dbpedia.org/ontology/Single>|"2022-11-17T12:14:46Z"^^xsd:dateTime|"2024-08-12T23:32:57Z"^^xsd:dateTime|instance_types_lhd_dbo_en
                line_list = line.strip().split("|")
                s = safe_uri(line_list[0][1:-1])  # Subject
                p = safe_uri(line_list[1][1:-1])  # Predicate
                o = safe_uri(line_list[2][1:-1])  # Object
                # Get derivationTimestamp
                t1_raw = line_list[3].split("^^")[0][1:-1]
                t1 = t1_raw if t1_raw else None  # Convert empty string to None
                # Get wikiTimestamp
                t2_raw = line_list[4].split("^^")[0][1:-1]
                t2 = t2_raw if t2_raw else None  # Convert empty string to None
                src = line_list[5]  # Source
                # Ensure we only process class insertions
                if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    table_name = o  # Ensure valid table names

                    query = sql.SQL('''
                        INSERT INTO {} (individual0, derivationTimestamp, wikiTimestamp, source) 
                        VALUES (%s, %s, %s, %s)
                    ''').format(sql.Identifier(table_name))

                    cursor.execute(query, (s, t1, t2, src))
                    tab_num += 1
                else:
                    not_inserted += 1
                    logger.debug(f"Skipped: line {line.strip()} not inserted!")

                    # ObjectProperty parsing
                    #table_name = p #.split('#')[-1]
                    #cursor.execute('INSERT INTO "{}" (individual0, individual1) VALUES (?, ?)'.format(table_name), (s, o))
            except psycopg2.Error as e:
                co += 1
                logger.debug(f"Database Error: {e}")
                conn.rollback()  # Reset the transaction so future queries work
                continue

    conn.commit()

    logger.debug(f"Processed assertions: {tab_num}, Not inserted: {not_inserted}, Absent tables: {co}")

    cursor.close()

def create_all_preferences_table(conn):
    """Creates a Table to store the relation NotGreater(\varphi_1,\varphi_2), useful for consistency checking approach."""
    logger.debug(f"Creating a connection to database, Creating tables from ontology...")
    
    cursor = conn.cursor()
    try:
        # Create the NotGreater table
        logger.debug("Creating NotGreater helper table")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS NotGreater (
                table1 TEXT NOT NULL,
                id1 INT NOT NULL,
                table2 TEXT NOT NULL,
                id2 INT NOT NULL,
                PRIMARY KEY (table1, id1, table2, id2)
            );
        ''')

        cursor.execute('''
            CREATE TEMP TABLE all_facts (
            table_name TEXT NOT NULL,
            id INT NOT NULL,
            derivationTimestamp TIMESTAMP WITH TIME ZONE,
            wikiTimestamp TIMESTAMP WITH TIME ZONE,
            source TEXT,
            PRIMARY KEY (table_name, id)
        );
        ''')

        start_time = time.time()
        
        # Get all table names in public schema
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        all_tables = [row[0] for row in cursor.fetchall()]
        tables = []
        for table_name in all_tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            if cursor.fetchone()[0] != 0:
                tables.append(table_name)

        for t in tables:
            if t.lower() == 'notgreater':
                continue
            cursor.execute(sql.SQL(
                '''INSERT INTO all_facts (table_name, id, derivationTimestamp, wikiTimestamp, source)
                SELECT %s, id, derivationTimestamp, wikiTimestamp, source FROM {}'''
            ).format(sql.Identifier(t)), [t])

        cursor.execute(f'SELECT COUNT(*) FROM all_facts')
        total_rows = cursor.fetchone()[0]
        mid_time = time.time()
        logger.debug(f'Finished insering all rows from all tables, result: {total_rows} rows, to the TEMP TABLE all_facts in {mid_time - start_time}.')

        query = """
            INSERT INTO NotGreater (table1, id1, table2, id2)
            SELECT a.table_name, a.id, b.table_name, b.id
            FROM all_facts a JOIN all_facts b 
            ON (
            (a.table_name <> b.table_name AND a.id <> b.id) AND (
                (
                    (a.derivationTimestamp IS NOT NULL AND b.derivationTimestamp IS NOT NULL AND a.derivationTimestamp <= b.derivationTimestamp) AND
                    (a.wikiTimestamp IS NOT NULL AND b.wikiTimestamp IS NOT NULL AND a.wikiTimestamp <= b.wikiTimestamp) AND
                    (a.source != 'instance-types_lang=en_specific' OR b.source != 'instance_types_lhd_dbo_en')
                )
                OR (
                    (b.source = 'instance-types_lang=en_specific' AND a.source = 'instance_types_lhd_dbo_en') OR
                    (a.derivationTimestamp IS NOT NULL AND b.derivationTimestamp IS NOT NULL AND b.derivationTimestamp > a.derivationTimestamp) OR
                    (a.wikiTimestamp IS NOT NULL AND b.wikiTimestamp IS NOT NULL AND b.wikiTimestamp > a.wikiTimestamp)
                )
            )
            );    
        """

        cursor.execute(query)
        
        end_time = time.time()
        
        logger.debug(f"Time spent: {end_time - start_time:.2f} seconds.")

        conn.commit()
        logger.debug("Finished populating NotGreater table")
        cursor.close()
    except psycopg2.Error as e:
        logger.debug(f"Error: {e}")
        conn.rollback()

def main(tBox_file, data_files):
    aboxHandler = ABoxHandler()
    CONN = aboxHandler.connect()

    # only execute the following line the first time to create a clean database
    empty_database(CONN)  # Done

    # import the ontology into rdflib graph from owl file
    ontologyHandler = OntologyHandler(tBox_file, format='application/rdf+xml')
    
    # create the database
    create_database(ontologyHandler, CONN)  # Done

    # add data from ttl files to database
    for data_file in data_files:
        insert_data(data_file, CONN)

    create_all_preferences_table(CONN)

    aboxHandler.disconnect()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Please provide an ontology owl file (tbox) and a csv data file (abox).")
    parser.add_argument("tbox", help="path to the ontology file.")
    parser.add_argument("abox", help="path to the csv data file.")
    args = parser.parse_args()

    tBox_file = args.tbox # "ontologies/DBO/ontology--DEV_type=parsed.owl" #"ontologies/DBO/ontology_type=parsed.owl" #

    data_file = args.abox

    main(tBox_file, [data_file])
    
    """
    tBox_file = "ontologies/DBO/ontology--DEV_type=parsed.owl" #"ontologies/DBO/ontology_type=parsed.owl" #
    data_files = ["dataset_preparation/instance_types_lhd_dbo_en_with_timestamps.csv", "dataset_preparation/instance-types_lang=en_specific_with_timestamps.csv"]
    main(tBox_file, data_files)
    """