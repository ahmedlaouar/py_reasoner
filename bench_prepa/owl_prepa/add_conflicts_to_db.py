import random
import subprocess
import rdflib
import sqlite3

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
        return None
    return query

def rewrite_query(query,ontology_path :str):
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

def add_conflicts(ontology_path, cursor, p):
    # analyze ontology and return disjointWith and propertyDisjointWith as negative axioms
    negative_axioms = get_negative_axioms(ontology_path)
    # "queries" are generated from each negative axiom in the TBox
    queries = []
    for axiom in negative_axioms:
        queries.append(generate_query(axiom))
    print(len(queries))
    # "all_queries" are the result of rewriting all "queries"
    all_queries = []
    for query in queries:
        all_queries += rewrite_query(query,ontology_path)
    print(len(all_queries))
    for query in all_queries:
        query = query.replace(' ', '').replace('),', '), ').split()
        # split query into two sides
        first, second = query[:2]       
        # tokenize each side and remove commas and parenthesis
        first_tokens = [token for token in first.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
        second_tokens= [token for token in second.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
        if len(first_tokens) == 2 and len(second_tokens) == 2:
            sql_query = f"SELECT individual0 FROM {first_tokens[0]};"
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if len(rows) != 0:
                for row in rows:
                    if random.random() <= p:
                        cursor.execute(f"INSERT INTO {second_tokens[0]} (individual0) VALUES (?)", (row[0],))
        elif len(first_tokens) == 3 and len(second_tokens) == 3:
            sql_query = f"SELECT individual0,individual1 FROM {first_tokens[0]}"
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if len(rows) != 0:
                for row in rows:
                    if random.random() <= (p/2):
                        cursor.execute(f"INSERT INTO {second_tokens[0]} (individual0,individual1) VALUES (?, ?)", (row[0],row[1]))
        elif len(first_tokens) == 3 and len(second_tokens) == 2:
            if second_tokens[1] == first_tokens[1]:
                sql_query = f"SELECT individual0 FROM {first_tokens[0]}"
            elif second_tokens[1] == first_tokens[2]:
                sql_query = f"SELECT individual1 FROM {first_tokens[0]}"
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if len(rows) != 0:
                for row in rows:
                    if random.random() <= (p/2):
                        cursor.execute(f"INSERT INTO {second_tokens[0]} (individual0) VALUES (?)", (row[0],))
        elif len(first_tokens) == 2 and len(second_tokens) == 3:
            if second_tokens[1] == first_tokens[1]:
                sql_query = f"SELECT individual0 FROM {second_tokens[0]}"
            elif second_tokens[2] == first_tokens[1]:
                sql_query = f"SELECT individual1 FROM {second_tokens[0]}"
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if len(rows) != 0:
                for row in rows:
                    if random.random() <= (p/2):
                        cursor.execute(f"INSERT INTO {first_tokens[0]} (individual0) VALUES (?)", (row[0],))

if __name__ == "__main__":
    owl_file = "ontologies/univ-bench/lubm-ex-20_disjoint.owl" 
    db_file = "bench_prepa/dataset.0.2/University5_p_0.0005.db"

    # set probability p to create multiple conflicting ABoxes "0.00005", "0.00001", "0.000005", 0.0000075
    p = 0.0005
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        add_conflicts(owl_file,cursor,p)
    except sqlite3.OperationalError as e:
            print(f"Error: {e}.")

    conn.commit()
    conn.close()
