import rdflib
import subprocess
from logzero import logger
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

class OntologyHandler:
    def __init__(self, ontology_path, format='application/rdf+xml'):
        self.ontology_path = ontology_path
        self.graph = rdflib.Graph()
        self.graph.parse(ontology_path, format=format)

        namespace = self.get_uri()
        logger.debug(f"The ontolgy's namespace: {namespace}.")
        prefix = rdflib.Namespace(namespace)
        self.graph.bind("", prefix)
        logger.debug((f"Number of axioms (triples): {len(self.graph)}"))

    def get_uri(self):    
        test = [x for x, _, _ in self.graph.triples((None, rdflib.RDF.type, rdflib.OWL.Ontology))]
        if test:
            return str(test[0])
        return None

    def get_negative_axioms(self):
        """this function goes through the ontology and returns disjointWith and propertyDisjointWith as negative axioms"""

        query1 = """
        select distinct ?s ?o 
        where { ?s owl:disjointWith ?o}
        """        
        result1 = self.graph.query(query1)
        negative_axioms = []
        for row in result1: #.bindings:
            s = row.s.toPython()
            o = row.o.toPython()
            negative_axioms.append(f"{s}|owl:disjointWith|{o}")

        # use the following for conflicts or roles "DL-Lite_R"
        query2 = """
        select distinct ?s ?p ?o 
        where { ?s owl:propertyDisjointWith ?o}
        """ 
        result2 = self.graph.query(query2)    
        for row in result2:
            s = row.s.toPython()
            o = row.o.toPython()
            negative_axioms.append(f"{s}|owl:propertyDisjointWith|{o}")
        
        logger.debug(f'The number of the disjointness (negative) axioms in the ontology is {len(negative_axioms)}.')
        logger.debug(f"The first negative axiom {negative_axioms[0]}")
        return negative_axioms
    
    def get_related_negative_axioms(self, assertion_name, role=False):
        """this function goes through the ontology and returns disjointWith or propertyDisjointWith related to a given concept or role name (assertion_nameà as negative axioms"""
    
        if not role:
            query1 = f"""
            select distinct ?o 
            where {{ ?{assertion_name} owl:disjointWith ?o}}
            """        
            result1 = self.graph.query(query1)
            negative_axioms = []
            for row in result1:
                o = row.o.toPython()
                negative_axioms.append(f"{assertion_name},owl:disjointWith,{o}")
        else: 
            # use the following for conflicts or roles "DL-Lite_R"
            query2 = f"""
            select distinct ?o 
            where {{ ?{assertion_name} owl:propertyDisjointWith ?o}}
            """ 
            result2 = self.graph.query(query2)    
            for row in result2:
                o = row.o.toPython()
                negative_axioms.append(f"{assertion_name},owl:propertyDisjointWith,{o}")
        
        logger.debug(f'The number of the disjointness (negative) axioms in the ontology is {len(negative_axioms)}.')
        logger.debug(f"The first negative axiom {negative_axioms[0]}")
        return negative_axioms
    
    def generate_query(self, axiom):
        # from a negative axiom generate a conjunctive query, here with 2 atoms since we use DL-Lite_R
        ax = axiom.split("|")
        if ax[1] == "owl:disjointWith" :
            query = f"Q(?0) <- <{ax[0]}>(?0), <{ax[2]}>(?0)"
        elif ax[1] == "owl:propertyDisjointWith" :
            query = f"Q(?0,?1) <- <{ax[0]}>(?0,?1), <{ax[2]}>(?0,?1)"
        else :
            return ""
        return query
    
    def generate_relative_query(self, axiom, assertion):
        """"""
        ax = axiom.split(",")
        if ax[1] == "owl:disjointWith" :
            query = f"Q({assertion.get_individuals()[0]}) <- <{ax[0]}>({assertion.get_individuals()[0]}), <{ax[2]}>({assertion.get_individuals()[0]})"
        elif ax[1] == "owl:propertyDisjointWith" :
            query = f"Q({assertion.get_individuals()[0]},{assertion.get_individuals()[1]}) <- <{ax[0]}>({assertion.get_individuals()[0]},{assertion.get_individuals()[1]}), <{ax[2]}>({assertion.get_individuals()[0]},{assertion.get_individuals()[1]})"
        else :
            return ""
        return query

    def rewrite_queries(self, queries: list):
        """This method interfaces with the OWL ontology using Rpaid query re-writing tool
           It takes a list of CQs and returns all their rewritings (stripped from useless part: Q(?0) <- ). 
        """
        all_queries = []
        # Path to your Java executable
        java_executable = 'java'
        # Path to your JAR file
        jar_file = 'libraries/Rapid2.jar'
        # Create a temporary file to store the content
        temp_file_path = 'core/temp/temp_queries.txt'
        with open(temp_file_path, 'w') as temp_file:
            temp_file.writelines(query + '\n' for query in queries)
        try:
            # Run the JAR file with the temporary file path as an argument
            result_bytes = subprocess.check_output([java_executable, "-Xmx8g", '-jar', jar_file, "DU", "FULL", self.ontology_path, temp_file_path])
            result = result_bytes.decode('utf-8').strip()
            results = result.split('\n')
            for i in range(1,len(results)):
                # Remove the first part of query before Q(?0) <- as it's not useful for SQL querying then Strip to remove leading/trailing whitespaces
                to_append = results[i].split("<-")[1].strip() 
                all_queries.append(to_append)
        except subprocess.CalledProcessError as e:
            logger.debug(f"Error executing Rapid2.jar. Error: {e}")
        
        logger.debug(f"The number of all the inferred re-writings based on TBox axioms: {len(all_queries)}.")
        return all_queries