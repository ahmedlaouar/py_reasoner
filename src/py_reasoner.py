import argparse
import pathlib
from dl_lite_parser.parser_to_db import process_line
from dl_lite_parser.tbox_parser import read_tbox
from helper import check_in_cpi_repair_helper, conflicts_helper, cpi_repair_helper
#necessary global constants
path = pathlib.Path().resolve()
database_name = "/src/py_reasoner.db"
db_path = str(path)+database_name

if __name__ == '__main__':    
    
    # Main parser
    parser = argparse.ArgumentParser(description='py_reasoner project, implementing the cpi-repair method in DL-Lite_R.')
    # subparsers
    subparsers = parser.add_subparsers(dest='command', help='Functionalities')

    # Subparser to compute cpi-repair
    compute_parser = subparsers.add_parser('compute_cpi_repair', help='Compute cpi-repair')
    compute_parser.add_argument('-t', '--tbox', type=str, required=True, help='Path to TBox file')
    compute_parser.add_argument('-a', '--abox', type=str, required=True, help='Path to ABox file')
    compute_parser.add_argument('-p', '--pos', type=str, required=True, help='Path to ABox Partial Order Set')
    # Subparser to check if a given assertion is in the cpi-repair
    check_in_parser = subparsers.add_parser('check_in_cpi_repair', help='Check in cpi-repair')
    check_in_parser.add_argument('-t', '--tbox', type=str, required=True, help='Path to TBox file')
    check_in_parser.add_argument('-a', '--abox', type=str, required=True, help='Path to ABox file')
    check_in_parser.add_argument('-p', '--pos', type=str, required=True, help='Path to ABox Partial Order Set')
    check_in_parser.add_argument('-e', '--assertion', type=str, required=True, help='Assertion to check')
    # Subparser to check TBox integrity
    check_integrity_parser = subparsers.add_parser('check_integrity', help='Check integrity of TBox')
    check_integrity_parser.add_argument('-t', '--tbox', type=str, required=True, help='Path to TBox file')
    # Subparser compute negative closure of TBox
    negative_closure_parser = subparsers.add_parser('negative_closure', help='Negative closure of TBox')
    negative_closure_parser.add_argument('-t', '--tbox', type=str, required=True, help='Path to TBox file')
    # Subparser compute the conflicts set of the ABox:
    conflicts_set_parser = subparsers.add_parser('conflicts_set', help='Conflicts set of ABox')
    conflicts_set_parser.add_argument('-t', '--tbox', type=str, required=True, help='Path to TBox file')
    conflicts_set_parser.add_argument('-a', '--abox', type=str, required=True, help='Path to ABox file')


    # Parse the command line arguments
    args = parser.parse_args()
    tbox_path = args.tbox
    tbox = read_tbox(str(path)+tbox_path)
    
    if args.command == 'compute_cpi_repair':
        abox_path = str(path)+args.abox
        pos_path = str(path)+args.pos
        tbox_size, abox_size, pos_size, conflicts_size, cpi_repair_size, execution_time = cpi_repair_helper(tbox,abox_path,pos_path,db_path)
        with open(str(path)+'/benchmark_data/results/execution_results.txt', 'a') as file:
            file.write('\n')
            file.write(f"{tbox_size}; {abox_size}; {pos_size}; {conflicts_size}; {cpi_repair_size}; {execution_time}")
        print(tbox_size, abox_size, pos_size, conflicts_size, cpi_repair_size, execution_time)

    elif args.command == 'check_in_cpi_repair':
        abox_path = str(path)+args.abox
        pos_path = str(path)+args.pos
        check_assertion_text = args.assertion
        check_assertion = process_line(check_assertion_text)[0]
        check_in_cpi_repair_helper(tbox,abox_path,pos_path,check_assertion,db_path)

    elif args.command == 'check_integrity':
        tbox.negative_closure()
        if not tbox.check_integrity():
            print("This TBox is not consistent.")
        else:
            print("This TBox is consistent.")

    elif args.command == 'negative_closure':
        tbox.negative_closure()
        print(f"Size of the negative closure = {len(tbox.get_negative_axioms())}")

    elif args.command == 'conflicts_set':
        abox_path = str(path)+args.abox
        conflicts_helper(tbox,abox_path,db_path)
    
    else:
        parser.print_help()


