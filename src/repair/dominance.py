# deprecated, old pos representation is replaced with adjacency matrix representation
def check_is_preferred_weight(pos,weight_1,weight_2) -> bool:
    check = False
    if weight_2 in pos[weight_1]: return True
    else: 
        for successor in pos[weight_1]:
            check = check_is_preferred_weight(pos,successor,weight_2)
    return check

# deprecated, old pos representation is replaced with adjacency matrix representation
def is_strictly_preferred_pos(cursor, pos, w_assertion_1, w_assertion_2) -> bool:
    # a test if assertion_1 is strictly preferred to assertion_2
    weight_1 = w_assertion_1.get_assertion_weight()
    weight_2 = w_assertion_2.get_assertion_weight()
    # Check if the assertions have the same weight associated
    if weight_1 == weight_2:
        return False
    return check_is_preferred_weight(pos,weight_1,weight_2)

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
        