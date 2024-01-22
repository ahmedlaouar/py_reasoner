import logging
import rdflib
import time

logging.basicConfig()
logger = logging.getLogger('logger')
logger.warning('The system may break down')

start_time = time.time()

g = rdflib.Graph()
g.parse ('py_reasoner/ontologies/univ-bench/lubm-ex-20_disjoint.owl', format='application/rdf+xml')
lubm = rdflib.Namespace('http://swat.cse.lehigh.edu/onto/univ-bench.owl#')

g.bind('lubm-ex-20_disjoint', lubm)

custom_prefix = "owl"
custom_namespace = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
g.bind(custom_prefix, custom_namespace)

query = """
select distinct ?s ?p ?o 
where { ?s owl:disjointWith ?o}
        """
result = g.query(query)
# Print the result with prefixed names or original URIs
for row in result.bindings:
    #s = str(row['s'])
    #o = str(row['o'])
    s = g.qname(row['s']) if 's' in row and row['s'] else str(row['s'])
    o = g.qname(row['o']) if 'o' in row and row['o'] else str(row['o'])
    print(f"{s}, owl:disjointWith, {o}")

print("--- %s seconds ---" % (time.time() - start_time))
