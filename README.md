# Py_reasoner: a DL-Lite reasoner to compute possibilistic repairs and answer queries.

## Description

Lightweights ontologies are used for efficient query answering and belongs to the Ontology Based Data Access (OBDA) paradigm. 
DL-Lite is one of the most important fragments of Description Logics, here we focus on [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x), which underlies the OWL2-QL language.

The conceptual knowledge of the ontology (i.e., the TBox) is usually assumed to be coherent. However, the dataset (i.e., the ABox) may potentially be inconsistent with respect to the TBox, making the whole ontology inconsistent.
This leads to the necessity of computing data repairs in order to safely evaluate queries.

The main focus of this work is a subset of methods for data repairs that operates in the context of possibilistic Knowledge Bases and more generally on weighted KBs.  
[__Possiblistic DL-Lite__](https://link.springer.com/chapter/10.1007/978-3-642-40381-1_27) extends the expressive power of DL-Lite to deal with possibilistic uncertain information without increasing the computational cost. 
In this context, multiple ABox repairs have been proposed, mainly for totally ordered KBs[1] and partially ordered KBs[2].

### Goals

The aim of this project is to
- Provide the implementation of the partially ordered possibilistic repair called the $\pi$-repair, then extend it to more general cases. 
- Provide a benchmarking study for possibilistic repairs in general and the ones that apply to partial orders in particular. The involved methods are exact repairing semantics that can be computed in polynomial time, but an experimental and algorithmic study is required to show the applicability of such methods (a demonstration of reasonable computation time and space complexity in similar to real life study cases). 
- Another goal is to adapt some famous ontology benchmarking dataset to this context in order to allow for comparative studies. 
- Morover, providing a useful tool to test the tractable methods in the DL-Lite framework is a plus for the OBDA community.

We want to implement the backend **engine** for the available tractable inconsistency-tolerant semantics in order to apply our work to scalable inconsistent KBs.


### Requirements

To run this project, all you need is **python3** interpreter and **git**.

### Install

**Clone** the repository, the main file is named "py_reasonr.py" this README serves also as a tutorial, a list of the main functionnalities is given below alongside the "commnads.txt" file containing a list of useful commands to run the available data examples on your CLI.

### Notation

The used examples of ontologies are saved in 3 different types of files, a file containing the TBox or the ontology, a file containing the ABox or the dataset and a file containing a Partially Ordered Set (POS) to represent the partial preorder over the assertions in the ABox. 

Note that the data is represented in its raw (or native) format in this first version, it is easier to start from here and test the implementation on randomly generated data (some simulation scenarios). After that, we can provide the support for an (xml/owl) parsing to be able to test it against adaptations of the well-known benchmarking datasets.

Consider the following toy scenario of a security policy of a sales company to illustrate the notation and the implementation. this scenario is based on the Concepts $\small\textsf{Manager}$, $\small\textsf{Sales}$, $\small\textsf{Staff}$ which represent employees affiliations, and $\small\textsf{Reports}$ which represents file categories. 

- The TBox file: a raw example of the file containing the TBox:
 ```
BEGINTBOX
Manager < Staff
Sales < Staff
Manager < NOT EXISTS Edit
Sales < NOT EXISTS Sign
ENDTBOX
```

Manager < Staff and Sales < Staff translate the DL-Lite concept inclusion axioms $\small\textsf{Manager} \sqsubseteq \small\textsf{Staff}$ and $\small\textsf{Sales} \sqsubseteq \small\textsf{Staff}$ respectively and indicate that a $\small\textsf{Manager}$ is a $\small\textsf{Staff}$ and a $\small\textsf{Sales}$ is a $\small\textsf{Staff}$.

The negative axioms Manager < NOT EXISTS Edit and Sales < NOT EXISTS Sign indicate disjoint concepts and translate $\small\textsf{Manager} \sqsubseteq \exists \small\textsf{Edit}$ and $\small\textsf{Sales} \sqsubseteq \exists \small\textsf{Sign}$ respectively. This means that for the roles $\small\textsf{Edit}$ and $\small\textsf{Sign}$ respectively, 

 - The ABox file:

 - The POS file:
 

### Current test datasets 


## Main functions


### check_integrity of TBox


### negative_closure of TBox


### conflicts_set of ABox


### compute_cpi_repair


### check_in_cpi_repair


## Future works


## Comments


## References:

[1] Benferhat, S., Bouraoui, Z., Tabia, K.: How to select one preferred assertional-based repair from inconsistent and prioritized DL-Lite knowledge bases? In: International Joint Conference on Artificial Intelligence (IJCAI), Buenos Aires, Argentina. pp. 1450–1456 (2015)

[2] Belabbes, S., Benferhat, S.: Computing a possibility theory repair for partially preordered inconsistent ontologies. IEEE Transactions on Fuzzy Systems pp. 1–10 (2021)
