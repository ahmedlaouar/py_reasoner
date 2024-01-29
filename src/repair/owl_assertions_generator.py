

from sqlite3 import Cursor
import subprocess
from rdflib import Graph, RDF, OWL

from dl_lite.assertion import w_assertion

def rewrite_query(query: str, ontology_path: str):
    all_queries = []    
    # Path to your Java executable
    java_executable = 'java'
    # Path to your JAR file
    jar_file = 'libraries/Rapid2.jar'
    # Create a temporary file to store the content
    temp_file_path = 'src/temp/temp_query.txt'
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(query)
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
        print(f"Error executing for query {query}. Error: {e}")    
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
    elif tokens[2] == "?0":
        sql_query = f"SELECT individual1 FROM {tokens[0]}"
    return sql_query

def run_sql_query(sql_query: str, cursor: Cursor):
    results = []
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            results.append(row)
    return results

def generate_assertions(ontology_path: str,cursor: Cursor):
    # this function reads through the ontology classes and properties (concepts and roles) and finds if they have individuals with which they can be derived from the data (ABox)
    all_assertions_to_check = []
    graph = Graph()
    graph.parse (ontology_path, format='application/rdf+xml')
    #concepts = [class_uri.split('#')[-1] for class_uri in graph.subjects(predicate=RDF.type, object=OWL.Class)]
    for class_uri in graph.subjects(predicate=RDF.type, object=OWL.Class):
        concept_name = class_uri.split('#')[-1]
        query = f"Q(?0) <- {concept_name}(?0)"
        queries = rewrite_query(query,ontology_path)
        for cq_query in queries:
            sql_query = generate_sql_query(cq_query)
            results = run_sql_query(sql_query,cursor)
            if len(results) != 0:
                for result in results:
                    assertion = w_assertion(concept_name,result[0])
                    all_assertions_to_check.append(assertion)

    #roles = [prop_uri.split('#')[-1] for prop_uri in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)]
    for prop_uri in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty):
        role_name = prop_uri.split('#')[-1]
        query = f"Q(?0,?1) <- {role_name}(?0,?1)"
        queries = rewrite_query(query,ontology_path)
        for cq_query in queries:
            sql_query = generate_sql_query(cq_query)
            results = run_sql_query(sql_query,cursor)
            if len(results) != 0:
                for result in results:
                    assertion = w_assertion(role_name,result[0],result[1])
                    all_assertions_to_check.append(assertion)
    
    return all_assertions_to_check