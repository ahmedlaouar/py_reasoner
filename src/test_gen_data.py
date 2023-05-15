from dl_lite_parser.abox_parser import read_abox
from dl_lite_parser.tbox_parser import read_tbox
from dl_lite.repair import conflict_set
import pathlib

path = pathlib.Path().resolve()
print("---------- Reading the TBox from file ----------")
tbox = read_tbox(str(path)+"/ontology.txt")
print(f"Size of the TBox = {len(tbox.get_negative_axioms())+len(tbox.get_positive_axioms())}")

print("---------- Reading the ABox from file ----------")
abox = read_abox(str(path)+"/dataset.txt")
print(f"Size of the ABox = {abox.get_size()}")

tbox.negative_closure()
print(f"The size of the negative closure = {len(tbox.get_negative_axioms())}")

#conflicts = conflict_set(tbox,abox)
#print(f"The size of the conflicts = {len(conflicts)}")
#for conf in conflicts :
#    print("Axiom : ", conf[0], " | Conflict : (", conf[1], ", ", conf[2],")")
