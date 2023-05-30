
from repair.dominance import check_all_dominance
from repair.conflicts import conflict_set
from repair.supports import compute_supports

def check_assertion_in_cpi_repair(cursor, tbox, pos, check_assertion, conflicts=None):
    if conflicts == None:
        tbox.negative_closure()
        conflicts = conflict_set(tbox, cursor)
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    if check_all_dominance(cursor, pos, conflicts, supports):
        return True
    else:
        return False


def compute_cpi_repair(cursor, tbox, pos, conflicts, check_list):
    cpi_repair = []
    for check_assertion in check_list:
        supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
        if check_all_dominance(cursor, pos, conflicts, supports):
            cpi_repair.append(check_assertion)
    return cpi_repair
