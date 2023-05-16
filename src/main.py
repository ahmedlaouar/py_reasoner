import time
import argparse
from dl_lite.assertion import assertion
from dl_lite.repair import check_all_dominance, check_assertion_in_cpi_repair, compute_supports, conflict_set, conflict_set_with_threads
from dl_lite_parser.abox_parser import read_abox, process_line
from dl_lite_parser.tbox_parser import read_tbox
import pathlib

if __name__ == '__main__':        
    path = pathlib.Path().resolve()
    parser = argparse.ArgumentParser(description='Check if assertion is in cpi-repair.')
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-t', '--tbox', help='Input tbox file name', required=True)
    requiredArgs.add_argument('-a', '--abox', help='Input abox file name', required=True)
    requiredArgs.add_argument('-e', '--assertion', help='Assertion to check', required=True)

    args = parser.parse_args()
    tbox_path = args.tbox
    abox_path = args.abox
    check_assertion_text = args.assertion

    check_assertion = process_line(check_assertion_text)[0]
    tbox = read_tbox(str(path)+tbox_path)
    print(tbox)
    print("-----------------------------------------------------")

    abox = read_abox(str(path)+abox_path)
    print("------------------- ABOX Relations ------------------")
    preference_relation = abox.get_directed_edges()
    for edge1,edge2 in preference_relation:
        print(edge1, " -> ",edge2)
    print("-----------------------------------------------------")

    tbox.negative_closure()
    print(f"Size of the negative closure = {len(tbox.get_negative_axioms())}")

    # Measure execution time
    start_time = time.time()
    conflicts = conflict_set_with_threads(tbox, abox)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    
    print(f"Size of the conflicts = {len(conflicts)}")
    print("-----------------------------------------------------")

    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),abox)
    print(f"Size of the supports = {len(supports)}")

    if check_all_dominance(abox, conflicts, supports):
        print(f"{check_assertion} is in the Cpi-repair of the abox")
    else:
        print(f"{check_assertion} is not in the Cpi-repair of the abox")
