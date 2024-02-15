from sqlite3 import Cursor
import subprocess
from rdflib import Graph, RDF, OWL
from dl_lite.assertion import w_assertion

separation_query = "Q(AHMED, SKIKDA) <- BornIN(AHMED, SKIKDA)"

def rewrite_queries(queries: list, ontology_path: str):
    all_queries = []    
    # Path to your Java executable
    java_executable = 'java'
    # Path to your JAR file
    jar_file = 'libraries/Rapid2.jar'
    # Create a temporary file to store the content
    temp_file_path = 'src/temp/temp_query_generation.txt'
    with open(temp_file_path, 'w') as temp_file:
        temp_file.writelines(query + '\n' for query in queries)
    try:
        # Run the JAR file with the temporary file path as an argument
        result_bytes = subprocess.check_output([java_executable, '-jar', jar_file, "DU", "SHORT", ontology_path, temp_file_path])
        #for line in result:print(result)
        result = result_bytes.decode('utf-8').strip()
        results = result.split('\n')
        for i in range(1,len(results)):
            to_append = results[i].split("<-")[1].strip() # Remove the first part of query before Q(?0) <- as it's not useful for SQL querying then Strip to remove leading/trailing whitespaces
            all_queries.append(to_append)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Rapid2.jar. Error: {e}")    
    return all_queries

def generate_sql_query(query: str):
    # this function generates a sql query from a conjunctive query, it assumes the query to have just 1 atom
    tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    if len(tokens) == 2:
        sql_query = f"SELECT individual0 FROM {tokens[0]}"
    elif tokens[1] == "?0" and tokens[2] == "?1":
        sql_query = f"SELECT individual0,individual1 FROM {tokens[0]}"
    elif tokens[2] == "?0" and tokens[1] == "?1":
        sql_query = f"SELECT individual1,individual0 FROM {tokens[0]}"
    elif tokens[1] == "?0":
        sql_query = f"SELECT individual0 FROM {tokens[0]}"
    else : #if tokens[2] == "?0":
        sql_query = f"SELECT individual1 FROM {tokens[0]}"
    return sql_query

def generate_assertions(ontology_path: str,cursor: Cursor):
    # this function reads through the ontology classes and properties (concepts and roles) and finds if they have individuals with which they can be derived from the data (ABox)
    all_assertions_to_check = set()
    graph = Graph()
    graph.parse (ontology_path, format='application/rdf+xml')

    concepts = [class_uri.split('#')[-1] for class_uri in graph.subjects(predicate=RDF.type, object=OWL.Class)]
    concept_queries = []    
    for concept_name in concepts:
        concept_queries.append(f"Q(?0) <- {concept_name}(?0)")
        concept_queries.append(separation_query)
    all_concept_queries = rewrite_queries(concept_queries,ontology_path)
    assertions_counter = 0
    for cq_query in all_concept_queries:
        if cq_query == "BornIN(AHMED, SKIKDA)":
            assertions_counter += 1
            continue
        sql_query = generate_sql_query(cq_query)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if len(results) != 0:
            for result in results:
                if len(result) == 1:
                    assertion = w_assertion(concepts[assertions_counter],result[0])
                    all_assertions_to_check.add(assertion)
    
    roles = [prop_uri.split('#')[-1] for prop_uri in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)] #+ [data_uri.split('#')[-1] for data_uri in graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty)]
    role_queries = []
    for role_name in roles:
        role_queries.append(f"Q(?0,?1) <- {role_name}(?0,?1)")
        role_queries.append(separation_query)
    all_role_queries = rewrite_queries(role_queries,ontology_path)    
    assertions_counter = 0
    for cq_query in all_role_queries:
        if cq_query == "BornIN(AHMED, SKIKDA)":
            assertions_counter += 1
            continue
        sql_query = generate_sql_query(cq_query)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if len(results) != 0:
            for result in results:
                if len(result) == 2:
                    assertion = w_assertion(roles[assertions_counter],result[0],result[1])
                    all_assertions_to_check.add(assertion)
    
    return all_assertions_to_check

def get_all_abox_assertions(tables: list,cursor: Cursor):
    all_assertions = []
    for table in tables:
        sql_query = f"SELECT * FROM {table[0]};"
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if len(results) != 0:
            for result in results:
                if len(result) == 3:
                    assertion = w_assertion(table[0],result[1],weight=result[2])
                    all_assertions.append(assertion)
                if len(result) == 4:
                    assertion = w_assertion(table[0],result[1],result[2],weight=result[3])
                    all_assertions.append(assertion)
    return all_assertions