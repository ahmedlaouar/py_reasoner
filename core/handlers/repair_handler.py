from multiprocessing import Pool
import random
import time
from logzero import logger

def check_assertion(args):
    assertion, conflicts, supports, dominates_fn = args
    accepted = True
    for conflict in conflicts:
        conflict_supported = False
        for support in supports:
            if dominates_fn([support], conflict):
                conflict_supported = True
                break
        if not conflict_supported:
            accepted = False    
    if accepted :
        return assertion

def dominates(subset1: list, subset2: list) -> bool:
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

def consistency_check_worker(args):
    from handlers.abox_handler import ABoxHandler  # import inside the worker to avoid issues during pickling

    supported_assertion, all_queries = args
    abox_handler = ABoxHandler()  # new instance with its own DB connection
    if abox_handler.consistency_checking_with_condition(supported_assertion, all_queries):
        return supported_assertion
    return None

def extended_check_assertion(args):
    supported_assertion, conflicts = args
    for a1,a2 in conflicts:
        if not (supported_assertion.isStrictlyPreferredTo(a1) or supported_assertion.isStrictlyPreferredTo(a2)):
            return None
    return supported_assertion

class RepairHandler:
    def __init__(self, ontologyHandler, aboxHandler):
        self.ontologyHandler = ontologyHandler
        self.aboxHandler = aboxHandler    

    def compute_cpi_repair(self, assertions, conflicts, supports):
        dominates_fn = dominates  # assumed to be a regular function
        args = [(assertion, conflicts, supports[assertion], dominates_fn) for assertion in assertions]        
        # arguments = [(assertion, conflicts, supports[assertion]) for assertion in assertions]
        with Pool() as pool:
            results = pool.map(check_assertion, args)
        cpi_repair = set([result for result in results if result is not None])
        return cpi_repair
    
    def run_cpi_repair(self):
        """"""
        exe_results = {}
        exe_results["ABox_size"] = self.aboxHandler.size
        # first, generate the possible assertions of (cl(ABox)), returns a list of dl_lite.assertion.w_assertion
        start_time = round(time.time(), 3)
        all_assertions = self.aboxHandler.compute_closure(self.ontologyHandler)
        inter_time0 = round(time.time(), 3)
        logger.debug(f"Number of the generated assertions: {len(all_assertions)}")
        logger.debug(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        exe_results["Closure_size"] = len(all_assertions)
        exe_results["Closure_time"] = inter_time0 - start_time
        
        # compute the conflicts, conflicts are of the form (assertion1,assertion2)
        conflicts = self.aboxHandler.compute_conflicts(self.ontologyHandler)
        inter_time1 = round(time.time(), 3)
        logger.debug(f"Number of conflicts: {len(conflicts)}")
        logger.debug(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results["Conflicts_time"] = inter_time1 - inter_time0
        exe_results["Conflicts_size"] = len(conflicts)
        
        # browse assertions and compute supports
        # returns a dictionnary with assertions indexes in the list as keys and as values lists of supports with the form [(table_name,id,degree)] 
        supports = self.aboxHandler.compute_supports(all_assertions, self.ontologyHandler)
        inter_time2 = round(time.time(), 3)
        supports_size = sum((len(val) for val in supports.values()))
        logger.debug(f"Number of all the computed supports: {supports_size}")
        logger.debug(f"Time to compute all the supports of all the assertions: {inter_time2 - inter_time1}")
        exe_results["size_all_supports"] = supports_size
        exe_results["Supports_time"] = inter_time2 - inter_time1

        cpi_repair = self.compute_cpi_repair(all_assertions, conflicts, supports)
        
        inter_time3 = round(time.time(), 3)
        logger.debug(f"Size of the cpi_repair: {len(cpi_repair)}")
        logger.debug(f"Time to compute the cpi_repair: {inter_time3 - inter_time2}")
        exe_results["Cpi_repair_size"] = len(cpi_repair)
        exe_results["Cpi_repair_time"] = inter_time3 - inter_time2
        
        logger.debug(f"Total time of execution: {inter_time3 - start_time}")
        exe_results["Total_time"] = inter_time3 - start_time

        return exe_results
    
    def compute_cpi_repair_by_consistency_checks(self):
        """"""
        exe_results = {}
        exe_results["ABox_size"] = self.aboxHandler.size
        # first, generate the possible assertions of (cl(ABox)), returns a list of SupportedAssertion objects
        start_time = round(time.time(), 3)
        all_assertions = self.aboxHandler.compute_weighted_closure(self.ontologyHandler)
        inter_time0 = round(time.time(), 3)
        logger.debug(f"Number of the generated assertions: {len(all_assertions)}")
        logger.debug(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        exe_results["Closure_size"] = len(all_assertions)
        exe_results["Closure_time"] = inter_time0 - start_time

        all_queries = self.aboxHandler.get_raw_conflicts_queries(self.ontologyHandler)
        cpi_repair = set()
        
        for i, supported_assertion in enumerate(all_assertions.values()):
            s_time = time.time()
            accepted = self.aboxHandler.consistency_checking_with_condition(supported_assertion, all_queries)
            if accepted:
                cpi_repair.add(supported_assertion)

            e_time = time.time()
            # Calculate and display progress
            progress = (i / len(all_assertions.values())) * 100
            logger.debug(f"Progress: {progress:.2f}%, time spent: {e_time - s_time:.2f} seconds.")

        inter_time1 = round(time.time(), 3)
        logger.debug(f"Size of the cpi_repair: {len(cpi_repair)}")
        logger.debug(f"Time to compute the cpi_repair: {inter_time1 - inter_time0}")
        exe_results["Cpi_repair_size"] = len(cpi_repair)
        exe_results["Cpi_repair_time"] = inter_time1 - inter_time0
        
        logger.debug(f"Total time of execution: {inter_time1 - start_time}")
        exe_results["Total_time"] = inter_time1 - start_time

        return exe_results
    
    def compute_cpi_repair_by_consistency_checks_parallel(self):
        """"""
        exe_results = {}
        exe_results["ABox_size"] = self.aboxHandler.size
        # first, generate the possible assertions of (cl(ABox)), returns a list of SupportedAssertion objects
        start_time = round(time.time(), 3)
        all_assertions = self.aboxHandler.compute_weighted_closure(self.ontologyHandler)
        inter_time0 = round(time.time(), 3)
        logger.debug(f"Number of the generated assertions: {len(all_assertions)}")
        logger.debug(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        exe_results["Closure_size"] = len(all_assertions)
        exe_results["Closure_time"] = inter_time0 - start_time

        all_queries = self.aboxHandler.get_raw_conflicts_queries(self.ontologyHandler)

        # Prepare arguments as a list of tuples
        args_list = [(sa, all_queries) for sa in all_assertions.values()]

        with Pool() as pool:
            results = pool.map(consistency_check_worker, args_list)

        # Filter out None results (i.e., unsupported assertions)
        cpi_repair = set(r for r in results if r is not None)        
        
        inter_time1 = round(time.time(), 3)
        logger.debug(f"Size of the cpi_repair: {len(cpi_repair)}")
        logger.debug(f"Time to compute the cpi_repair: {inter_time1 - inter_time0}")
        exe_results["Cpi_repair_size"] = len(cpi_repair)
        exe_results["Cpi_repair_time"] = inter_time1 - inter_time0
        
        logger.debug(f"Total time of execution: {inter_time1 - start_time}")
        exe_results["Total_time"] = inter_time1 - start_time

        return exe_results
    
    def compute_extended_cpi_repair(self, supported_assertions, conflicts):
        args = [(supported_assertion, conflicts) for supported_assertion in supported_assertions]
        with Pool() as pool:
            results = pool.map(extended_check_assertion, args)
        cpi_repair = set([result for result in results if result is not None])
        return cpi_repair

    def run_cpi_repair_on_weighted_closure(self):
        """"""
        exe_results = {}
        exe_results["ABox_size"] = self.aboxHandler.size
        # first, generate the possible assertions of (cl(ABox)), returns a list of SupportedAssertion objects
        start_time = round(time.time(), 3)
        all_assertions = self.aboxHandler.compute_weighted_closure(self.ontologyHandler)
        inter_time0 = round(time.time(), 3)
        logger.debug(f"Number of the generated assertions: {len(all_assertions)}")
        logger.debug(f"Time to compute the generated assertions: {inter_time0 - start_time}")
        exe_results["Closure_size"] = len(all_assertions)
        exe_results["Closure_time"] = inter_time0 - start_time        

        # In this version, compute the conflicts instead to run dominance checks on cpu instead of IO sql operations, conflicts are of the form (assertion1,assertion2)
        conflicts = self.aboxHandler.compute_conflicts(self.ontologyHandler)
        inter_time1 = round(time.time(), 3)
        logger.debug(f"Number of conflicts: {len(conflicts)}")
        logger.debug(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results["Conflicts_time"] = inter_time1 - inter_time0
        exe_results["Conflicts_size"] = len(conflicts)

        supports_size = sum((len(supported_assertion.supports) for supported_assertion in all_assertions.values()))
        logger.debug(f"Number of all the computed supports: {supports_size}")
        exe_results["size_all_supports"] = supports_size
        
        cpi_repair = self.compute_extended_cpi_repair(all_assertions.values(), conflicts)

        inter_time2 = round(time.time(), 3)
        logger.debug(f"Size of the cpi_repair: {len(cpi_repair)}")
        logger.debug(f"Time to compute the cpi_repair: {inter_time2 - inter_time1}")
        exe_results["Cpi_repair_size"] = len(cpi_repair)
        exe_results["Cpi_repair_time"] = inter_time2 - inter_time1
        
        logger.debug(f"Total time of execution: {inter_time2 - start_time}")
        exe_results["Total_time"] = inter_time2 - start_time

        return exe_results
    
    def select_assertion_randomly(self):
        """Selects an assertion randomly from the database to perform IC (Instance Checking)"""
        
        all_assertions = self.aboxHandler.compute_weighted_closure(self.ontologyHandler)

        selected = random.choice(list(all_assertions.values()))
        return selected

    def run_random_IC(self):
        """Runs random IC Instance checking operations using two methods, one based on dominant supports, and the other on a consistency test"""
        exe_results = {}
        
        start_time = round(time.time(), 3)
        supported_assertion = self.select_assertion_randomly()

        print(supported_assertion)
        for support in supported_assertion.supports:
            print(support)

        # the dominant supports method
        # compute the conflicts, conflicts are of the form (assertion1,assertion2)
        inter_time0 = round(time.time(), 3)
        conflicts = self.aboxHandler.compute_conflicts(self.ontologyHandler)
        inter_time1 = round(time.time(), 3)
        logger.debug(f"Number of conflicts: {len(conflicts)}")
        logger.debug(f"Time to compute the conflicts: {inter_time1 - inter_time0}")
        exe_results["Conflicts_time"] = inter_time1 - inter_time0
        exe_results["Conflicts_size"] = len(conflicts)
        
        # extract the supports of the assertion
        supports = {}
        supports[supported_assertion] = supported_assertion.supports

        inter_time1 = round(time.time(), 3)
        # Check dominance
        dominates_fn = dominates
        args = supported_assertion, conflicts, supported_assertion.supports, dominates_fn

        if check_assertion(args):
            accepted1 = True
        else: 
            accepted1 = False

        inter_time2 = round(time.time(), 3)
        logger.debug(f"Result of IC using Dominant_supports: {accepted1}")
        logger.debug(f"Time of Instance Checking (IC) using Dominant_supports: {inter_time2 - inter_time0}")
        exe_results["Dominant_supports_time"] = inter_time2 - inter_time0
        exe_results["Dominant_supports_result"] = accepted1

        # the c\pi-acceptance method
        inter_time3 = round(time.time(), 3)

        all_queries = self.aboxHandler.get_raw_conflicts_queries(self.ontologyHandler)
        accepted2 = self.aboxHandler.consistency_checking_with_condition(supported_assertion, all_queries)

        inter_time4 = round(time.time(), 3)
        logger.debug(f"Result of IC using Cpi_acceptance: {accepted2}")
        logger.debug(f"Time of Instance Checking (IC) Cpi_acceptance: {inter_time4 - inter_time3}")
        exe_results["Cpi_acceptance_time"] = inter_time4 - inter_time3
        exe_results["Cpi_acceptance_result"] = accepted2

        end_time = round(time.time(), 3)
        exe_results["Total_time"] = end_time - start_time

        return exe_results