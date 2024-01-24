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
    
    print(negative_axioms)
    return negative_axioms

#print(get_negative_axioms(ontology_path))

def generate_queries(negative_axioms):
    queries = []
    for axiom in negative_axioms:
        ax = axiom.split(",")
        if ax[1] == "owl:disjointWith" :
            queries.append(f"Q(?0) <- {ax[0]}(?0), {ax[2]}(?0)")
        elif ax[1] == "owl:propertyDisjointWith" :
            queries.append(f"Q(?0,?1) <- {ax[0]}(?0,?1), {ax[2]}(?0,?1)")
    return queries

#print(generate_queries(get_negative_axioms(ontology_path)))

def rewrite_queries(queries,ontology_path :str):
    all_queries = []
    
    for query in queries:
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


#queries = generate_queries(get_negative_axioms(ontology_path))
#all_queries = rewrite_queries(queries,ontology_path)
#print(all_queries)
#temp_file_path = 'src/temp/temp_query.txt'
#with open(temp_file_path,'w') as temp_file:
    # Write each element of the list to a new line in the file
#    for query in all_queries:
#        temp_file.write(f"{query}\n")

def generate_sql_query(query_str):
    query = query_str.replace(' ', '').replace('),', '), ').split()
    #split query into two sides
    first, second = query[:2]        
    #tokenize each side and remove commas and parenthesis
    first_tokens = [token for token in first.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    second_tokens= [token for token in second.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
    #find matching elements between first and second tokens
    matching_indexes = [(i, j) for i, item1 in enumerate(first_tokens[1:]) for j, item2 in enumerate(second_tokens[1:]) if item1 == item2]
    #Generate query according to matches
    sql_query = f"SELECT * FROM {first_tokens[0]} t1 JOIN {second_tokens[0]} t2 ON"
    for (index0,index1) in matching_indexes:
        sql_query += " t1.individual"+str(index0)+" = t2.individual"+str(index1)+" and"
    #remove last trailing and
    sql_query = sql_query.rsplit(' ', 1)[0]
    return sql_query, first_tokens[0], second_tokens[0]

def run_sql_query(sql_query:str,cursor, table1:str, table2:str):
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    #for row in rows:
    #Here process rows and associate them with tables names

def compute_conflicts(ontology_path :str, cursor):
    conflicts = []
    negative_axioms = get_negative_axioms(ontology_path)
    queries = generate_queries(negative_axioms)
    all_queries = rewrite_queries(queries,ontology_path)
    for query in all_queries:
        sql_query, table1, table2 = generate_sql_query(query)
        conflicts += run_sql_query(sql_query, table1, table2)
    return conflicts