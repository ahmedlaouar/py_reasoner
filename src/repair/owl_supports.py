from sqlite3 import Cursor
import subprocess
from dl_lite.assertion import w_assertion

ontology_path = 'ontologies/univ-bench/lubm-ex-20_disjoint.owl'

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
    # it returns the sql_query alongside table name to faciliate construction of supports
    tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    if len(tokens) == 2:
        sql_query = f"SELECT t.id,t.degree FROM {tokens[0]} t WHERE t.individiual0={tokens[1]}"
    elif tokens[1][0] == "?":
        sql_query = f"SELECT t.id,t.degree FROM {tokens[0]} t WHERE t.individiual1={tokens[2]}"
    elif tokens[2][0] == "?":
        sql_query = f"SELECT t.id,t.degree FROM {tokens[0]} t WHERE t.individiual0={tokens[1]}"
    else:
        sql_query = f"SELECT t.id,t.degree FROM {tokens[0]} t WHERE t.individiual0={tokens[1]} AND t.individual1={tokens[2]}"
    return sql_query, tokens[0]

def run_sql_query(sql_query: str,table_name: str, cursor: Cursor):
    supports = []
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            supports.append((table_name, row[0], row[1]))
    return supports

def compute_supports(assertion : w_assertion, ontology_path: str, cursor: Cursor):
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
    return supports

#assertion = w_assertion("memberOf","Bob","University54",weight=57)
#queries = compute_supports(assertion,ontology_path,None)
#for query in queries:
#    print(query)