import pathlib
from dl_lite_parser.tbox_parser import read_tbox

path = pathlib.Path().resolve()

print("---------- Reading the TBox from file ----------")
tbox = read_tbox(str(path)+"/test/cln_tests.txt")
tbox.negative_closure()
print(f"The size of the negative closure = {len(tbox.get_negative_axioms())}")
tbox.check_integrity()
print(tbox)