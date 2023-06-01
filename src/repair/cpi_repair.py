from dl_lite.assertion import assertion
from repair.dominance import check_all_dominance, is_strictly_preferred
from repair.conflicts import conflict_set, conflicts_one_axiom
from repair.supports import compute_supports

def check_assertion_in_cpi_repair(cursor, tbox, pos, check_assertion, conflicts=None):
    if conflicts == None:
        tbox.negative_closure()
        conflicts = conflict_set(tbox, cursor)
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    if check_all_dominance(pos, conflicts, supports):
        return True
    else:
        return False

def compute_cpi_repair(cursor, tbox, pos, conflicts, check_list):
    cpi_repair = []
    for check_assertion in check_list:
        supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
        if check_all_dominance(pos, conflicts, supports):
            cpi_repair.append(check_assertion)
    return cpi_repair

#In this version the check list is only formed with the assertions that may be added to the cpi_repair 
def compute_cpi_repair_bis(cursor, tbox, pos, check_list, conflicts=None):
    cpi_repair = []
    
    # First phase is to check additional assertions
    for check_assertion in check_list:
        supports = compute_supports(check_assertion, tbox.get_positive_axioms(), cursor)
        if check_all_dominance(pos, conflicts, supports):
            cpi_repair.append(check_assertion)
    
    # Second phase is to retrieve and verify the assertions from the database (ABox) one by one
    query = "SELECT DISTINCT assertion_name, individual_1, individual_2 FROM assertions"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        if row[2] is None or row[2] == 'None':
            new_assertion = assertion(row[0], row[1])
        else:
            new_assertion = assertion(row[0], row[1], row[2])
        supports = compute_supports(new_assertion, tbox.get_positive_axioms(), cursor)
        if check_all_dominance(pos, conflicts, supports):
            cpi_repair.append(new_assertion)
    
    return cpi_repair


def check_assertion_optimized(cursor, tbox, pos, check_assertion):
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    #tbox.negative_closure()
    #if not tbox.check_integrity():
    #    print("This TBox is not consistent, cannot proceed in this case, abort execution.")
    #    sys.exit()
    for negative_axiom in tbox.get_negative_axioms():
        conflicts = conflicts_one_axiom(negative_axiom, cursor, pos)
        for conflict in conflicts:
            conflict_supported = False # flag to track if a supporting assertion dominates the conflict
            for support in supports:
                if is_strictly_preferred(pos, support, conflict[0]) or is_strictly_preferred(pos, support, conflict[1]):
                    conflict_supported = True # Set the flag to indicate that a dominating support is found
                    break # exit the loop for support, as a dominating support was found
            if not conflict_supported:
                return False # f no dominating support is found, exit the function
    return True