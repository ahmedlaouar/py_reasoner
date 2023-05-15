from dl_lite.abox import ABox
from dl_lite_parser.abox_parser import read_abox
from dl_lite_parser.tbox_parser import read_tbox
import pathlib

path = pathlib.Path().resolve()
#print(path)

tbox = read_tbox(str(path)+"/src/first_tbox.txt")
print(tbox)

abox = read_abox(str(path)+"/src/first_abox.txt")

assertions_list = abox.get_assertions()

for asser in assertions_list:
    print(asser, abox.get_assertion_id(asser), abox.get_assertion_successors(asser))

preference_relation = abox.get_directed_edges()
for edge1,edge2 in preference_relation:
    print(edge1, " -> ",edge2)

#a,b,c,d = Side("A"), Side("B"), Side("C"), Side("D")
#ax1,ax2,ax3,ax4 = Axiom(a,b), Axiom(b,c), Axiom(c,d), Axiom(d,a)
#test_tbox = TBox()
#test_tbox.add_axiom(ax1)
#test_tbox.add_axiom(ax2)
#test_tbox.add_axiom(ax3)
#test_tbox.add_axiom(ax4)
#test_tbox.resolve_circular()