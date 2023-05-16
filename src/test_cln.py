import pathlib
from dl_lite_parser.tbox_parser import read_tbox

path = pathlib.Path().resolve()

print("---------- Reading the TBox from file ----------")
tbox = read_tbox(str(path)+"/test/cln_tests.txt")
tbox.negative_closure()
print(f"The size of the negative closure = {len(tbox.get_negative_axioms())}")
tbox.check_integrity()
print(tbox)
"""
tbox2 = read_tbox(str(path)+"/examples/ontology.txt")
tbox2.negative_closure()
print(f"The size of the negative closure = {len(tbox2.get_negative_axioms())}")
tbox2.check_integrity()

with open(str(path)+"/examples/negative_closure_ontology.txt", 'w') as file:
    for axiom in tbox2.get_positive_axioms():
        line = "{}\n".format(axiom)
        file.write(line)
    for axiom in tbox2.get_negative_axioms():
        line = "{}\n".format(axiom)
        file.write(line)
        """