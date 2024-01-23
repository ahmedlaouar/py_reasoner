import pathlib
import rdflib

path = str(pathlib.Path().resolve())

def get_OntologyURI(graph):
    
    test = [x for x, y, z in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Ontology))]

    if test:
        return str(test[0])
    else:
        return None
    
def get_negative_axioms(ontology_path :str):
    graph = rdflib.Graph()
    graph.parse (path+ontology_path, format='application/rdf+xml')
    
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

#print(get_negative_axioms('/ontologies/univ-bench/lubm-ex-20_disjoint.owl'))

def generate_queries(negative_axioms):
    queries = []
    for axiom in negative_axioms:
        ax = axiom.split(",")
        if ax[1] == "owl:disjointWith" :
            queries.append(f"Q(?0) <- {ax[0]}(?0), {ax[2]}(?0)")
        elif ax[1] == "owl:propertyDisjointWith" :
            queries.append(f"Q(?0,?1) <- {ax[0]}(?0,?1), {ax[2]}(?0,?1)")
    return queries

#print(generate_queries(get_negative_axioms('/ontologies/univ-bench/lubm-ex-20_disjoint.owl')))

def compute_conflicts(ontology_path :str, data_path: str):
    negative_axioms = get_negative_axioms(ontology_path)
    queries = generate_queries(negative_axioms)
