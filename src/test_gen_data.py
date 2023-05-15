from dl_lite.axiom import Axiom, Side
from dl_lite.tbox import TBox
from dl_lite_parser.abox_parser import read_abox
from dl_lite_parser.tbox_parser import read_tbox
from dl_lite.repair import conflict_set
import pathlib

path = pathlib.Path().resolve()
print("---------- Reading the TBox from file ----------")
tbox = read_tbox(str(path)+"/ontology.txt")
print(f"Size of the TBox = {len(tbox.get_negative_axioms())+len(tbox.get_positive_axioms())}")
print("---------------------------------------------------------")
print("---------- Reading the ABox from file ----------")
abox = read_abox(str(path)+"/dataset.txt")
print(f"Size of the ABox = {abox.get_size()}")

#a,b,c,d = Side("A"), Side("B"), Side("C"), Side("D")
#ax1,ax2,ax3,ax4 = Axiom(a,b), Axiom(b,c), Axiom(c,d), Axiom(d,a)
#test_tbox = TBox()
#test_tbox.add_axiom(ax1)
#test_tbox.add_axiom(ax2)
#test_tbox.add_axiom(ax3)
#test_tbox.add_axiom(ax4)
#test_tbox.resolve_circular()

print("---------------------------------------------------------")
tbox.resolve_circular()

tbox.negative_closure()
print(f"The size of the negative closure = {len(tbox.get_negative_axioms())}")
print("---------------------------------------------------------")
conflicts = conflict_set(tbox,abox)
print(f"The size of the conflicts = {len(conflicts)}")

print("---------------------------------------------------------")
with open(str(path)+"/conflicts_set.txt", 'w') as file:
    for conf in conflicts :
        line = "Axiom: {} | Conflict: ({}, {})\n".format(conf[0],conf[1],conf[2])
        file.write(line)