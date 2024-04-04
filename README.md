# Guide for the experimentation study of the $C\pi$-repair

This is a guide for data preparation and result reproduction for the implementation of the closure-based partially orered possibilsitic repair ($C\pi$-repair)[1].

This implementation needs three main ingredients:

- An ontology: a [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x) TBox.
- A database: a data set representing the ABox, may contain conflicts.
- A partially ordered set: represents the set of weights to be associated with the database elements, it expresses partial order independently from the ABox.

## Libraries and tools

- Python.
- The [__RDFLib__](https://github.com/RDFLib/rdflib): a python library to read from the OWL ontology.
- Rapid: a DL-Lite query-rewriting tool [4]. It can be found within the [__Combo__](https://home.uni-leipzig.de/clu/) project and also within the systems studied in the [__ForBackBench__](https://github.com/georgeKon/ForBackBench/tree/main) benchmarking framework (for Chasing Vs Query Rewriting).
- SQLite3 relational database engine.
- The [__bnlearn__](https://www.bnlearn.com/) R package[6]: to generate random Directed Acyclic Graphs (DAGs) which represent partially ordered sets of weights.

Note: the Rapid tool is build with java, hence, a java instalation must be present in order to be able to make calls to this tool.

## The ontology

In the experiments, we used the [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x) version of the modified LUBM benchmark (LUBM $^{\exists}_{20}$), which was presented in [5]. It is available within the [__Combo__](https://home.uni-leipzig.de/clu/) project. 

This version of the ontology does not contain any disjointness (or negative) axioms, namely owl:disjointWith and owl:propertyDisjointWith axioms. We manually added 18 different negative axioms, which lead to 4561 negative axioms in the negative closure of the TBox. Since the TBox is assumed to be coherent in this type of experiments, we used a fixed ontology and focused on varying data.

## The data

The data was generated from the ontology, using the Extended University Data Generator v0.1 (EUDG), which is a part of the [__Combo__](https://home.uni-leipzig.de/clu/) project. This tool is written in java.

The EUDG tool generates a consistent (free of conflicts) dataset, in the form of an owl file. we start by using the functions in "bench_prepa/owl_prepa/owl_data_to_db.py" to transform the data to a sqlite database. We generated three different sizes for the datasets: $9156$, $75671$ and $463349$ assertions.

Then conflicts are randomly added to the data as follows. For each negative axiom inferred from the ontology, individuals present in a concept assertion are added to a contradicting assertion with probability $p$, and individuals present in a role assertion are added to a contradicting assertion with probability $p/2$. We used increasing values for $p$ to obtain five different ratios of inconsistency for each ABox. Values in $\{5 \times 10^{-6}, 10^{-5}, 5 \times 10^{-5}, 10^{-4}, 5 \times 10^{-4}\}$ were used, different values may be used for different ABoxes to introduce certain levels of inconsistency. Functions in "bench_prepa/owl_prepa/add_conflicts_to_db.py" were used to add the conflicts.

## Partially ordered sets (POSets)

In order to represent the partial order defined over the dataset, we associate weights to the assertions. These weights belong to a partially ordered set. We opted for random Directed Acyclic Graphs to represent these sets. We used the [__bnlearn__](https://www.bnlearn.com/) R package to generate different types of DAGs, the goal is to capture different situations of POSets. In a DAG, the number of nodes indicate the size of the POSet (number of weights) to be associated with the assertions, an arc between two assertions indicate the preference relation and the absence of an arc in both directions between two nodes encodes incomparability. The probability of having an arc represents the density of the DAG, a more dense DAG has less incomparabilities and is closer to a totally ordered set, a DAG with all possible arcs represent a totally ordered set. 

The code to generate the DAGs is available in "bench_prepa/owl_prepa/pos_generator_bnlearn.r". Generated DAGs vary in size from {$50,100,250,500,750,1000,2500$} and in the probability of having an arc between two nodes which is varied from [$0.1, \dots,0.9$]. Each generated DAG is saved in a txt file, where in each line, a source node is associated to the target nodes to which its arcs are pointing. Functions in "bench_prepa/owl_prepa/complete_pos.py" are used to add all indirect arcs explicitly to the generated file.

Before any execution of the repairing algorithms, weights from a specified DAG are randomly assigned to the assertions (tuples in the database). The function "add_pos_to_db(data_path:str, pos_path:str)" from "src/repair/utils.py" makes this step.

The POSet is read into a dictionnary, where each node points to all its direct and indirect less preferred nodes, this makes the preferrence checking process equivalent to reading values of a given key from a dictionnary.

## The $\pi$-repair
The $\pi$-repair can be computed using the function "compute_pi_repair(ontology_path: str, data_path: str, pos_path: str)" in "src/repair/owl_pi_repair.py". It takes paths to the ontology, the database file of the ABox and the POSet. The resulting repair is a "set()" of assertions. 

This function makes calls to the following functions:

- "get_all_abox_assertions()" from "src/repair/owl_assertions_generator.py": this function read all the assertions in the provided sqlite database and returns them as objects of the class "assertion" from "src/dl_lite/assertion.py"
- "compute_conflicts()" from "src/repair/owl_conflicts.py": this function reads all the negative axioms of the ontology, generate a conjunctive query (CQ) for each, rewrites the query using the Rapid tool (it makes a single external java call), the resulting CQs are transformed to sql queries and executed on the sqlite datbase. The results of the querying here are conflicts of the form "((table1name, id, degree),(table2name, id, degree))". This is the minimal form we can get about an assertion in the database, since the most important information are the degrees of the assertions in a conflict.
- "compute_pi_repair_raw()" iterates over all the assertions and verifies if each assertion is at least more certain than an element of each conflict to return it in the resulting repair. Function "dominates()" from "src/repair/owl_dominance.py" makes the strict order checking. Note that we used "multiprocessing.Pool()" to parallelize the loop.

## The $C\pi$-repair
The $C\pi$-repair can be computed either using the function "compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str)" from "src/repair/owl_cpi_repair.py" or the function "compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str)" from "src/repair/owl_cpi_repair_enhanced.py".

### The naive $C\pi$-repair
The function "compute_cpi_repair(ontology_path: str, data_path: str, pos_path: str)" from "src/repair/owl_cpi_repair.py" makes calls to the folowing functions:

- "generate_assertions()" from "src/repair/owl_assertions_generator.py": this funtion computes the deductive closure of the ABox under classical semantics. It generates a query for each concept and role name in the ontology, rewrites the query to obtain all its candidate supports. It executes the queries on the sqlite database, the answers are associates with the initial concept or role name, before creating an assertion for each result.
- In the same way above, it calls the function "compute_conflicts()" from "src/repair/owl_conflicts.py" to get all the conflicts of the ABox.
- It takes each generated assertion and computes its supports, using the function "compute_all_supports()" from "src/repair/owl_supports.py". This function creates an instance checking query for each assertion, rewrites the query to get the instance checking queries of its supports. It then transforms the queries into sql queries before executing them on the sqlite database. For the queries with True as result, a support of the assertion is returned.
- Having all the conflicts and the supports, for each assertion "compute_cpi_repair_raw()" checks if for each conflict, at least one of its supports dominates the conflict. Function "dominates()" from "src/repair/owl_dominance.py" makes the dominance checking. Note that we used "multiprocessing.Pool()" to parallelize the loop.

The resulting repair is a "set()" of assertions. 

### The enhanced $C\pi$-repair
In this version, the function "compute_cpi_repair_enhanced(ontology_path: str, data_path: str, pos_path: str)" from "src/repair/owl_cpi_repair_enhanced.py" starts first by:

- Computing the $\pi$-repair as showed above. 
- Then, it generates the assertions of the deductive closure of the ABox under classical semantics. 
- Assertions of the $\pi$-repair are discarded from the generated assertions.
- The closure of the $\pi$-repair is computed using the function "compute_cl_pi_repair()" from "src/repair/owl_supports.py", it consists of all the assertions that can be inferred from the $\pi$-repair, and thus no need to verify them using the $C\pi$-repair method.
- Now, for the remaining assertions, which are not in the $\pi$-repair or its closure, the supports are computed using "compute_all_supports()" from "src/repair/owl_supports.py". Note that at this level, any assertion that has only one support, cannot be in the $C\pi$-repair. Therefore, assertions with a single support are discarded from the following verification.
- For each remaining assertion "compute_cpi_repair_raw()" is called, as in the naive method, to check if for each conflict, the assertion has at least one support that dominates the conflict.

## Results
The ontology can be found under the folder:
- "ontologies/univ-bench"

The different used datasets can be found under the folders:

- "bench_prepa/dataset_1_university"
- "bench_prepa/dataset_small_u1"
- "bench_prepa/dataset.0.2"

The POSets can be found under the folder: 

- "bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method". 
- Other types of POSets were also explored, like the uniform random DAGs generated using the methods "ic-dag" and "melancon" (in folders: "bench_prepa/DAGs/DAGs_with_bnlearn/ic-dag_method" and "bench_prepa/DAGs/DAGs_with_bnlearn/melancon_method"). These DAGs gave similar results.

For result reproduction, the function in "src/main2.py" features the different calls made for the experiment.

Summary of the results, including charts and plots is found under the folder "bench_prepa/results".

## Future works

The next steps in this project are:
- Test and bench with other benchmarking ontologies (the DL-Lite_R adapted version)
- Extend the experminets for other types of repairs (not only the possibilistic repairs).

## References:

[1] A. Laouar, S. Belabbes, S. Benferhat, Tractable closure-based possibilistic repair for partially ordered dl-lite ontologies, in: European Conference on Logics in Artificial Intelligence, Springer, 2023, pp. 353–368

[2] Benferhat, S., Bouraoui, Z., Tabia, K.: How to select one preferred assertional-based repair from inconsistent and prioritized DL-Lite knowledge bases? In: International Joint Conference on Artificial Intelligence (IJCAI), Buenos Aires, Argentina. pp. 1450–1456 (2015)

[3] Belabbes, S., Benferhat, S.: Computing a possibility theory repair for partially preordered inconsistent ontologies. IEEE Transactions on Fuzzy Systems pp. 1–10 (2021)

[4] A. Chortaras, D. Trivela, G. Stamou, Optimized query rewriting for owl 2 ql, in: Automated Deduction–CADE-23: 23rd International Conference on Automated Deduction, Wrocław, Poland, July 31-August 5, 2011. Proceedings 23, Springer, 2011, pp. 192–206.

[5] C. Lutz, I. Seylan, D. Toman, F. Wolter, The combined approach to OBDA: taming role hierarchies using filters, in: The Semantic Web - ISWC 2013 - 12th International Semantic Web Conference, Sydney, Australia, 2013, pp. 314–330.

[6] M. Scutari, Learning bayesian networks with the bnlearn r package, arXiv preprint arXiv:0908.3817 (2009).

## More

The main focus of this work is a subset of methods for data repairs that operates in the context of possibilistic Knowledge Bases and more generally on partially ordered KBs.  
[__Possiblistic DL-Lite__](https://link.springer.com/chapter/10.1007/978-3-642-40381-1_27) extends the expressive power of DL-Lite to deal with possibilistic uncertain information without increasing the computational cost. 