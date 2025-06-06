import time
from core.handlers.ontology_handler import OntologyHandler
from core.handlers.abox_handler import ABoxHandler
from core.load_data_to_sqldb import main
from logzero import logger

if __name__ == '__main__':
    """"""

    start_time = time.time()
    ontology_path = "ontologies/DBO/ontology--DEV_type=parsed.owl"
    ontologyHandler = OntologyHandler(ontology_path, format='application/rdf+xml')

    aboxHandler = ABoxHandler()
    aboxHandler.connect()

    d1 = "dataset_preparation/instance-types_lang=en_specific_with_timestamps.csv" 
    d2 = "dataset_preparation/instance_types_lhd_dbo_en_with_timestamps.csv"  
    r1 = "dataset_preparation/mappingbased-objects_lang=en_with_timestamps.csv"

    data_files = [d1, d2, r1]

    main(ontology_path, data_files)


    end_time = time.time()    
    

    logger.debug(f"Time to run is {end_time-start_time} seconds.")

    aboxHandler.disconnect()