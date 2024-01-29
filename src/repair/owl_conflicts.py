from sqlite3 import Cursor
import rdflib
import subprocess

ontology_path = 'ontologies/univ-bench/lubm-ex-20_disjoint.owl'

def get_OntologyURI(graph):
    
    test = [x for x, y, z in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Ontology))]

    if test:
        return str(test[0])
    else:
        return None
    
def get_negative_axioms(ontology_path :str):
    # this function goes through the ontology and returns "disjointWith" and "propertyDisjointWith" as negative axioms
    graph = rdflib.Graph()
    graph.parse (ontology_path, format='application/rdf+xml')
    
    namespace = get_OntologyURI(graph)
    prefix = rdflib.Namespace(namespace)
    graph.bind("", prefix)

    query1 = """
    select distinct ?s ?p ?o 
    where { ?s owl:disjointWith ?o}
            """
    query2 = """
    select distinct ?s ?p ?o 
    where { ?s owl:propertyDisjointWith ?o}
            """
    
    result1 = graph.query(query1)
    
    negative_axioms = []

    for row in result1.bindings:
        s = graph.qname(row['s']) if 's' in row and row['s'] else str(row['s'])
        o = graph.qname(row['o']) if 'o' in row and row['o'] else str(row['o'])
        negative_axioms.append(f"{s},owl:disjointWith,{o}")

    result2 = graph.query(query2)
    
    for row in result2.bindings:
        s = graph.qname(row['s']) if 's' in row and row['s'] else str(row['s'])
        o = graph.qname(row['o']) if 'o' in row and row['o'] else str(row['o'])
        negative_axioms.append(f"{s},owl:propertyDisjointWith,{o}")
    
    return negative_axioms


def generate_query(axiom):
    # from a negative axiom generate a conjunctive query, here with 2 atoms since we use DL-Lite_R
    ax = axiom.split(",")
    if ax[1] == "owl:disjointWith" :
        query = f"Q(?0) <- {ax[0]}(?0), {ax[2]}(?0)"
    elif ax[1] == "owl:propertyDisjointWith" :
        query = f"Q(?0,?1) <- {ax[0]}(?0,?1), {ax[2]}(?0,?1)"
    else :
        return ""
    return query


"""def rewrite_query(query,ontology_path :str):
    # this function calls Rapid2.jar to rewrite a query with an ontology (this step replaces the computation of cln(TBox))
    # cln(TBox) is the negative closure of the TBox which is the exhaustive list of all the negative axioms that we can infer from a TBox
    # for space complexity reasons, the step of the computation cln(TBox) (a preprocessing of the ontology) is moved to compute_conflicts step 
    # can be moved back if time complexity is more concerning here
    all_queries = []    
    # Path to your Java executable
    java_executable = 'java'
    # Path to your JAR file
    jar_file = 'libraries/Rapid2.jar'
    # Create a temporary file to store the content
    temp_file_path = 'src/temp/temp_query_conflicts.txt'
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
    
    return all_queries"""

def rewrite_all_queries(queries: list,ontology_path: str):
    all_queries = []
    # Path to your Java executable
    java_executable = 'java'
    # Path to your JAR file
    jar_file = 'libraries/Rapid2.jar'
    # Create a temporary file to store the content
    temp_file_path = 'src/temp/temp_query_conflicts.txt'
    with open(temp_file_path, 'w') as temp_file:
        for query in queries:
            temp_file.write(query + '\n')
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
    

def generate_sql_query(query_str):
    # this function generates a sql query from a conjunctive query, it assumes the query to have just 2 atoms
    # it returns the sql_query alongside table names to faciliate construction of conlicts
    query = query_str.replace(' ', '').replace('),', '), ').split()
    # split query into two sides
    first, second = query[:2]        
    # tokenize each side and remove commas and parenthesis
    first_tokens = [token for token in first.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    second_tokens= [token for token in second.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    # find matching elements between first and second tokens
    matching_indexes = [(i, j) for i, item1 in enumerate(first_tokens[1:]) for j, item2 in enumerate(second_tokens[1:]) if item1 == item2]
    # Insert here a verification that the integrity of the TBox (the coherence), if not exit and show error message
    # if first_tokens[0] == second_tokens[0]: print("Warrning : The TBox is not coherent, reasoning is not possible")
    # Generate query according to matches
    sql_query = f"SELECT t1.id,t1.degree,t2.id,t2.degree FROM {first_tokens[0]} t1 JOIN {second_tokens[0]} t2 ON"
    for (index0,index1) in matching_indexes:
        sql_query += " t1.individual"+str(index0)+" = t2.individual"+str(index1)+" and"
    # remove last trailing "and"
    sql_query = sql_query.rsplit(' ', 1)[0]
    return sql_query, first_tokens[0], second_tokens[0]

def run_sql_query(sql_query:str,cursor: Cursor, table1:str, table2:str):
    # this function takes a query for conflicts and gets the ids of the conflicting elements
    # we limit only ids for space considerations, we can use ids later to get assertions
    conflicts = []
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            conflicts.append(((table1, row[0], row[1]),(table2, row[2], row[3])))      
    return conflicts

def compute_conflicts(ontology_path :str, cursor: Cursor):
    conflicts = []
    # analyze ontology and return disjointWith and propertyDisjointWith as negative axioms
    negative_axioms = get_negative_axioms(ontology_path)
    # "queries" are generated from each negative axiom in the TBox
    queries = []
    for axiom in negative_axioms:
        queries.append(generate_query(axiom))
    # "all_queries" are the result of rewriting all "queries"
    all_queries = []
    all_queries = rewrite_all_queries(queries,ontology_path)
    #for query in queries:
    #    all_queries += rewrite_query(query,ontology_path)
    # generate sql query from each conjunctive query
    for query in all_queries:
        sql_query, table1, table2 = generate_sql_query(query)
        conflicts += run_sql_query(sql_query, cursor, table1, table2)
    return conflicts
