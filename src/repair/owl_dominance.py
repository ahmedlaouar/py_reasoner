def is_strictly_preferred(pos_dict, member1, member2) -> bool:
    # a test if member1 is strictly preferred to member2 in the pos, member1 and member2 is either a conflict member or a support (assertion) in the form (table1name, id, degree)
    if member2[2] in pos_dict[member1[2]] and member1[2] not in pos_dict[member2[2]] :
        return True
    return False

def dominates(pos_dict, subset1: list, subset2: list) -> bool:
    # returns True if subset1 dominates subset2 (each element of subset1 is_strictly_preferred to at least an element of subset2)
    for member1 in subset1:
        dominates_at_least_one = False        
        for member2 in subset2:
            if is_strictly_preferred(pos_dict, member1, member2):
                dominates_at_least_one = True
                break 
        if not dominates_at_least_one:
            return False
    return True
