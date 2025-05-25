from logzero import logger
import random
from core.handlers.abox_handler import ABoxHandler
from core.handlers.ontology_handler import OntologyHandler

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

names = {
    1000 : "n1e03",
    10000 : "n1e04",
    50000 : "n5e04",
    100000 : "n1e05",
    0.02 : "2e-02",
    0.2 : "2e-01",
    0.5 : "5e-01"
}

def generate_conflicting_dataset(conflicts, size, percent_in_conf):
    """This functions will generate a csv file of the form: 
    <http://dbpedia.org/resource/PLA2G6>|<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>|<http://dbpedia.org/ontology/HumanGene>|"2022-07-26T05:19:25Z"^^xsd:dateTime|"2024-07-07T05:28:44Z"^^xsd:dateTime|instance-types_lang=en_specific
    By injecting the wanted number of assertions in conflicts to it (computed from percent_in_conf and target size), 
    it first uses the function to computes the conflicts using: conflicts = aboxHandler.compute_conflicts(ontologyHandler)
    It should also make sure to keep track of any already added assertion from a previous conflict.
    Once the number of assertions in conflicts reached, it should fill the rest with random lines from the file "dataset_preparation/instance-types_lang=en_specific_with_timestamps_100000.csv"
    To simplify things, a conflict is formed of two assertions (assertion1, assertion2) and an assertion should be casted to a line as follows:
    |<assertion.get_individuals()[0]><http://www.w3.org/1999/02/22-rdf-syntax-ns#type>|<assertion.get_assertion_name()>|"assertion.get_derivationTimestamp()"^^xsd:dateTime|"assertion.get_wikiTimestamp()"^^xsd:dateTime|assertion.get_source()
    
    The filling lines from the csv file should just be copied as they are, no change is needed for them.
    """

    # output_file = f"dataset_preparation/instance-types_with_timestamps_{size}_p_{percent_in_conf}.csv"

    output_file = f"dataset_preparation/it_{names[size]}_p{names[percent_in_conf]}.csv"

    source_file = "dataset_preparation/it_100000.csv"
    
    conflict_limit = int(size * percent_in_conf)
    added_assertions = set()
    lines = []

    def format_assertion(a):
        if not a.is_role():
            return f"<{a.get_individuals()[0]}>|<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>|<{a.get_assertion_name()}>|\"{a.get_derivationTimestamp()}\"^^xsd:dateTime|\"{a.get_wikiTimestamp()}\"^^xsd:dateTime|{a.get_source()}\n"
        else:
            return f"<{a.get_individuals()[0]}>|<{a.get_assertion_name()}>|<{a.get_individuals()[1]}>|\"{a.get_derivationTimestamp()}\"^^xsd:dateTime|\"{a.get_wikiTimestamp()}\"^^xsd:dateTime|{a.get_source()}\n"

    # Step 2: Add conflicting assertions until the limit is reached
    for a1, a2 in conflicts:
        if len(added_assertions) >= conflict_limit:
            break
        key1 = (a1.get_assertion_name(), *a1.get_individuals())
        key2 = (a2.get_assertion_name(), *a2.get_individuals())
        if key1 not in added_assertions:
            lines.append(format_assertion(a1))
            added_assertions.add(key1)
        if len(added_assertions) >= conflict_limit:
            break
        if key2 not in added_assertions:
            lines.append(format_assertion(a2))
            added_assertions.add(key2)

    # Step 3: Fill the rest with random lines from the base dataset (as raw lines, unmodified)
    remaining = size - len(lines)
    if remaining > 0:
        with open(source_file, 'r', encoding='utf-8') as f:
            reservoir = []

            for i, line in enumerate(f):
                if i < remaining:
                    reservoir.append(line)
                else:
                    j = random.randint(0, i)
                    if j < remaining:
                        reservoir[j] = line

        lines.extend(reservoir)

    # Step 4: Write all to the output file
    with open(output_file, 'w', encoding='utf-8') as out:
        out.writelines(lines)

    return len(lines)

if __name__ == '__main__':
    """"""

    percents = [0.02, 0.2, 0.5]
    sizes = [1000, 10000, 50000, 100000]

    ontology_path = "ontologies/DBO/ontology--DEV_type=parsed.owl"
    ontologyHandler = OntologyHandler(ontology_path, format='application/rdf+xml')

    aboxHandler = ABoxHandler()

    aboxHandler.connect()

    # Step 1: Get conflicts
    conflicts = aboxHandler.compute_conflicts(ontologyHandler)
    random.shuffle(conflicts)

    for percent in percents:
        for size in sizes:
            lines = generate_conflicting_dataset(conflicts, size, percent)

            logger.debug(f"Created a raw data file of {lines} assertions and {percent} of the assertions in conflicts.")

    logger.debug('Done.')