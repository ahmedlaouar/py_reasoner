import random
from assertion import assertion
from core.handlers.repair_handler import RepairHandler
from handlers.ontology_handler import OntologyHandler
from handlers.abox_handler import ABoxHandler
from load_data_to_sqldb import main
import time
from logzero import logger
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

names = {
    1000 : "n1e03",
    10000 : "n1e04",
    50000 : "n5e04",
    100000 : "n1e05",
    0.02 : "2e-02",
    0.2 : "2e-01",
    0.5 : "5e-01"
}

if __name__ == '__main__':
    """"""

    start_time = time.time()
    ontology_path = "ontologies/DBO/ontology--DEV_type=parsed.owl"
    ontologyHandler = OntologyHandler(ontology_path, format='application/rdf+xml')

    aboxHandler = ABoxHandler()
    aboxHandler.connect()
    
    """assertions_list = [ ['http://dbpedia.org/ontology/Agent', 'http://dbpedia.org/resource/Number_18_School_in_Marshall'],['http://dbpedia.org/ontology/Place', 'http://dbpedia.org/resource/Number_18_School_in_Marshall'],['http://dbpedia.org/ontology/Building', 'http://dbpedia.org/resource/Isabel_Marant'],['http://dbpedia.org/ontology/Person', 'http://dbpedia.org/resource/Isabel_Marant'],["http://dbpedia.org/ontology/Settlement","http://dbpedia.org/resource/Ca_Pierre"]]
    assertions =[]
    for element in assertions_list:
        assertions.append(assertion(assertion_name=element[0], individual_0=element[1],)) # derivationTimestamp = element[2], wikiTimestamp = element[3], source = element[4]))
    
    supports = aboxHandler.compute_supports(assertions, ontologyHandler)

    for assertion_i, supports_i in supports.items():
        logger.debug(f"The supports of {assertion_i} are the assertions:")
        for support_i in supports_i:
            logger.debug(support_i)
        logger.debug(f"The number of supports of the assertion {assertion_i} is: {len(supports[assertion_i])}.")"""
    
    #assertions_to_check = aboxHandler.compute_closure(ontologyHandler)

    #logger.debug(f"The number of all the possible assertions of this ABox (closure size): {len(assertions_to_check)}.")

    size = 50000
    percent = 0.02
    data_file = f"dataset_preparation/it_{names[size]}_p{names[percent]}.csv"

    data_file = "dataset_preparation/instance-types_lang=en_specific_with_timestamps.csv" # "dataset_preparation/instance_types_lhd_dbo_en_with_timestamps.csv" # 

    logger.info(f"Loading: {data_file.split('/')[-1]}")

    # load data to postgresql database using load_data_to_sqldb.main
    main(ontology_path, [data_file])

    conflicts = aboxHandler.compute_conflicts(ontologyHandler)

    #consistent = aboxHandler.consistency_checking(ontologyHandler)

    for a1,a2 in conflicts:
        print(a1,a2)
    
    #repairHandler = RepairHandler(ontologyHandler, aboxHandler)

    #results = repairHandler.run_cpi_repair()

    #for cle, valeur in results.items():
    #    logger.debug(f"{cle}: {valeur}")
    
    #results = repairHandler.run_cpi_repair_on_weighted_closure()

    #for cle, valeur in results.items():
    #    logger.debug(f"{cle}: {valeur}")
    
    #assertions_to_check = aboxHandler.compute_weighted_closure(ontologyHandler)

    #logger.debug(f"The number of all the possible assertions of this ABox (weighted closure size): {len(assertions_to_check.values())}.")

    #logger.debug(f"The number of all the possible supports for these assertions in the weighted closure: {sum((len(assertion_i.supports) for assertion_i in assertions_to_check.values()))}.")
    
    #for assertion_i in assertions_to_check.values():
    #    print(assertion_i)
    #    print("---------------------")
    #    for supp in assertion_i.supports:
    #        print(supp)
    #    break

    end_time = time.time()

    #logger.debug(f"The number of conflicts of this database = {len(conflicts)}.")
    #logger.debug(f"The evaluation of the statement the ABox is consistent is: {consistent}.")

    logger.debug(f"Time to run is {end_time-start_time} seconds.")

    aboxHandler.disconnect()