import os
import re
from rdflib import Graph, RDF, OWL, RDFS
import time
from dotenv import load_dotenv
import psycopg2
from logzero import logger

from assertion import SupportedAssertion, assertion
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

separation_query = "Q(AHMED, SKIKDA) <- BornIN(AHMED, SKIKDA)"

class ABoxHandler:
    def __init__(self):
        load_dotenv()
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.connect()
        self.size, self.nb_tables = self.abox_size()
        logger.debug(f"The number of the tables in the database: {self.nb_tables}, the size of the ABox (number of assertions): {self.size}")
        
    def connect(self):
        logger.info("Establishing connection to database.")
        self.CONN = psycopg2.connect(dbname=self.DB_NAME,user=self.DB_USER,password=self.DB_PASSWORD,host=self.DB_HOST,port=self.DB_PORT)
        return self.CONN

    def disconnect(self):
        logger.info("Terminating connection to database.")
        if self.CONN:
            self.CONN.close()

    def abox_size(self):
        cursor = self.CONN.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()
        total_rows = 0
        for table in tables:            
            table_name = table[0]
            if table_name.lower() == 'notgreater':
                continue
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cursor.fetchone()[0]
            total_rows += count

        return total_rows, len(tables)

    def quote_identifier(self, identifier: str) -> str:
        """Safely quote SQL identifiers (e.g., table names)."""
        return '"' + identifier.replace('"', '""') + '"'

    def extract_relation_and_vars(self, atom: str):
        """Parse one atom and return its relation and variable list."""
        rel, vars_str = atom.split('(')
        relation = rel.strip('<>')
        variables = [v.strip() for v in vars_str.strip(')').split(',')]
        return relation, variables

    def parse_atoms(self, query_str: str):
        """Extract atoms of the form <IRI>(?var,...) from the query string."""
        return re.findall(r'<[^>]+>\([^\)]+\)', query_str)

    def generate_consistency_sql_query(self, queries):
        """ Generates a single SQL query as a disjunction of EXISTS subqueries, assuming each BCQ query has exactly 2 atoms with overlapping variables. """
        exists_clauses = []
        for query_str in queries:
            atoms = self.parse_atoms(query_str)
            if len(atoms) < 2:
                continue  # Skip invalid or incomplete BCQs

            rel1, vars1 = self.extract_relation_and_vars(atoms[0])
            rel2, vars2 = self.extract_relation_and_vars(atoms[1])

            # Find matching variable indices (excluding the predicate name)
            matching_indexes = [
                (i, j) for i, var1 in enumerate(vars1)
                    for j, var2 in enumerate(vars2) if var1 == var2
            ]

            if not matching_indexes:
                continue  # No joinable variables, skip

            join_conditions = " AND ".join(
                f"t1.individual{i} = t2.individual{j}"
                for (i, j) in matching_indexes
            )

            sql_query = (
                f"SELECT 1 FROM {self.quote_identifier(rel1)} t1 "
                f"JOIN {self.quote_identifier(rel2)} t2 ON {join_conditions}"
            )

            exists_clauses.append(f"EXISTS ({sql_query})")

        if not exists_clauses:
            return "SELECT false AS result;"  # No valid queries to evaluate

        return f"SELECT {' OR '.join(exists_clauses)} AS result;"
    
    def generate_exists_sql_queries(self, queries):
        sql_list = []
        for query_str in queries:
            atoms = self.parse_atoms(query_str)
            if len(atoms) < 2:
                continue

            rel1, vars1 = self.extract_relation_and_vars(atoms[0])
            rel2, vars2 = self.extract_relation_and_vars(atoms[1])
            matching_indexes = [(i, j) for i, var1 in enumerate(vars1) for j, var2 in enumerate(vars2) if var1 == var2]
            if not matching_indexes:
                continue

            join_conditions = " AND ".join(
                f"t1.individual{i} = t2.individual{j}" for i, j in matching_indexes
            )
            sql = (
                f"SELECT 1 FROM {self.quote_identifier(rel1)} t1 "
                f"JOIN {self.quote_identifier(rel2)} t2 ON {join_conditions}"
            )
            sql_list.append(sql)
        return sql_list

    def consistency_checking(self, ontologyHandler):
        """ Perform consistency checking by evaluating batched BCQs as a single SQL query per batch. Returns False if any batch detects inconsistency, True otherwise. """        
        negative_axioms = ontologyHandler.get_negative_axioms()
        queries = [ontologyHandler.generate_query(axiom) for axiom in negative_axioms]

        logger.debug(f"The first generated CQ query: {queries[0]}")
        logger.debug(f"The number of generated conjunctive queries: {len(queries)}.")

        all_queries = ontologyHandler.rewrite_queries(queries)

        cursor = self.CONN.cursor()
        batch_size = 5000
        for i in range(0, len(all_queries), batch_size):
            batch = all_queries[i:i + batch_size]
            exists_queries = self.generate_exists_sql_queries(batch)

            for q in exists_queries:
                try:
                    cursor.execute(q)
                    if cursor.fetchone():  # Conflict found
                        cursor.close()
                        return False
                except Exception as e:
                    logger.debug(f"[Error] SQL error in batch {i}-{i + batch_size}: {e}")
                    logger.debug(f"[Debug] SQL query:\n{q}")
                    raise

        cursor.close()
        return True
    
    def check_if_conflicting(self, ontologyHandler, assertion):
        """Returns True if a given assertion is in some conflict"""
        negative_axioms = ontologyHandler.get_related_negative_axioms(self, assertion.get_assertion_name(), assertion.is_role())
                
        queries = [ontologyHandler.generate_relative_query(axiom, assertion) for axiom in negative_axioms]

        logger.debug(f"The first generated CQ query: {queries[0]}")
        logger.debug(f"The number of generated conjunctive queries: {len(queries)}.")

        all_queries = ontologyHandler.rewrite_queries(queries)

        """TODO: To be completed later (if usefulness is proven)."""

    def dominates(self, subset1: list, subset2: list) -> bool:
        # returns True if subset1 dominates subset2 (each element of subset1 is_strictly_preferred to at least an element of subset2)
        # takes a list for both subset1 and subset2, if you have one element (eg: support) pass it as a list [support]
        for assertion1 in subset1:
            dominates_at_least_one = False        
            for assertion2 in subset2:
                if assertion1.isStrictlyPreferredTo(assertion2):
                    dominates_at_least_one = True
                    break 
            if not dominates_at_least_one:
                return False
        return True

    def generate_conflicts_sql_query(self, queries):
        """ Generate SQL queries to fetch conflicting assertions for each BCQ. Returns a list of individual SELECT queries, not a UNION or EXISTS. 
            DO NOT FORGET TO ADD SUPPORT FOR ROLE ASSERTIONS IN THE SELECT CLAUSE HERE!!"""
        select_queries = []
        for query_str in queries:
            atoms = self.parse_atoms(query_str)
            if len(atoms) < 2:
                continue

            rel1, vars1 = self.extract_relation_and_vars(atoms[0])
            rel2, vars2 = self.extract_relation_and_vars(atoms[1])

            matching_indexes = [
                (i, j) for i, var1 in enumerate(vars1)
                    for j, var2 in enumerate(vars2) if var1 == var2
            ]

            if not matching_indexes:
                continue

            join_conditions = " AND ".join(
                f"t1.individual{i} = t2.individual{j}" for i, j in matching_indexes
            )

            table1 = self.quote_identifier(rel1)
            table2 = self.quote_identifier(rel2)

            if len(vars1) == 1 and len(vars2) == 1:
                select_clause = (
                    f"SELECT t1.id, t1.individual0, t1.derivationTimestamp, t1.wikiTimestamp, t1.source, t2.id, t2.individual0, t2.derivationTimestamp, t2.wikiTimestamp, t2.source "
                    f"FROM {table1} t1 JOIN {table2} t2 ON {join_conditions}"
                )
            elif len(vars1) == 2 and len(vars2) == 1:
                select_clause = (
                    f"SELECT t1.id, t1.individual0, t1.individual1, t1.derivationTimestamp, t1.wikiTimestamp, t1.source, t2.id, t2.individual0, t2.derivationTimestamp, t2.wikiTimestamp, t2.source "
                    f"FROM {table1} t1 JOIN {table2} t2 ON {join_conditions}"
                )
            elif len(vars1) == 1 and len(vars2) == 2:
                select_clause = (
                    f"SELECT t1.id, t1.individual0, t1.derivationTimestamp, t1.wikiTimestamp, t1.source, t2.id, t2.individual0, t2.individual1, t2.derivationTimestamp, t2.wikiTimestamp, t2.source "
                    f"FROM {table1} t1 JOIN {table2} t2 ON {join_conditions}"
                )
            elif len(vars1) == 2 and len(vars2) == 2:
                select_clause = (
                    f"SELECT t1.id, t1.individual0, t1.individual1, t1.derivationTimestamp, t1.wikiTimestamp, t1.source, t2.id, t2.individual0, t2.individual1, t2.derivationTimestamp, t2.wikiTimestamp, t2.source "
                    f"FROM {table1} t1 JOIN {table2} t2 ON {join_conditions}"
                )

            select_queries.append((select_clause, rel1, rel2, len(vars1), len(vars2)))  # Keep track of table names and length of variables too

        return select_queries
    
    def compute_conflicts(self, ontologyHandler):
        """
        Return a list of conflicts detected in the ABox using disjoint axioms.
        Each conflict is a tuple of two `assertion` objects.
        """
        conflicts = []

        negative_axioms = ontologyHandler.get_negative_axioms()
        queries = [ontologyHandler.generate_query(axiom) for axiom in negative_axioms]

        logger.debug(f"The first generated CQ query: {queries[0]}")
        logger.debug(f"The number of generated conjunctive queries: {len(queries)}.")

        all_queries = ontologyHandler.rewrite_queries(queries)

        cursor = self.CONN.cursor()
        batch_size = 1000
        for i in range(0, len(all_queries), batch_size):
            batch = all_queries[i:i + batch_size]
            select_queries = self.generate_conflicts_sql_query(batch)

            for query, table1, table2, v1len, v2len in select_queries:
                try:
                    cursor.execute(query)
                    for row in cursor.fetchall():
                        # Initialize indexes
                        idx = 0
                        # --- First assertion (t1) ---
                        id1 = row[idx]; idx += 1
                        ind0_1 = row[idx]; idx += 1
                        ind1_1 = row[idx] if v1len == 2 else None
                        if v1len == 2: idx += 1
                        ts1 = row[idx]; idx += 1
                        wt1 = row[idx]; idx += 1
                        src1 = row[idx]; idx += 1
                        
                        a1 = assertion(assertion_name=table1,individual_0=ind0_1,individual_1=ind1_1,derivationTimestamp=ts1,wikiTimestamp=wt1,source=src1,id=id1)
                        
                        # --- Second assertion (t2) ---
                        id2 = row[idx]; idx += 1
                        ind0_2 = row[idx]; idx += 1
                        ind1_2 = row[idx] if v2len == 2 else None
                        if v2len == 2: idx += 1
                        ts2 = row[idx]; idx += 1
                        wt2 = row[idx]; idx += 1
                        src2 = row[idx]; idx += 1

                        a2 = assertion(assertion_name=table2,individual_0=ind0_2,individual_1=ind1_2,derivationTimestamp=ts2,wikiTimestamp=wt2,source=src2,id=id2)
                        
                        conflicts.append((a1, a2))
                        #result = (a1, a2)
                        #if not any(self.dominates(conflict,result) for conflict in conflicts):                    
                        #    to_remove = [conflict for conflict in conflicts if self.dominates(result,conflict)]
                        #    if to_remove:
                        #        conflicts = [x for x in conflicts if x not in to_remove]
                        #    conflicts.append(result)
                        conflicts.append((a1, a2))

                except Exception as e:
                    logger.debug(f"[Error] SQL query execution failed: {e}")
                    logger.debug(f"[Debug] SQL query:\n{query}")
                    raise

        cursor.close()
        return conflicts
    
    def format_support_query(self, assertion):
        def safe_uri(uri):
            if uri:
                # Replace all problematic characters
                return f"<{uri.replace(',', '%2C').replace('(', '%28').replace(')', '%29').replace("\'", '%27')}>"
            return None

        individuals = [safe_uri(ind) for ind in assertion.get_individuals() if ind is not None]
        predicate = f"<{assertion.get_assertion_name()}>"
        return f"Q({', '.join(individuals)}) <- {predicate}({', '.join(individuals)})"
    
    def generate_support_sql_query(self, query):
        """ TODO: Consider writing a version that takes a query of any size!
            this function generates a sql query from a conjunctive query, it assumes the query to have just 1 atom
            it returns the sql_query alongside table name to faciliate construction of supports
            tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
        """        
        table_name = query.split(">(")[0].strip("<>")
        tokens = [token.strip("<>") for token in query.split(">(")[1][:-1].split(", ")]
        if len(tokens) == 1:
            sql_query = 'SELECT * FROM "{}" WHERE individual0 = \'{}\''.format(table_name,tokens[0])
        elif tokens[0][0] == "?":
            sql_query = 'SELECT * FROM "{}" WHERE individual1 = \'{}\''.format(table_name,tokens[1])
        elif tokens[1][0] == "?":
            sql_query = 'SELECT * FROM "{}" WHERE individual0 = \'{}\''.format(table_name,tokens[0])
        else:
            sql_query = 'SELECT * FROM "{}" WHERE individual0 = \'{}\' AND individual1 = \'{}\''.format(table_name,tokens[0],tokens[1])
        return sql_query, table_name

    def compute_supports(self, assertions, ontologyHandler):
        """Takes a list of assetions and computes their supports (in a traditional way), returns a dictionnary where each assertion object points to a list of its supports.
           It optimises one call for the Rapid.jar query re-writing tool, avoiding useless in/out operations. a single assertion should be passed as a list: [assertion]
        """
        queries = []
        assertions_list = assertions
        for i_assertion in assertions:
            queries.append(self.format_support_query(i_assertion))
            queries.append(separation_query)

        batch_size = 25000
        all_queries = []

        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]
            rewritten = ontologyHandler.rewrite_queries(batch)
            all_queries.extend(rewritten)
        
        cqueries = {}
        start_index = 0
        for i_assertion in assertions_list:
            end_index = all_queries.index("BornIN(AHMED, SKIKDA)", start_index)
            cqueries[i_assertion] = all_queries[start_index:end_index]
            start_index = end_index + 1

        #logger.error(f"Number of assertions processed: {len(assertions_list)}")

        #logger.error(f"Number of CQs re-writings: {sum((len(val) for val in cqueries.values()))}")

        cursor = self.CONN.cursor()

        supports = {}
        for i_assertion in cqueries.keys():
            supports[i_assertion] = []
            for query in cqueries[i_assertion]:
                sql_query, table_name = self.generate_support_sql_query(query)

                # logger.error(f"Example SQL query: {sql_query}")
                cursor.execute(sql_query)
                
                rows = cursor.fetchall()
                if len(rows) != 0:
                    # logger.error("SQL query returned some values")
                    for row in rows:
                        if len(row) == 6:
                            temp_assertion = assertion(assertion_name=table_name, individual_0=row[1], individual_1 = None, derivationTimestamp = row[2], wikiTimestamp = row[3], source = row[4],id=row[0])
                            supports[i_assertion].append(temp_assertion)
                        if len(row) == 7:
                            temp_assertion = assertion(assertion_name=table_name, individual_0=row[1], individual_1 = row[2], derivationTimestamp = row[3], wikiTimestamp = row[4], source = row[5],id=row[0])
                            supports[i_assertion].append(temp_assertion)
        
        cursor.close()
        return supports
    
    def generate_closure_sql_query(self, query: str):
        # this function generates a sql query from a conjunctive query, it assumes the query to have just 1 atom
        # tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]

        table_name = query.split(">(")[0][1:]
        tokens = query.split(">(")[1][:-1].split(", ")

        if len(tokens) == 1:
            sql_query = 'SELECT individual0 FROM "{}"'.format(table_name)
        elif tokens[0] == "?0" and tokens[1] == "?1":
            sql_query = 'SELECT individual0,individual1 FROM "{}"'.format(table_name)
        elif tokens[1] == "?0" and tokens[0] == "?1":
            sql_query = 'SELECT individual1,individual0 FROM "{}"'.format(table_name)
        elif tokens[0] == "?0":
            sql_query = 'SELECT individual0 FROM "{}"'.format(table_name)
        else : #if tokens[1] == "?0":
            sql_query = 'SELECT individual1 FROM "{}"'.format(table_name)
        return sql_query

    def compute_closure(self, ontologyHandler):
        """Returns all the possible assertions to be checked using the dominant supports characterisation (computes a closure of the initial ABox).
            It reads through the ontology classes and properties (concepts and roles) and finds if they have individuals with which they can be derived from the data (ABox)
        """
        all_assertions_to_check = set()
        cursor = self.CONN.cursor()

        concepts = [class_uri.split('#')[-1] for class_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.Class)]
        concept_queries = []
        for concept_name in concepts:
            concept_queries.append(f"Q(?0) <- <{concept_name}>(?0)")
            concept_queries.append(separation_query)
        all_concept_queries = ontologyHandler.rewrite_queries(concept_queries)
        assertions_counter = 0
        for cq_query in all_concept_queries:
            if cq_query == "BornIN(AHMED, SKIKDA)":
                assertions_counter += 1
                continue
            sql_query = self.generate_closure_sql_query(cq_query)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    if len(result) == 1:
                        assertion_k = assertion(concepts[assertions_counter],result[0])
                        all_assertions_to_check.add(assertion_k)
        
        concepts_number = len(all_assertions_to_check)
        logger.error(f"The number of all concept assertions: {concepts_number}")

        roles = [prop_uri.split('#')[-1] for prop_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)]
        role_queries = []
        for role_name in roles:
            role_queries.append(f"Q(?0,?1) <- <{role_name}>(?0,?1)")
            role_queries.append(separation_query)
        all_role_queries = ontologyHandler.rewrite_queries(role_queries)    
        assertions_counter = 0
        for cq_query in all_role_queries:
            if cq_query == "BornIN(AHMED, SKIKDA)":
                assertions_counter += 1
                continue
            sql_query = self.generate_closure_sql_query(cq_query)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    if len(result) == 2:
                        assertion_k = assertion(roles[assertions_counter],result[0],result[1])
                        all_assertions_to_check.add(assertion_k)

        logger.error(f"The number of all role assertions: {len(all_assertions_to_check) - concepts_number}")
        
        cursor.close()

        return all_assertions_to_check

    def generate_wieghted_closure_sql_query(self, query: str):
        # this function generates a sql query from a conjunctive query, it assumes the query to have just 1 atom
        # tokens = [token for token in query.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]

        table_name = query.split(">(")[0][1:]
        tokens = query.split(">(")[1][:-1].split(", ")

        if len(tokens) == 1:
            sql_query = 'SELECT * FROM "{}"'.format(table_name)
        elif tokens[0] == "?0" and tokens[1] == "?1":
            sql_query = 'SELECT * FROM "{}"'.format(table_name)
        elif tokens[1] == "?0" and tokens[0] == "?1":
            sql_query = 'SELECT * FROM "{}"'.format(table_name)
        elif tokens[0] == "?0":
            sql_query = 'SELECT * FROM "{}"'.format(table_name)
        else : #if tokens[1] == "?0":
            sql_query = 'SELECT * FROM "{}"'.format(table_name)
        return sql_query, table_name, tokens

    def compute_weighted_closure(self, ontologyHandler):
        """Returns all the possible assertions as a list of SupportedAssertion objects (computes a partially ordered weighted closure of the initial ABox).
            It reads through the ontology classes and properties (concepts and roles) and finds if they have individuals with which they can be derived from the data (ABox)
        """
        all_assertions_to_check = {}
        cursor = self.CONN.cursor()

        concepts = [class_uri.split('#')[-1] for class_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.Class)]
        concept_queries = []
        for concept_name in concepts:
            concept_queries.append(f"Q(?0) <- <{concept_name}>(?0)")
            concept_queries.append(separation_query)
        all_concept_queries = ontologyHandler.rewrite_queries(concept_queries)
        assertions_counter = 0
        error_size = 0
        for cq_query in all_concept_queries:
            if cq_query == "BornIN(AHMED, SKIKDA)":
                assertions_counter += 1
                continue
            sql_query, table_name, tokens = self.generate_wieghted_closure_sql_query(cq_query)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    assertion_name = table_name
                    idx = 0
                    id = result[idx]; idx+=1
                    individual_0=result[idx]; idx+=1
                    individual_1=result[idx] if len(tokens) == 2 else None
                    if len(tokens) == 2: idx+=1
                    dts = result[idx]; idx+=1
                    wts = result[idx]; idx+=1
                    source = result[idx]; idx+=1

                    # temp_assertion is the support, it can be retrieved as it is in database using SELECT*
                    temp_assertion = assertion(assertion_name=assertion_name,individual_0=individual_0,individual_1=individual_1,derivationTimestamp=dts,wikiTimestamp=wts,source=source,id=id)

                    # key refers to an assertion that can depend on order of query elements, e.g. Q(?0,?1) <- <{role_name}>(?0,?1) or Q(?0,?1) <- <{role_name}>(?1,?0) makes a difference
                    # tokens are returned as they are for this purpose
                    if len(tokens) == 1 :
                        key = (concepts[assertions_counter], individual_0, None)
                    elif len(tokens) == 2 and tokens[0] == "?0":
                        key = (concepts[assertions_counter], individual_0, None)
                    elif len(tokens) == 2 and tokens[1] == "?0":
                        key = (concepts[assertions_counter], individual_1, None)

                    if key in all_assertions_to_check:
                        all_assertions_to_check[key].add_support(temp_assertion)
                    else:
                        supported_assertion = SupportedAssertion(*key)
                        supported_assertion.add_support(temp_assertion)
                        all_assertions_to_check[key] = supported_assertion
        
        concepts_number = len(all_assertions_to_check)
        logger.error(f"The number of all concept assertions: {concepts_number}")

        roles = [prop_uri.split('#')[-1] for prop_uri in ontologyHandler.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)]
        role_queries = []
        for role_name in roles:
            role_queries.append(f"Q(?0,?1) <- <{role_name}>(?0,?1)")
            role_queries.append(separation_query)
        all_role_queries = ontologyHandler.rewrite_queries(role_queries)    
        assertions_counter = 0
        for cq_query in all_role_queries:
            if cq_query == "BornIN(AHMED, SKIKDA)":
                assertions_counter += 1
                continue
            sql_query, table_name, tokens = self.generate_wieghted_closure_sql_query(cq_query)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    if len(result) != 7:
                        error_size+=1
                    if len(result) == 7:                        
                        temp_assertion = assertion(assertion_name=table_name, individual_0=result[1], individual_1 = result[2], derivationTimestamp = result[3], wikiTimestamp = result[4], source = result[5],id=result[0])
                        if len(tokens) == 2 and tokens[0] == "?0":
                            key = (roles[assertions_counter], result[1], result[2])
                        else: # if len(tokens) == 2 and tokens[1] == "?0":
                            key = (roles[assertions_counter], result[2], result[1])

                        if key in all_assertions_to_check:
                            all_assertions_to_check[key].add_support(temp_assertion)
                        else:
                            supported_assertion = SupportedAssertion(*key)
                            supported_assertion.add_support(temp_assertion)
                            all_assertions_to_check[key] = supported_assertion
        
        logger.error(f"error size: {error_size}")

        logger.error(f"The number of all role assertions: {len(all_assertions_to_check) - concepts_number}")

        cursor.close()

        return all_assertions_to_check
    
    def generate_no_preferred_support_sql_queries(self, queries, supports):
        sql_list = []

        # Prepare support VALUES clause
        support_rows = []
        for assertion in supports:
            # Escape single quotes
            support = {}
            support['derivationTimestamp'] = assertion.get_derivationTimestamp()
            support['wikiTimestamp'] = assertion.get_wikiTimestamp()
            support['source'] = assertion.get_source()

            dts = f"'{support['derivationTimestamp']}'::timestamptz" if support['derivationTimestamp'] else "NULL"
            wts = f"'{support['wikiTimestamp']}'::timestamptz" if support['wikiTimestamp'] else "NULL"
            src = support['source'] #.replace("'", "''")
            support_rows.append(f"({dts}, {wts}, '{src}')")

        support_values = ",\n        ".join(support_rows)
        support_table = f"(VALUES\n        {support_values}\n    ) AS s(derivationTimestamp, wikiTimestamp, source)"

        for query_str in queries:
            atoms = self.parse_atoms(query_str)
            if len(atoms) < 2:
                continue

            rel1, vars1 = self.extract_relation_and_vars(atoms[0])
            rel2, vars2 = self.extract_relation_and_vars(atoms[1])

            matching_indexes = [(i, j) for i, var1 in enumerate(vars1) for j, var2 in enumerate(vars2) if var1 == var2]
            if not matching_indexes:
                continue

            join_conditions = " AND ".join(
                f"t1.individual{i} = t2.individual{j}" for i, j in matching_indexes
            )

                        
            sql = f"""
SELECT 1 FROM {self.quote_identifier(rel1)} t1 JOIN {self.quote_identifier(rel2)} t2 ON {join_conditions} 
JOIN {support_table}
ON (
  (
    (
      (s.derivationTimestamp IS NOT NULL AND t1.derivationTimestamp IS NOT NULL AND s.derivationTimestamp::timestamptz <= t1.derivationTimestamp) 
      AND
      (s.wikiTimestamp IS NOT NULL AND t1.wikiTimestamp IS NOT NULL AND s.wikiTimestamp::timestamptz <= t1.wikiTimestamp) 
      AND
      (s.source != 'instance-types_lang=en_specific' OR t1.source != 'instance_types_lhd_dbo_en')
    )
    OR (
      (s.derivationTimestamp IS NOT NULL AND t1.derivationTimestamp IS NOT NULL AND s.derivationTimestamp::timestamptz < t1.derivationTimestamp)
      OR
      (s.wikiTimestamp IS NOT NULL AND t1.wikiTimestamp IS NOT NULL AND s.wikiTimestamp::timestamptz < t1.wikiTimestamp)
      OR
      (s.source = 'instance_types_lhd_dbo_en' AND t1.source = 'instance-types_lang=en_specific')
    )
  ) AND (
    (
      (s.derivationTimestamp IS NOT NULL AND t2.derivationTimestamp IS NOT NULL AND s.derivationTimestamp::timestamptz <= t2.derivationTimestamp) 
      AND 
      (s.wikiTimestamp IS NOT NULL AND t2.wikiTimestamp IS NOT NULL AND s.wikiTimestamp::timestamptz <= t2.wikiTimestamp) 
      AND
      (s.source != 'instance-types_lang=en_specific' OR t2.source != 'instance_types_lhd_dbo_en')
    )
    OR (
      (s.derivationTimestamp IS NOT NULL AND t2.derivationTimestamp IS NOT NULL AND s.derivationTimestamp::timestamptz < t2.derivationTimestamp)
      OR
      (s.wikiTimestamp IS NOT NULL AND t2.wikiTimestamp IS NOT NULL AND s.wikiTimestamp::timestamptz < t2.wikiTimestamp)
      OR
      (s.source = 'instance_types_lhd_dbo_en' AND t2.source = 'instance-types_lang=en_specific')
    )
  )
)
LIMIT 1;
"""
            sql_list.append(sql.strip())
            
        return sql_list
    
    def get_assertion_id_from_DB(self, assertion, cursor):
         # get each supports ID in table and put it in tuple with table name (assertion.get_assertion_name()):
        dts = f"= '{assertion.get_derivationTimestamp()}'::timestamptz" if assertion.get_derivationTimestamp() else "IS NULL"
        wts = f"= '{assertion.get_wikiTimestamp()}'::timestamptz" if assertion.get_wikiTimestamp() else "IS NULL"
        id_query = '''
                SELECT id FROM "{}"  WHERE individual0 = \'{}\' AND derivationTimestamp {} AND wikiTimestamp {} AND source = \'{}\' 
            '''.format(assertion.get_assertion_name(),assertion.get_individuals()[0],dts,wts,assertion.get_source())
            
        cursor.execute(id_query)
        row = cursor.fetchone()
        if row:
            id = row[0]
            return id            
        else:
            logger.error(f"Id of suuport {assertion.__str__()} not found, check again!")

    def generate_no_preferred_support_sql_queries_using_NotGreater(self, queries, supports, cursor):
        sql_list = []

        # Prepare support rows
        support_rows = []
        for assertion in supports:
            id = assertion.get_assertion_id()
            if id == -1:
                id = self.get_assertion_id_from_DB(assertion, cursor)
            support_rows.append((id,assertion.get_assertion_name()))
    
        for query_str in queries:
            atoms = self.parse_atoms(query_str)
            if len(atoms) < 2:
                continue

            rel1, vars1 = self.extract_relation_and_vars(atoms[0])
            rel2, vars2 = self.extract_relation_and_vars(atoms[1])

            matching_indexes = [(i, j) for i, var1 in enumerate(vars1) for j, var2 in enumerate(vars2) if var1 == var2]
            if not matching_indexes:
                continue

            join_conditions = " AND ".join(
                f"t1.individual{i} = t2.individual{j}" for i, j in matching_indexes
            )
            
            i = 1
            supports_join_condition = ""
            for row_id, table_name in support_rows:
                supports_join_condition += f"""JOIN NotGreater ng{i} ON (
                    ng{i}.table1 = '{table_name}' AND ng{i}.id1 = {row_id} AND ng{i}.table2 = '{rel1}' AND ng{i}.id2 = t1.id
                ) JOIN NotGreater ng{i+1} ON (
                    ng{i+1}.table1 = '{table_name}' AND ng{i+1}.id1 = {row_id} AND ng{i+1}.table2 = '{rel2}' AND ng{i+1}.id2 = t2.id
                )
                """
                i += 2

            sql = f"""
                SELECT 1 FROM {self.quote_identifier(rel1)} t1 JOIN {self.quote_identifier(rel2)} t2 ON {join_conditions} 
                {supports_join_condition}
                LIMIT 1;
            """
            sql_list.append(sql.strip())
            
        return sql_list

    def get_raw_conflicts_queries(self, ontologyHandler):
        negative_axioms = ontologyHandler.get_negative_axioms()
        queries = [ontologyHandler.generate_query(axiom) for axiom in negative_axioms]

        logger.debug(f"The first generated CQ query: {queries[0]}")
        logger.debug(f"The number of generated conjunctive queries: {len(queries)}.")

        all_queries = ontologyHandler.rewrite_queries(queries)

        return all_queries
    
    def consistency_checking_with_condition(self, supported_assertion, all_queries):
        """"""
        """ Perform consistency checking by evaluating batched BCQs as a single SQL query per batch. Returns False if any batch detects inconsistency, True otherwise. """        
        
        cursor = self.CONN.cursor()
        batch_size = 2000
        for i in range(0, len(all_queries), batch_size):
            #start_time = time.time()
            batch = all_queries[i:i + batch_size]
            exists_queries = self.generate_no_preferred_support_sql_queries_using_NotGreater(batch, supported_assertion.supports, cursor)

            for q in exists_queries:
                try:
                    cursor.execute(q)
                    if cursor.fetchone():  # Conflict found
                        cursor.close()
                        return False
                except Exception as e:
                    logger.debug(f"[Error] SQL error in batch {i}-{i + batch_size}: {e}")
                    logger.debug(f"[Debug] SQL query:\n{q}")
                    raise
            
            #end_time = time.time()
            # Calculate and display progress
            #progress = (i / len(all_queries)) * 100
            #logger.debug(f"Progress: {progress:.2f}%, time spent: {end_time - start_time:.2f} seconds.")
        cursor.close()
        return True