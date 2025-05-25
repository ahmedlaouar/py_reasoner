# Dataset preparation 

This folder describes step by step how the data used in our experiments is prepared.

1. The data used is from two sources of assertions in the [DBpedia ontology (DBO)](https://www.dbpedia.org/resources/ontology/) project:
    - The first is the english version of the DBpedia Ontology A-Box RDF type statements, version 2022.12.01, which can be found at https://databus.dbpedia.org/dbpedia/mappings/instance-types/, direct download link: https://downloads.dbpedia.org/repo/dbpedia/mappings/instance-types/2022.12.01/instance-types_lang=en_specific.ttl.bz2
    - The second is an earlier version from 2016-10, found at "http://downloads.dbpedia.org/2016-10/core/" under the name `instance_types_lhd_dbo_en.ttl.bz2`. Direct download link: http://downloads.dbpedia.org/2016-10/core-i18n/en/instance_types_lhd_dbo_en.ttl.bz2. This version is said to be "Changes compared to 2016-10
removed LHD EN Inference as it contained too many unclean, inferred types." on [DBpedia Databus latest-core collection](https://databus.dbpedia.org/dbpedia/collections/latest-core)[^1].

2. The data comes in the form of triples, mainly of the form: 
```triples
<http://dbpedia.org/resource/Cahora_Bassa> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/resource/Reservoir> . 
```
3. A main need in our application is to find a form of order between the triples when applicable, for that we defined three different criteria:
    - We have two distinct information sources: (1) is "2016-10/core-release", and (2) is "latest-release". (we consider (2) as more reliable than (1)).
    - Criteria of recency (the two methods retrun two different values, one for creation and the other for last edit): 
      - get last edit timestamps by name using wikipedia API.
      - get the provenance website of each resource using the property `prov:wasDerivedFrom` from DBpedia-API then get timestamps using the property `schema:dateModified` from that wiki version.

4. The resulting files, where each triple is associated with its source name and timestamps are available on [Zenodo](link to be provided later) (DOI ...) and must be placed in the current folder if one wants to use the full dataset. The two files names are `instance-types_lang=en_specific_with_2_timestamps.csv` and `instance_types_lhd_dbo_en_with_2_timestamps.csv`.

   - For loading in a postgresql database, use the script in `load_data_to_sqldb.py`.

5. We generated several versions of the dataset for our experiments: 
   - ABox size: 1000, percentage of assertions in conflicts: 0%, 2%, 25%, 50%.
   - ABox size: 10000, percentage of assertions in conflicts: 0%, 2%, 25%, 50%.
   - ABox size: 50000, percentage of assertions in conflicts: 0%, 2%, 25%, 50%.
   - ABox size: 100000, percentage of assertions in conflicts: 0%, 2%, 25%, 50%.

6. The scripts used to generate the target datasets from the initial dataset:
   - `dataset_preparation/create_consistent_datasets.py`: creates files with non-conflicting assertions (from a single source), useful for tests with a consistent ABox.
   - `dataset_preparation/create_conflicting_datasets.py`: created the raw datasets with size in [10^3, 10^4, 5*10^4, 10^5] and percentage of assertions in conflicts in [2%, 25%, 50%]

The files are large and provided seperately on [Zenodo](link to be provided later) (DOI ...).

[^1]: One of our motivations to get this dataset, the [SPARQL endpoint](https://dbpedia.org/sparql#) still returns values from it. Please conslut the main README for further motivations.