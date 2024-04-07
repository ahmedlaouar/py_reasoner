import argparse
from helper import check_in_cpi_repair_helper, conflicts_helper, read_assertion
from repair.owl_cpi_repair import compute_cpi_repair
from repair.owl_cpi_repair_enhanced import compute_cpi_repair_enhanced
from repair.owl_pi_repair import compute_pi_repair
from repair.utils import add_pos_to_db

if __name__ == '__main__':    
    
    # Main parser
    parser = argparse.ArgumentParser(description='py_reasoner project, implementing the pi-repair and the cpi-repair methods in DL-Lite_R.')
    # subparsers
    subparsers = parser.add_subparsers(dest='command', help='Functionalities')

    # Subparser to compute pi-repair
    pi_parser = subparsers.add_parser('compute_pi_repair', help='Compute pi-repair')
    pi_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    pi_parser.add_argument('--abox', type=str, required=True, help='Path to ABox file')
    pi_parser.add_argument('--pos', type=str, required=True, help='Path to the POset')

    # Subparser to compute cpi-repair
    cpi_parser = subparsers.add_parser('compute_cpi_repair', help='Compute cpi-repair')
    cpi_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    cpi_parser.add_argument('--abox', type=str, required=True, help='Path to ABox file')
    cpi_parser.add_argument('--pos', type=str, required=True, help='Path to ABox Partial Order Set')
    
    # Subparser to compute cpi-repair using the improved method
    cpi_improved_parser = subparsers.add_parser('compute_cpi_repair_improved', help='Compute cpi-repair')
    cpi_improved_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    cpi_improved_parser.add_argument('--abox', type=str, required=True, help='Path to ABox file')
    cpi_improved_parser.add_argument('--pos', type=str, required=True, help='Path to ABox Partial Order Set')

    # Subparser to check if a given assertion is in the cpi-repair
    check_in_parser = subparsers.add_parser('check_in_cpi_repair', help='Check in cpi-repair')
    check_in_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    check_in_parser.add_argument('--abox', type=str, required=True, help='Path to ABox file')
    check_in_parser.add_argument('--pos', type=str, required=True, help='Path to ABox Partial Order Set')
    check_in_parser.add_argument('--assertion', type=str, required=True, help='Assertion to check')
    
    # Subparser to check TBox integrity
    #check_integrity_parser = subparsers.add_parser('check_integrity', help='Check integrity of TBox')
    #check_integrity_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    
    # Subparser compute the conflicts set of the ABox:
    conflicts_set_parser = subparsers.add_parser('compute_conflicts', help='Conflicts set of ABox')
    conflicts_set_parser.add_argument('--tbox', type=str, required=True, help='Path to TBox file')
    conflicts_set_parser.add_argument('--abox', type=str, required=True, help='Path to ABox file')


    # Parse the command line arguments
    try:
        args = parser.parse_args()
    
        tbox_path = args.tbox
        abox_path = args.abox
        
        if args.command == 'compute_conflicts':
            conflicts_helper(tbox_path,abox_path)
        
        elif args.command == 'compute_pi_repair':
            pos_path = args.pos
            add_pos_to_db(abox_path, pos_path)
            pi_repair_results = compute_pi_repair(tbox_path,abox_path,pos_path)
        
        
        elif args.command == 'compute_cpi_repair':
            pos_path = args.pos
            add_pos_to_db(abox_path, pos_path)
            cpi_repair_results = compute_cpi_repair(tbox_path,abox_path,pos_path)
            
        
        elif args.command == 'compute_cpi_repair_improved':
            pos_path = args.pos
            add_pos_to_db(abox_path, pos_path)
            cpi_repair_results = compute_cpi_repair_enhanced(tbox_path,abox_path,pos_path)

        elif args.command == 'check_in_cpi_repair':
            pos_path = args.pos
            add_pos_to_db(abox_path, pos_path)
            check_assertion_text = args.assertion
            check_assertion = read_assertion(check_assertion_text)
            check_in_cpi_repair_helper(tbox_path,abox_path,pos_path,check_assertion)
    
    except AttributeError as e:
        parser.print_help()


