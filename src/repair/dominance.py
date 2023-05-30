
def check_is_preferred_weight(pos,weight_1,weight_2) -> bool:
    if weight_2 in pos[weight_1]: return True
    else: 
        for successor in pos[weight_1]:
            return check_is_preferred_weight(pos,successor,weight_2)
    return False

def is_strictly_preferred_pos(cursor, pos, w_assertion_1, w_assertion_2) -> bool:
    # a test if assertion_1 is strictly preferred to assertion_2
    vertex_1 = w_assertion_1.get_assertion_weight()
    vertex_2 = w_assertion_2.get_assertion_weight()
    cursor.execute(f"SELECT successor FROM partial_order WHERE assertion_id={vertex_1}")
    result = cursor.fetchone()
    weight_1 = result[0]
    cursor.execute(f"SELECT successor FROM partial_order WHERE assertion_id={vertex_2}")
    result = cursor.fetchone()
    weight_2 = result[0]
    # Check if the assertions have the same weight associated
    if weight_1 == weight_2:
        return False
    return check_is_preferred_weight(pos,weight_1,weight_2)

def check_all_dominance(cursor, pos, conflicts, supports):

    for conflict in conflicts:
        conflict_supported = False
        for support in supports:
            if is_strictly_preferred_pos(cursor, pos, support, conflict[0]) or is_strictly_preferred_pos(cursor, pos, support, conflict[1]):
                conflict_supported = True
                break
        if not conflict_supported:
            return False
    return True
        