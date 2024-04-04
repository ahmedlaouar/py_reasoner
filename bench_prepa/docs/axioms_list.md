This file contains the list of the disjointness axioms we added to the modify LUBM benchmarking ontology (TBox) to allow for inconsistency in the knowledge base:

"assistant professor" Disjoint With "full professor"

"associate professor" Disjoint With "full professor"

"chair" Disjoint With "visiting professor"

"dean" Disjoint With "visiting professor"

"dean" Disjoint With "ExDean"

"Exam" Disjoint With "ExamRecord"

"ExamRecord" Disjoint With "research work"

"full professor" Disjoint With "visiting professor"

"graduate student" Disjoint With "post doctorate"

"graduate student" Disjoint With "professor"

"organization" Disjoint With "person"

"post doctorate" Disjoint With "professor"

"professor" Disjoint With "student"

"teaching course" Disjoint With "Exam"

"teaching course" Disjoint With "Exam Record"

"has a degree from" Disjoint With "has as an alumnus"

"has as a member" Disjoint With "member of"

"hasFaculty" Disjoint With "isPartOfUniversity"

The 18 added axioms lead to 4561 axioms in the negative closure of the TBox.