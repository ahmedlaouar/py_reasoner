from dl_lite.abox import ABox
from dl_lite_parser.abox_parser import process_line

file = """BEGINABOX
Reports(F78);1;2
Manager(Bob);3
Sales(Bob);4
Sign(Bob,F78);
Edit(Bob,F78);
ENDABOX
"""

abox = ABox()
for line in file.splitlines():
    if line.strip() == "BEGINABOX" or line.strip() == "ENDABOX":
            continue
    new_assertion,successors = process_line(line) 
    abox.add_assertion(new_assertion,successors,file.splitlines().index(line))

assertions_list = abox.get_all_graph()
print(assertions_list)
#for ass in assertions_list:
#    print(ass)
print(abox.is_strictly_preferred(abox.get_assertion_by_id(0),abox.get_assertion_by_id(1)))
print(abox.get_assertion_by_id(0))
#preference_relation = abox.get_directed_edges()
#for edge1,edge2 in preference_relation:
#    print(edge1, " -> ",edge2)