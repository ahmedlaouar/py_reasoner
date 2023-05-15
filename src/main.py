from dl_lite.repair import check_assertion_in_cpi_repair
from dl_lite_parser.abox_parser import read_abox
from dl_lite_parser.tbox_parser import read_tbox
import pathlib

path = pathlib.Path().resolve()

check_assertion = "Staff(Bob)"

tbox = read_tbox(str(path)+"/src/first_tbox.txt")
print(tbox)

abox = read_abox(str(path)+"/src/first_abox.txt")

assertions_list = abox.get_assertions()

for asser in assertions_list:
    print(asser, abox.get_assertion_id(asser), abox.get_assertion_successors(asser))

preference_relation = abox.get_directed_edges()
for edge1,edge2 in preference_relation:
    print(edge1, " -> ",edge2)

check_assertion_in_cpi_repair(abox, tbox, check_assertion)