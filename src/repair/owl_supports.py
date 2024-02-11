from sqlite3 import Cursor
import subprocess
import time

from rdflib import OWL, RDF, Graph
from dl_lite.assertion import w_assertion
from repair.owl_dominance import dominates

separation_query = "Q(AHMED, SKIKDA) <- BornIN(AHMED, SKIKDA)"

def rewrite_queries(queries: list, ontology_path: str):
    all_queries = []    
    # Path to your Java executable
    java_executable = 'java'
    # Path to your JAR file
    jar_file = 'libraries/Rapid2.jar'
    # Create a temporary file to store the queries
    temp_file_path = 'src/temp/temp_query_supports.txt'
    with open(temp_file_path, 'w') as temp_file:
        temp_file.writelines(query + '\n' for query in queries)
    try:
        # Run the JAR file with the temporary file path as an argument
        result_bytes = subprocess.check_output([java_executable, "-Xmx8g", '-jar', jar_file, "DU", "SHORT", ontology_path, temp_file_path])
        result = result_bytes.decode('utf-8').strip()
        results = result.split('\n')
        for i in range(1,len(results)):
            all_queries.append(results[i].split("<-")[1].strip()) # Remove the first part of query before Q(?0) <- as it's not useful for SQL querying then Strip to remove leading/trailing whitespaces
    except subprocess.CalledProcessError as e:
        print(f"Error executing Rapid2.jar. Error: {e}")    
    return all_queries

def generate_sql_query(query: str):
    # this function generates a sql query from a conjunctive query, it assumes the query to have just 1 atom
    # it returns the sql_query alongside table name to faciliate construction of supports
    tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    if len(tokens) == 2:
        sql_query = f"SELECT * FROM '{tokens[0]}' WHERE individual0='{tokens[1]}'"
    elif tokens[1][0] == "?":
        sql_query = f"SELECT * FROM '{tokens[0]}' WHERE individual1='{tokens[2]}'"
    elif tokens[2][0] == "?":
        sql_query = f"SELECT * FROM '{tokens[0]}' WHERE individual0='{tokens[1]}'"
    else:
        sql_query = f"SELECT * FROM '{tokens[0]}' WHERE individual0='{tokens[1]}' AND individual1='{tokens[2]}'"
    return sql_query, tokens[0]

def run_sql_query(sql_query: str,table_name: str, cursor: Cursor):
    supports = []
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            if len(row) == 3:
                supports.append((table_name, row[1], None, row[2]))
            if len(row) == 4:
                supports.append((table_name, row[1], row[2], row[3]))
    return supports

def compute_all_supports(assertions, ontology_path: str, cursor: Cursor, pos_dict):
    # in this version we use a seperation query, in order to perform a single rewriting with Rapid2.jar, because multiple calls to it is bad for time complexity

    queries = []
    time1 = time.time()
    assertions_list = list(assertions)
    for assertion in assertions_list:
        assertion_name = assertion.get_assertion_name()
        individuals = [ind for ind in assertion.get_individuals() if ind is not None]
        query_format = f"Q({', '.join(individuals)}) <- {assertion_name}({', '.join(individuals)})"
        queries.append(query_format)
        queries.append(separation_query)
    time2 = time.time()
    print(f"Time to generate all BCQs {time2 - time1}, number of BCQs {len(queries)}")
    all_queries = rewrite_queries(queries,ontology_path)
    time3 = time.time()
    print(f"Time to rewrite all BCQs {time3 - time2}, number of rewritings {len(all_queries)}")
    
    cqueries = {}
    start_index = 0
    for assertion in assertions_list:
        end_index = all_queries.index("BornIN(AHMED, SKIKDA)", start_index)
        cqueries[assertion] = all_queries[start_index:end_index]
        start_index = end_index + 1    
    
    supports = {}
    for assertion in cqueries.keys():
        supports[assertion] = set()
        for query in cqueries[assertion]:            
            sql_query, table_name = generate_sql_query(query)
            some_supports = run_sql_query(sql_query,table_name,cursor)
            if len(some_supports) != 0:            
                for new_element in some_supports:
                    if not any(dominates(pos_dict, [support], [new_element]) for support in supports[assertion]):
                        to_remove = {support for support in supports[assertion] if dominates(pos_dict, [new_element], [support])}
                        if to_remove:
                            supports[assertion] = supports[assertion] - to_remove
                        supports[assertion].add(new_element)
    time4 = time.time()
    print(f"Time to generate and run all SQL queries {time4 - time3}")
    return supports

def compute_all_supports_enhanced(assertions, ontology_path: str, cursor: Cursor, pos_dict):
    # in this version we verify if a support of an assetion is in pi_repair, if so, assertion is accepted in cpi directly    
    queries = []
    assertions_list = list(assertions)
    for assertion in assertions_list:
        assertion_name = assertion.get_assertion_name()
        individuals = [ind for ind in assertion.get_individuals() if ind is not None]
        query_format = f"Q({', '.join(individuals)}) <- {assertion_name}({', '.join(individuals)})"
        queries.append(query_format)
        queries.append(separation_query)
    all_queries = rewrite_queries(queries,ontology_path)
    
    cqueries = {}
    start_index = 0
    for assertion in assertions_list:
        end_index = all_queries.index("BornIN(AHMED, SKIKDA)", start_index)
        cqueries[assertion] = all_queries[start_index:end_index]
        start_index = end_index + 1
    
    # This filtering step assumes that an assertion is present only once with one weight in the database, so if a query of an assertion has only one rewriting it will return one element from the sql DB
    cqueries = {key: value for key, value in cqueries.items() if len(value) > 1}
    
    supports = {}
    for assertion in cqueries.keys():
        supports[assertion] = set()
        for query in cqueries[assertion]:            
            sql_query, table_name = generate_sql_query(query)
            some_supports = run_sql_query(sql_query,table_name,cursor)
            if len(some_supports) != 0:            
                for new_element in some_supports:
                    if not any(dominates(pos_dict, [support], [new_element]) for support in supports[assertion]):
                        to_remove = {support for support in supports[assertion] if dominates(pos_dict, [new_element], [support])}
                        if to_remove:
                            supports[assertion] = supports[assertion] - to_remove
                        supports[assertion].add(new_element)

    return supports

def compute_cl_pi_repair(ontology_path: str, pi_repair):
    graph = Graph()
    graph.parse (ontology_path, format='application/rdf+xml')

    cl_pi_repair = set()

    concepts = [class_uri.split('#')[-1] for class_uri in graph.subjects(predicate=RDF.type, object=OWL.Class)]
    concept_queries = []
    for concept_name in concepts:
        concept_queries.append(f"Q(?0) <- {concept_name}(?0)")
        concept_queries.append(separation_query)
    all_concept_queries = rewrite_queries(concept_queries,ontology_path)

    ref_queries = {}
    start_index = 0
    for concept in concepts:
        end_index = all_concept_queries.index("BornIN(AHMED, SKIKDA)", start_index)
        ref_queries[concept] = all_concept_queries[start_index:end_index]
        start_index = end_index + 1

    for assertion in pi_repair:
        for concept in ref_queries:
            if assertion.get_assertion_name() == concept: continue
            for query in ref_queries[concept]:
                tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
                if assertion.get_assertion_name() == tokens[0]:
                    if tokens[1] == "?0": 
                        temp_assertion = w_assertion(concept,assertion.get_individuals()[0],weight=assertion.get_assertion_weight())
                    elif tokens[2] == "?0":
                        temp_assertion = w_assertion(concept,assertion.get_individuals()[1],weight=assertion.get_assertion_weight())
                    cl_pi_repair.add(temp_assertion)

    roles = [prop_uri.split('#')[-1] for prop_uri in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)] + [data_uri.split('#')[-1] for data_uri in graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty)]
    role_queries = []
    for role_name in roles:
        role_queries.append(f"Q(?0,?1) <- {role_name}(?0,?1)")
        role_queries.append(separation_query)
    all_role_queries = rewrite_queries(role_queries,ontology_path)
    ref_queries = {}
    start_index = 0
    for role in roles:
        end_index = all_role_queries.index("BornIN(AHMED, SKIKDA)", start_index)
        ref_queries[role] = all_role_queries[start_index:end_index]
        start_index = end_index + 1

    for assertion in pi_repair:
        for role in ref_queries:
            if assertion.get_assertion_name() == role: continue
            for query in ref_queries[role]:
                tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
                if len(tokens) < 3 : continue
                if assertion.get_assertion_name() == tokens[0]:
                    if tokens[1] == "?0":
                        temp_assertion = w_assertion(role,assertion.get_individuals()[0],assertion.get_individuals()[1],weight=assertion.get_assertion_weight())
                    elif tokens[2] == "?0":
                        temp_assertion = w_assertion(role,assertion.get_individuals()[1],assertion.get_individuals()[0],weight=assertion.get_assertion_weight())
                    cl_pi_repair.add(temp_assertion)
    
    return cl_pi_repair
