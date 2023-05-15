import time
from dl_lite.assertion import assertion
from dl_lite.repair import check_all_dominance, check_assertion_in_cpi_repair, compute_supports, conflict_set_concurrent_futures, conflict_set_with_threads
from dl_lite_parser.abox_parser import read_abox
from dl_lite_parser.tbox_parser import read_tbox
import pathlib

path = pathlib.Path().resolve()

check_assertion = assertion("Staff", "Bob")

tbox = read_tbox(str(path)+"/src/first_tbox.txt")
print(tbox)

abox = read_abox(str(path)+"/src/first_abox.txt")

assertions_list = abox.get_assertions()

for asser in assertions_list:
    print(asser, abox.get_assertion_id(asser), abox.get_assertion_successors(asser))

preference_relation = abox.get_directed_edges()
for edge1,edge2 in preference_relation:
    print(edge1, " -> ",edge2)

tbox.negative_closure()
print(f"The size of the negative closure = {len(tbox.get_negative_axioms())}")
# Measure execution time
start_time = time.time()
conflicts = conflict_set_concurrent_futures(tbox, abox)
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
supports = compute_supports(check_assertion, tbox.get_positive_axioms(),abox)
if check_all_dominance(abox, conflicts, supports):
    print(f"{check_assertion} is in the Cpi-repair of the abox")
#check_assertion_in_cpi_repair(abox, tbox, check_assertion)