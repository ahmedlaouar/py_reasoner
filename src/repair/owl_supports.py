from sqlite3 import Cursor
import subprocess
import time
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
        sql_query = f"SELECT id,degree FROM '{tokens[0]}' WHERE individual0='{tokens[1]}'"
    elif tokens[1][0] == "?":
        sql_query = f"SELECT id,degree FROM '{tokens[0]}' WHERE individual1='{tokens[2]}'"
    elif tokens[2][0] == "?":
        sql_query = f"SELECT id,degree FROM '{tokens[0]}' WHERE individual0='{tokens[1]}'"
    else:
        sql_query = f"SELECT id,degree FROM '{tokens[0]}' WHERE individual0='{tokens[1]}' AND individual1='{tokens[2]}'"
    return sql_query, tokens[0]

def run_sql_query(sql_query: str,table_name: str, cursor: Cursor):
    supports = []
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            supports.append((table_name, row[0], row[1]))
    return supports

def compute_all_supports(assertions: list, ontology_path: str, cursor: Cursor, pos_dict):
    # in this version we use a seperation query, in order to perform a single rewriting with Rapid2.jar, because multiple calls to it is bad for time complexity
    supports = {}
    queries = []
    time1 = time.time()
    for assertion in assertions:
        assertion_name = assertion.get_assertion_name()
        individual0, individual1 = assertion.get_individuals()
        if individual1 != None:
            queries.append(f"Q({individual0},{individual1}) <- {assertion_name}({individual0},{individual1})")
        else:
            queries.append(f"Q({individual0}) <- {assertion_name}({individual0})")
        queries.append(separation_query)
    time2 = time.time()
    print(f"Time to generate all BCQs {time2 - time1}, number of BCQs {len(queries)}")
    all_queries = rewrite_queries(queries,ontology_path)
    time3 = time.time()
    print(f"Time to rewrite all BCQs {time3 - time2}, number of rewritings {len(all_queries)}")
    
    assertions_counter = 0
    supports[assertions_counter] = []
    for query in all_queries:
        if query == "BornIN(AHMED, SKIKDA)":
            assertions_counter += 1
            supports[assertions_counter] = []
            continue
        sql_query, table_name = generate_sql_query(query)
        some_supports = run_sql_query(sql_query,table_name,cursor)
        for new_element in some_supports:
            if not any(dominates(pos_dict, [support], [new_element]) for support in supports[assertions_counter]):
                to_remove = {support for support in supports[assertions_counter] if dominates(pos_dict, [new_element], [support])}
                if to_remove:
                    supports[assertions_counter] = [x for x in supports[assertions_counter] if x not in to_remove]                
                supports[assertions_counter].append(new_element)      
    time4 = time.time()
    print(f"Time to generate and run all SQL queries {time4 - time3}")
    return supports


"""def compute_supports(assertion : w_assertion, ontology_path: str, cursor: Cursor):
    assertion_name = assertion.get_assertion_name()
    individual0, individual1 = assertion.get_individuals()
    if individual1 != None:
        query = f"Q({individual0},{individual1}) <- {assertion_name}({individual0},{individual1})"
    else:
        query = f"Q({individual0}) <- {assertion_name}({individual0})"
    queries = rewrite_query(query,ontology_path)
    supports = []
    for query in queries:
        sql_query, table_name = generate_sql_query(query)
        supports += run_sql_query(sql_query,table_name,cursor)
    return supports"""