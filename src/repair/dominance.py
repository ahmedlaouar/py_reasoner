# new implementation using pos_mat as an adjacency matrix 
def is_strictly_preferred(pos_mat, w_assertion_1, w_assertion_2) -> bool:
    # a test if assertion_1 is strictly preferred to assertion_2
    weight_1 = w_assertion_1.get_assertion_weight()
    weight_2 = w_assertion_2.get_assertion_weight()
    if pos_mat[weight_1][weight_2] == 1 and pos_mat[weight_2][weight_1] != 1:
        return True

def check_all_dominance(pos, conflicts, supports):
    for conflict in conflicts:
        conflict_supported = False
        for support in supports:
            if is_strictly_preferred(pos, support, conflict[0]) or is_strictly_preferred(pos, support, conflict[1]):
                conflict_supported = True
                break
        if not conflict_supported:
            return False
    return True
        