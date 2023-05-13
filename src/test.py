from dl_lite.abox import ABox
from dl_lite_parser.abox_parser import process_line, read_abox

import pathlib
path = pathlib.Path().resolve()
print(path)

abox = read_abox(str(path)+"/src/first_abox.txt")

assertions_list = abox.get_assertions()

for ass in assertions_list:
    print(ass, abox.get_assertion_id(ass), abox.get_assertion_successors(ass))

preference_relation = abox.get_directed_edges()
for edge1,edge2 in preference_relation:
    print(edge1, " -> ",edge2)