import csv
import os

import logzero
from handlers.repair_handler import RepairHandler
from handlers.ontology_handler import OntologyHandler
from handlers.abox_handler import ABoxHandler
from load_data_to_sqldb import main
import time
from logzero import logger
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def instance_checking_experiment(ontology_path):
    start_time = time.time()
    
    ontologyHandler = OntologyHandler(ontology_path, format='application/rdf+xml')
    aboxHandler = ABoxHandler()
    aboxHandler.connect()

    mid_time = time.time()
    consistent = aboxHandler.consistency_checking(ontologyHandler)
    cons_time = time.time()

    logger.debug(f"The evaluation of the statement the ABox is consistent is: {consistent}.")
    logger.debug(f"The time to test consistency of the ABox: {cons_time - mid_time}")

    repairHandler = RepairHandler(ontologyHandler, aboxHandler)

    results = repairHandler.run_random_IC()

    # Ensure directory exists
    os.makedirs("results", exist_ok=True)
    csv_path = "results/ABox_RDF_type_and_mappingbased_objects_IC_experiments.csv"
    file_exists = os.path.isfile(csv_path)
    is_empty = not file_exists or os.stat(csv_path).st_size == 0

    # Write to CSV
    with open(csv_path, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(results.keys()))
        if is_empty:
            writer.writeheader()
        writer.writerow(results)

    end_time = time.time()
    logger.debug(f"Time to run is {end_time-start_time} seconds.")
    aboxHandler.disconnect()

def computeRepair_experiment(ontology_path):
    start_time = time.time()
    
    ontologyHandler = OntologyHandler(ontology_path, format='application/rdf+xml')
    aboxHandler = ABoxHandler()
    aboxHandler.connect()

    repairHandler = RepairHandler(ontologyHandler, aboxHandler)

    results1 = repairHandler.run_cpi_repair()
    
    results2 = repairHandler.run_cpi_repair_on_weighted_closure()

    # Combine results with prefixes
    combined_results = {}

    for k, v in results1.items():
        combined_results[f"old_method_{k}"] = v
    for k, v in results2.items():
        combined_results[f"new_method_{k}"] = v

    # Ensure directory exists
    os.makedirs("results", exist_ok=True)
    csv_path = "results/ABox_RDF_dbr_repair_experiments.csv"
    file_exists = os.path.isfile(csv_path)
    is_empty = not file_exists or os.stat(csv_path).st_size == 0

    # Write to CSV
    with open(csv_path, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(combined_results.keys()))
        if is_empty:
            writer.writeheader()
        writer.writerow(combined_results)

    end_time = time.time()
    logger.debug(f"Time to run is {end_time-start_time} seconds.")
    aboxHandler.disconnect()

names = {
    1000 : "n1e03",
    10000 : "n1e04",
    50000 : "n5e04",
    100000 : "n1e05",
    0.02 : "2e-02",
    0.05 : "5e-02",
    0.2 : "2e-01",
    0.3 : "3e-01",
    0.5 : "5e-01"
}

if __name__ == '__main__':
    """"""
    # Set a logfile
    timestamp = int(time.time())
    log_filename = f"logs/logfile_{timestamp}.log"
    logzero.logfile(log_filename)
    logger.debug('Starting...')

    tBox_file = "ontologies/DBO/ontology--DEV_type=parsed.owl"

    for size in [1000, 10000, 50000]: #1000, 10000, 50000, 100000
        for percent in [0.05, 0.3, 0.5]: #0.02, 0.2, 0.5

            data_file = f"dataset_preparation/dbr_{names[size]}_p{names[percent]}.csv"
            
            logger.info(f"Loading: {data_file.split('/')[-1]}")

            data_files = [data_file]

            # load data to postgresql database using load_data_to_sqldb.main

            useNotGreaterTable = False # for running computeRepair experiments
            main(tBox_file, data_files, useNotGreaterTable)

            computeRepair_experiment(tBox_file)

    logger.debug('Done.')