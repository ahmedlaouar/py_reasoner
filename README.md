# Guide for the experimentation study of the $C\pi$-repair

This is a guide for data preparation and result reproduction for the implementation of the closure-based partially ordered possibilistic repair ($C\pi$-repair)[1].

This implementation needs two main ingredients:

- An ontology: a [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x) TBox.
- A database: a data set representing the ABox, which may contain conflicts.

## 📌 Version & Citation

This repository is actively maintained.

If you are reading this in the context of our paper submission titled:  
**"Closure-Based Tractable Possibilistic Inference from Partially Ordered DL-Lite Ontologies"**, please refer to the tagged version of the code used in that paper:

🔗 **[https://github.com/ahmedlaouar/py_reasoner/tree/jelia2025](https://github.com/ahmedlaouar/py_reasoner/tree/jelia2025)**

This tag captures exactly the version of the code and data used for the results in that paper.  
We recommend readers use that version for reproducibility.

If you're interested in the newer or ongoing improvements, see the master branch.

This repository also contains:
- The version of the experiments from the DL2024 paper [On the Computation of a Productive Partially Ordered Possibilistic Repair](https://univ-artois.hal.science/hal-04622237/file/DL-2024-paper-6.pdf) in the branch `DL2024-version`.

### List of the most recent changes and updates:
- Integration of the DBpedia ontology and ABox in the experiments.
- A new (more efficient) method for computing the $C\pi$-repair.

## Full guide to experiments reproduction for the $c\pi$-acceptance method:

### Setting up dependencies and requirements:
- Either: install the dependencies in `requirements.txt`; or:
- Simply run the bash script `prepare.sh` (it creates a python venv for the project then installs the required libraries).

- Rapid: a DL-Lite query-rewriting tool [4]. It can be found within the [__Combo__](https://home.uni-leipzig.de/clu/) project and also within the systems studied in the [__ForBackBench__](https://github.com/georgeKon/ForBackBench/tree/main) benchmarking framework (for Chasing Vs Query Rewriting).
- Note: the Rapid tool is build with java, hence, a java installation must be present in order to be able to make calls to this tool.

- Prepare a local postgresql database and create a local `.env` file in which the following information should be added:
  - DB_NAME=[db_name]
  - DB_USER=[username]
  - DB_PASSWORD=[pswd]
  - DB_HOST=[localhost]
  - DB_PORT=[port]

  👉 For help setting up PostgreSQL locally, see the [official PostgreSQL documentation](https://www.postgresql.org/docs/current/tutorial-install.html) or follow this [DigitalOcean guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-22-04).

### Load full data-sets from Zenodo:
- The original data is saved in (3) separate files, representing data sources from DBpedia ontology and datasets (redristributed here under the licence).
- We augmented the data with timestamps from the Wikipedia API and using timestamps from the wiki version data was derived from (using the object property `prov:wasDerivedFrom`).
- We provide full-augmented data in [Zenodo](https://doi.org/10.5281/zenodo.15605504) (DOI 10.5281/zenodo.15605504) in (3) separate files:
  - `instance-types_lang=en_specific_with_timestamps.csv`
  - `instance_types_lhd_dbo_en_with_timestamps.csv`
  - `mappingbased-objects_lang=en_with_timestamps.csv`

#### Option 1: re-extract the ABoxes: 
- Load the full-augmented datasets into the PostgreSQL database: run the script in `dataset_preparation/load_full_data.py` as a module using:
```python
python3 -m dataset_preparation.load_full_data
```

- Then, use the script in `dataset_preparation/create_conflicting_datasets.py` to generate the conflicting ABoxes by running:

```python
python3 -m dataset_preparation.create_conflicting_datasets
```
(must be run as module to avoid importing exceptions)

- We also generated consistent ABoxes to fully test our system: simply run the script in `dataset_preparation/create_consistent_datasets.py`

The script randomly samples assertions from one datasource and populates them to the postgresql database.


#### Option 2 (faster): use the provided ABoxes directly from Zenodo:
Load prepared ABoxes from Zenodo: avoid data preparation and use our ABoxes directly:
- A small dataset (1k and 10k assertions) provided within the github project.
- The remaining files are all provided in [Zenodo](https://doi.org/10.5281/zenodo.15605504) (DOI 10.5281/zenodo.15605504).

*** Before running the experiments, copy the data downloaded from Zenodo to the folder `dataset_preparation/` ***

### Re-run experiments:
- The main `py_reasoner` implementation scripts are under the `core` folder.

- Use the script in `core/run_experiments.py` to re-launch full experimental evaluation.

- The results are saved in the folder: `results`, the main result files are `results/ABox_RDF_type_experiments_larger_repair.csv`, `ABox_RDF_dbr_repair_experiments.csv` and `results/ABox_RDF_type_experiments_smaller_repair.csv`.

  The files contain similar results, the difference is that of using different subsets containing either only concept assertions, role assertions or both.

- The analysis and plots generation is done in the notebook in `core/results_stats.ipynb`.
  Re-run cells to reproduce the figures saved in `results/figures`.

## License

This project's code and analysis is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

## Source of Data

This project includes data extracted and derived from [DBpedia](https://www.dbpedia.org/), which is licensed under the [Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA 3.0)](https://creativecommons.org/licenses/by-sa/3.0/).
These files are marked accordingly and must be used under the terms of that license.

Modifications and annotations were performed by the authors of this project.

© DBpedia contributors. All rights reserved.


## References:

[1] A. Laouar, S. Belabbes, S. Benferhat, Tractable closure-based possibilistic repair for partially ordered dl-lite ontologies, in: European Conference on Logics in Artificial Intelligence, Springer, 2023, pp. 353–368

[2] Benferhat, S., Bouraoui, Z., Tabia, K.: How to select one preferred assertional-based repair from inconsistent and prioritized DL-Lite knowledge bases? In: International Joint Conference on Artificial Intelligence (IJCAI), Buenos Aires, Argentina. pp. 1450–1456 (2015)

[3] Belabbes, S., Benferhat, S.: Computing a possibility theory repair for partially preordered inconsistent ontologies. IEEE Transactions on Fuzzy Systems pp. 1–10 (2021)

[4] A. Chortaras, D. Trivela, G. Stamou, Optimized query rewriting for owl 2 ql, in: Automated Deduction–CADE-23: 23rd International Conference on Automated Deduction, Wrocław, Poland, July 31-August 5, 2011. Proceedings 23, Springer, 2011, pp. 192–206.

[5] C. Lutz, I. Seylan, D. Toman, F. Wolter, The combined approach to OBDA: taming role hierarchies using filters, in: The Semantic Web - ISWC 2013 - 12th International Semantic Web Conference, Sydney, Australia, 2013, pp. 314–330.

[6] M. Scutari, Learning bayesian networks with the bnlearn r package, arXiv preprint arXiv:0908.3817 (2009).


<!--- ### Interface with the system:

- Check the consistency of an ABox:

- Compute a repair using one of the methods:

- Check the $c\pi$-acceptance of a given assertion:

  - randomly select one:
  
  - provide your assertion: -->


<!---
## Libraries and tools

- Python.
- The [__RDFLib__](https://github.com/RDFLib/rdflib): a python library to read from the OWL ontology.
- Rapid: a DL-Lite query-rewriting tool [4]. It can be found within the [__Combo__](https://home.uni-leipzig.de/clu/) project and also within the systems studied in the [__ForBackBench__](https://github.com/georgeKon/ForBackBench/tree/main) benchmarking framework (for Chasing Vs Query Rewriting).
- SQLite3 relational database engine.
- The [__bnlearn__](https://www.bnlearn.com/) R package[6]: to generate random Directed Acyclic Graphs (DAGs) which represent partially ordered sets of weights.

Note: the Rapid tool is build with java, hence, a java instalation must be present in order to be able to make calls to this tool.

## The ontology

In the experiments, we used the [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x) version of the modified LUBM benchmark (LUBM $^{\exists}_{20}$), which was presented in [5]. It is available within the [__Combo__](https://home.uni-leipzig.de/clu/) project. 

This version of the ontology does not contain any disjointness (or negative) axioms, namely owl:disjointWith and owl:propertyDisjointWith axioms. We manually added 18 different negative axioms, which lead to 4561 negative axioms in the negative closure of the TBox. The list of the added axioms is availabe in the file [bench_prepa/docs/axioms_list.md](bench_prepa/docs/axioms_list.md).

Since the TBox is assumed to be coherent in this type of experiments, we used a fixed ontology and focused on varying data.

## The data

The data was generated from the ontology, using the Extended University Data Generator v0.1 (EUDG), which is a part of the [__Combo__](https://home.uni-leipzig.de/clu/) project. This tool is written in java.

### From owl data file to a sqlite3 database file

The EUDG tool generates a dataset, in the form of an owl file. we use the script [bench_prepa/owl_prepa/owl_data_to_db.py](bench_prepa/owl_prepa/owl_data_to_db.py) to transform the data to a sqlite database. 

The following command is an exmaple of use, the ontology owl file should be provided (option `--owl`) alongside the data owl file (option `--owl_data`) generated by the EUDG tool and the target database file (option `--db`):

```
python3 bench_prepa/owl_prepa/owl_data_to_db.py --owl ontologies/univ-bench/lubm-ex-20_disjoint.owl --db bench_prepa/dataset_1_university/University0.db --owl_data bench_prepa/dataset_1_university/University0.owl
```

We generated three different sizes for the datasets: 9156, 75671 and 463349 assertions.

### Adding conflicts to the data

The datasets obtained using the previous steps are consistent (free of conflicts). The conflicts are randomly added to the data as follows. For each negative axiom inferred from the ontology, individuals present in a concept assertion are added to a contradicting assertion with probability $p$, and individuals present in a role assertion are added to a contradicting assertion with probability $p/2$. We used increasing values for $p$ to obtain five different ratios of inconsistency for each ABox. Values in $\{5 \times 10^{-6}, 10^{-5}, 5 \times 10^{-5}, 10^{-4}, 5 \times 10^{-4}\}$ were used, different values may be used for different ABoxes to introduce certain levels of inconsistency. 

The script in [bench_prepa/owl_prepa/add_conflicts_to_db.py](bench_prepa/owl_prepa/add_conflicts_to_db.py) was used to add the conflicts.

The following command is an example of use, the script takes the ontology owl file (option `--owl`), a database file (option `--db`) and a probability as a float (option `-p`):

```
python3 bench_prepa/owl_prepa/add_conflicts_to_db.py --owl ontologies/univ-bench/lubm-ex-20_disjoint.owl --db bench_prepa/dataset_small_u1/university0.5_p_0.001.db -p 0.00005
```
Note that we create a copy of the database .db file before running this command, to keep a copy of the original free of conflict database file and to keep all the files generated in the experiment.

## Partially ordered sets (POSets)

In order to represent the partial order defined over the dataset, we associate weights to the assertions. These weights belong to a partially ordered set. We opted for random Directed Acyclic Graphs to represent these sets. We used the [__bnlearn__](https://www.bnlearn.com/) R package to generate different types of DAGs, the goal is to capture different situations of POSets. In a DAG, the number of nodes indicates the size of the POSet (number of weights) to be associated with the assertions, an arc between two assertions indicate the preference relation and the absence of an arc in both directions between two nodes encodes incomparability. The probability of having an arc represents the density of the DAG, a more dense DAG has less incomparabilities and is closer to a totally ordered set, a DAG with all possible arcs represent a totally ordered set. Generated DAGs vary in size from $\{50,100,250,500,750,1000,2500\}$ and in the probability of having an arc between two nodes which is varied from $[0.1,\dots,0.9]$.

The code to generate the DAGs is available in the script [bench_prepa/owl_prepa/pos_generator_bnlearn.r](bench_prepa/owl_prepa/pos_generator_bnlearn.r). In the script, setting the parameter `num_nodes` to `100` creates DAGs with probablities varying from `0.1` to `0.9`:

``` 
Rscript bench_prepa/owl_prepa/pos_generator_bnlearn.r
```

Each generated DAG is saved in a txt file, where in each line, a source node is associated to the target nodes to which its arcs are pointing. The script in [bench_prepa/owl_prepa/complete_pos.py](bench_prepa/owl_prepa/complete_pos.py) completes all the DAGs under the folder [bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method](bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method) with all the indirect arcs.
```
python3 py_reasoner/bench_prepa/owl_prepa/complete_pos.py
```

Before any execution of the repairing algorithms, weights from a specified DAG are randomly assigned to the assertions (tuples in the database). The function `add_pos_to_db(data_path:str, pos_path:str)` from [src/repair/utils.py](src/repair/utils.py) makes this step.

The POSet is read into a dictionnary, where each node points to all its direct and indirect less preferred nodes, this makes the preferrence checking process equivalent to reading values of a given key from a dictionnary.

All the data preparation and POSet (DAG) generation and completion scripts can be found under the folder [bench_prepa/owl_prepa](bench_prepa/owl_prepa).

## The $\pi$-repair
The $\pi$-repair can be computed using the function `compute_pi_repair(ontology_path: str, data_path: str, pos_path: str)` in [src/repair/owl_pi_repair.py](src/repair/owl_pi_repair.py). It takes paths to the ontology, the database file of the ABox and the POSet. The resulting repair is a `set()` of assertions. 

This function makes calls to the following functions:

- `get_all_abox_assertions()` from [src/repair/owl_assertions_generator.py](src/repair/owl_assertions_generator.py): this function read all the assertions in the provided sqlite database and returns them as objects of the class `assertion` from [src/dl_lite/assertion.py](src/dl_lite/assertion.py)
- `compute_conflicts()` from [src/repair/owl_conflicts.py](src/repair/owl_conflicts.py): this function reads all the negative axioms of the ontology, generate a conjunctive query (CQ) for each, rewrites the query using the Rapid tool (it makes a single external java call), the resulting CQs are transformed to sql queries and executed on the sqlite datbase. The results of the querying here are conflicts of the form `((table1name, id, degree),(table2name, id, degree))`. This is the minimal form we can get about an assertion in the database, since the most important information are the degrees of the assertions in a conflict.

Run the following command to see an exmaple of the computation of the conflicts:

```
python3 src/py_reasoner.py compute_conflicts --abox bench_prepa/dataset_small_u1/university0.5_p_0.00001.db --tbox ontologies/univ-bench/lubm-ex-20_disjoint.owl
```

- `compute_pi_repair_raw()` iterates over all the assertions and verifies if each assertion is at least more certain than an element of each conflict to return it in the resulting repair. Function `dominates()` from [src/repair/owl_dominance.py](src/repair/owl_dominance.py) makes the strict order checking. Note that we used `multiprocessing.Pool()` to parallelize the loop.

Run the following command to see an exmaple for computing the $\pi$-repair of the ABox: `bench_prepa/dataset_small_u1/university0.5_p_0.00001.db` with the DAG `bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt`

```
python3 src/py_reasoner.py compute_pi_repair --abox bench_prepa/dataset_small_u1/university0.5_p_0.00001.db --tbox ontologies/univ-bench/lubm-ex-20_disjoint.owl --pos bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt 
```
The result prompt should be similar to the following:
```
Computing pi-repair for the ABox: university0.5_p_0.00001.db and the TBox: lubm-ex-20_disjoint.owl with the POS: prob_0.3.txt
Size of the ABox: 9158.
Number of the generated assertions: 9158
Time to compute the generated assertions: 0.023
Number of the conflicts: 1
Time to compute the conflicts: 1.988
Size of the pi_repair: 2603
Time to compute the pi_repair: 0.184
Total time of execution: 2.196
```

## The $C\pi$-repair
The $C\pi$-repair can be computed either using the function `compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str)` from [src/repair/owl_cpi_repair.py](src/repair/owl_cpi_repair.py) or the function `compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str)` from [src/repair/owl_cpi_repair_enhanced.py](src/repair/owl_cpi_repair_enhanced.py).

### The naive $C\pi$-repair
The function `compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str)` from [src/repair/owl_cpi_repair.py](src/repair/owl_cpi_repair.py) makes calls to the folowing functions:

- `generate_assertions()` from [src/repair/owl_assertions_generator.py](src/repair/owl_assertions_generator.py): this funtion computes the deductive closure of the ABox under classical semantics. It generates a query for each concept and role name in the ontology, rewrites the query to obtain all its candidate supports. It executes the queries on the sqlite database, the answers are associates with the initial concept or role name, before creating an assertion for each result.
- In the same way above, it calls the function `compute_conflicts()` from [src/repair/owl_conflicts.py](src/repair/owl_conflicts.py) to get all the conflicts of the ABox.
- It takes each generated assertion and computes its supports, using the function `compute_all_supports()` from [src/repair/owl_supports.py](src/repair/owl_supports.py). This function creates an instance checking query for each assertion, rewrites the query to get the instance checking queries of its supports. It then transforms the queries into sql queries before executing them on the sqlite database. For the queries with True as result, a support of the assertion is returned.
- Having all the conflicts and the supports, for each assertion `compute_cpi_repair_raw()` checks if for each conflict, at least one of its supports dominates the conflict. Function `dominates()` from [src/repair/owl_dominance.py](src/repair/owl_dominance.py) makes the dominance checking. Note that we used `multiprocessing.Pool()` to parallelize the loop.

The resulting repair is a `set()` of assertions. 

Run the following command for an example for computing the $C\pi$-repair of the ABox: `bench_prepa/dataset_small_u1/university0.5_p_0.00001.db` with the DAG `bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt` using the naive method:
```
python3 src/py_reasoner.py compute_cpi_repair --abox bench_prepa/dataset_small_u1/university0.5_p_0.00001.db --tbox ontologies/univ-bench/lubm-ex-20_disjoint.owl --pos bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt
```
The result prompt should be similar to the following:
```
Computing Cpi-repair for the ABox: university0.5_p_0.00001.db and the TBox: lubm-ex-20_disjoint.owl with the POS: prob_0.3.txt
Size of the ABox is 9158.
Number of the generated assertions: 25345
Time to compute the generated assertions: 1.461
Number of conflicts: 40
Time to compute the conflicts: 2.336
Number of all the computed supports: 25466
Time to compute all the supports of all the assertions: 31.033
Size of the cpi_repair: 9929
Time to compute the cpi_repair: 1.389
Total time of execution: 36.221
```
### The enhanced $C\pi$-repair
In this version, the function `compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str)` from [src/repair/owl_cpi_repair_enhanced.py](src/repair/owl_cpi_repair_enhanced.py) starts first by:

- Computing the $\pi$-repair as showed above. 
- Then, it generates the assertions of the deductive closure of the ABox under classical semantics. 
- Assertions of the $\pi$-repair are discarded from the generated assertions.
- The closure of the $\pi$-repair is computed using the function `compute_cl_pi_repair()` from [src/repair/owl_supports.py](src/repair/owl_supports.py), it consists of all the assertions that can be inferred from the $\pi$-repair, and thus no need to verify them using the $C\pi$-repair method.
- Now, for the remaining assertions, which are not in the $\pi$-repair or its closure, the supports are computed using `compute_all_supports()` from [src/repair/owl_supports.py](src/repair/owl_supports.py). Note that at this level, any assertion that has only one support, cannot be in the $C\pi$-repair. Therefore, assertions with a single support are discarded from the following verification.
- For each remaining assertion `compute_cpi_repair_raw()` is called, as in the naive method, to check if for each conflict, the assertion has at least one support that dominates the conflict.

Run the following command for an example for computing the $C\pi$-repair of the ABox: `bench_prepa/dataset_small_u1/university0.5_p_0.00001.db` with the DAG `bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt` using the improved method:
```
python3 src/py_reasoner.py compute_cpi_repair_improved --abox bench_prepa/dataset_small_u1/university0.5_p_0.00001.db --tbox ontologies/univ-bench/lubm-ex-20_disjoint.owl --pos bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos500/prob_0.3.txt
```
The result prompt should be similar to the following:
```
Computing cpi-repair for the ABox: university0.5_p_0.00001.db and the TBox: lubm-ex-20_disjoint.owl with the POS: prob_0.3.txt
Size of the ABox: 9158.
Number of the ABox assertions: 9158
Time to load the ABox assertions: 0.032
Number of new generated assertions: 16187
Time to compute the generated assertions: 1.484
Number of the conflicts: 14
Time to compute the conflicts: 1.484
Size of the pi_repair: 1097
Time to compute the pi_repair: 2.374
The number of assertions left to check: 24248
Size of cl_pi_repair: 2561
Time to compute the cl_pi_repair: 2.163
Number of all the computed supports before filtering: 15149
Number of all the computed supports: 166
Time to compute all the supports of all the assertions: 24.311
Size of the cpi_repair: 3658
Time to compute the cpi_repair: 0.124
Total time of execution: 30.488
```
Note that in the ABove examples of execution, each time a new random assigning of weights from the POset is done. A proper way to evaluate the algorthms is by computing the $\pi$-repair and the $C\pi$-repair using both methods with the same weights assigned to the ABox. 

## Results
The ontology can be found in:
- [ontologies/univ-bench/lubm-ex-20_disjoint.owl](ontologies/univ-bench/lubm-ex-20_disjoint.owl)

The different used datasets can be found under the folders:

- [bench_prepa/dataset_1_university](bench_prepa/dataset_1_university)
- [bench_prepa/dataset_small_u1](bench_prepa/dataset_small_u1)
- [bench_prepa/dataset.0.2](bench_prepa/dataset.0.2)

The POSets can be found under the folder: 

- [bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method](bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method). 
- Other types of POSets were also explored, like the uniform random DAGs generated using the methods `ic-dag` and `melancon` (in folders: [bench_prepa/DAGs/DAGs_with_bnlearn/ic-dag_method](bench_prepa/DAGs/DAGs_with_bnlearn/ic-dag_method) and [bench_prepa/DAGs/DAGs_with_bnlearn/melancon_method](bench_prepa/DAGs/DAGs_with_bnlearn/melancon_method)). These DAGs gave similar results.

For our experiments, we computed the repairs of all the ABoxes in the datasets folders assigned with each of the DAGs in the folder [bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method](bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method) using the script in [src/main2.py](src/main2.py).

For result reproduction, a lot of executions are done, we separated the executions with ABoxes sizes. Running only for the small sized ABoxes in [bench_prepa/dataset_small_u1](bench_prepa/dataset_small_u1) is fast and illustrates how experiments work. 

<!--- Experiments results are saved in csv files under the folder [bench_prepa/execution_results](bench_prepa/execution_results). 

Summary of the results, including charts and plots are found under the folder [bench_prepa/results](bench_prepa/results). -->


<!--- ## Future works

The next steps in this project are:
- 
- 
- -->

<!--- ## More

The main focus of this work is a subset of methods for data repairs that operates in the context of possibilistic Knowledge Bases and more specifically on partially ordered KBs.  
[__Possiblistic DL-Lite__](https://link.springer.com/chapter/10.1007/978-3-642-40381-1_27) extends the expressive power of DL-Lite to deal with possibilistic uncertain information without increasing the computational cost. -->
