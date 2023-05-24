from dl_lite.assertion import assertion, w_assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox

def generate_query(axiom: Axiom):
    left_side = axiom.get_left_side()
    right_side = axiom.get_right_side().negate()
    if Modifier.inversion in left_side.get_modifiers() and Modifier.projection in left_side.get_modifiers() and Modifier.inversion in right_side.get_modifiers() and Modifier.projection in right_side.get_modifiers():
        query = f'''SELECT * FROM assertions t1 INNER JOIN assertions t2 ON t1.individual_2 = t2.individual_2
        WHERE t1.assertion_name = '{left_side.get_name()}' AND t2.assertion_name = '{right_side.get_name()}';'''
    elif Modifier.inversion in left_side.get_modifiers() and Modifier.projection in left_side.get_modifiers():
        query = f'''SELECT * FROM assertions t1 INNER JOIN assertions t2 ON t1.individual_2 = t2.individual_1
        WHERE t1.assertion_name = '{left_side.get_name()}' AND t2.assertion_name = '{right_side.get_name()}';'''
    elif Modifier.inversion in right_side.get_modifiers() and Modifier.projection in right_side.get_modifiers():
        query = f'''SELECT * FROM assertions t1 INNER JOIN assertions t2 ON t1.individual_1 = t2.individual_2
        WHERE t1.assertion_name = '{left_side.get_name()}' AND t2.assertion_name = '{right_side.get_name()}';'''
    elif Modifier.projection in left_side.get_modifiers() or Modifier.projection in right_side.get_modifiers():
        query = f'''SELECT * FROM assertions t1 INNER JOIN assertions t2 ON t1.individual_1 = t2.individual_1
        WHERE t1.assertion_name = '{left_side.get_name()}' AND t2.assertion_name = '{right_side.get_name()}';'''
    else:
        query = f'''SELECT * FROM assertions t1 INNER JOIN assertions t2 ON t1.individual_1 = t2.individual_1 and t1.individual_2 = t2.individual_2
        WHERE t1.assertion_name = '{left_side.get_name()}' AND t2.assertion_name = '{right_side.get_name()}';'''

    return query

# here to define a conflict set function that query an sql database
def conflict_set(tbox: TBox, cursor) -> list():
    print("------------ Computation of conflicts set -----------")
    conflicts = []
    #tbox.negative_closure()
    negative_axioms = tbox.get_negative_axioms()
    # Browse all negative axioms
    counter = 1
    for axiom in negative_axioms:
        print(f"Axiom number = {counter}")
        # For each axiom, take left and right side, according to each case generate a query to the database and retreive the result of a select statement
        query = generate_query(axiom)
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            continue
        else:
            for row in rows:
                if row[3] == 'None' or row[3] == None:
                    assertion_1 = w_assertion(row[1],row[2],weight=row[0])
                else:
                    assertion_1 = w_assertion(row[1],row[2],row[3],weight=row[0])
                if row[7] == 'None' or row[7] == None:
                    assertion_2 = w_assertion(row[5],row[6],weight=row[4])
                else:
                    assertion_2 = w_assertion(row[5],row[6],row[7],weight=row[4])
                conflicts.append((assertion_1,assertion_2))
        counter += 1
    return conflicts

def supports_deduction(find_assertion: assertion, positive_axioms: list(), cursor):
    supports = []
    for axiom in positive_axioms:
        query = ""
        if Modifier.projection in axiom.get_right_side().get_modifiers():
            continue
        if axiom.get_right_side().get_name() == find_assertion.get_assertion_name() :
            if find_assertion.is_role():
                query = f"""SELECT * FROM assertions WHERE assertion_name = '{axiom.get_left_side().get_name()}' 
                AND individual_1 = '{find_assertion.get_individuals()[0]}' and individual_2 = '{find_assertion.get_individuals()[1]}'"""                
            else:
                if Modifier.inversion in axiom.get_left_side().get_modifiers():
                    query = f"""SELECT * FROM assertions WHERE assertion_name = '{axiom.get_left_side().get_name()}' 
                    AND individual_2 = '{find_assertion.get_individuals()[0]}'"""
                else:
                    query = f"""SELECT * FROM assertions WHERE assertion_name = '{axiom.get_left_side().get_name()}'
                    AND individual_1 = '{find_assertion.get_individuals()[0]}'"""
            if query != "":
                cursor.execute(query)
                rows = cursor.fetchall()
                if len(rows) != 0:
                    for row in rows:
                        if row[3] == 'None' or row[3] == None:
                            new_assertion = w_assertion(row[1],row[2],weight=row[0])
                        else:
                            new_assertion = w_assertion(row[1],row[2],row[3],weight=row[0])
                        supports.append(new_assertion)
            next_assertion = assertion(axiom.get_left_side().get_name(),find_assertion.get_individuals2()[0],find_assertion.get_individuals2()[1])
            supports += supports_deduction(next_assertion, positive_axioms, cursor)
    return supports

def compute_supports(target_assertion: assertion, positive_axioms: list(), cursor):
    supports = supports_deduction(target_assertion, positive_axioms, cursor)
    query = f"""SELECT * FROM assertions WHERE assertion_name = '{target_assertion.get_assertion_name()}' AND 
    individual_1 = '{target_assertion.get_individuals2()[0]}' and individual_2 = '{target_assertion.get_individuals2()[1]}'"""
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        if row[3] == 'None' or row[3] == None:
            new_assertion = w_assertion(row[1],row[2],weight=row[0])
        else:
            new_assertion = w_assertion(row[1],row[2],row[3],weight=row[0])
        supports.append(new_assertion)
    return supports

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

# Deprecated, to be removed
def is_strictly_preferred(cursor, w_assertion_1, w_assertion_2, first_call=True) -> bool:
    # a test if assertion_1 is strictly preferred to assertion_2    
    vertex_1 = w_assertion_1.get_assertion_weight()
    vertex_2 = w_assertion_2.get_assertion_weight()
    cursor.execute(f"SELECT successor FROM partial_order WHERE assertion_id={vertex_1}")
    result = cursor.fetchall()
    successors_1 = []
    if len(result) != 0:
        for row in result:
            if len(row) != 0 : successors_1.append(row[0])  # Extract the first element of each tuple

    successors_2 = []
    cursor.execute(f"SELECT successor FROM partial_order WHERE assertion_id={vertex_2}")
    result = cursor.fetchall()
    if len(result) != 0:
        for row in result:
            if len(row) != 0 : successors_2.append(row[0])  # Extract the first element of each tuple

    # in the first call, we don't want the two assertions to be equivalent (both in each one successors)
    if first_call and (vertex_2 in successors_1) and (vertex_1 not in successors_2):
        return True
    
    # in the rest of the subsequent recursive calls if the assertion is equivalent to one of our assertions successors (or their successors) it is retianed
    if not first_call and (vertex_2 in successors_1):
        return True
    # for all assertion successors and their successors we need to check if assertion_2 is their, the partial order is a transitive relation  
    
    if len(successors_1) != 0: # Check if assertion_1 has successors
        for vertex in successors_1:
            
            cursor.execute(f"SELECT * FROM assertions WHERE id={vertex}")
            row = cursor.fetchone()
            if row is not None:
                if row[3] == 'None' or row[3] == None:
                    new_assertion = w_assertion(row[1],row[2],weight=row[0])
                else:
                    new_assertion = w_assertion(row[1],row[2],row[3],weight=row[0])
                if is_strictly_preferred(cursor, new_assertion, w_assertion_2, False):
                    return True

    return False

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

def check_assertion_in_cpi_repair(cursor, tbox, pos, check_assertion):
    tbox.negative_closure()
    conflicts = conflict_set(tbox, cursor)
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),cursor)
    if check_all_dominance(cursor, pos, conflicts, supports):
        print(f"{check_assertion} is in the Cpi-repair of the abox")
    else:
        print(f"{check_assertion} is not in the Cpi-repair of the abox")

# need to work more on this
def generate_possible_assertions(cursor, positive_axioms):
    list_to_check = []

    for axiom in positive_axioms:
        if Modifier.projection in axiom.get_right_side().get_modifiers():
            continue
        query = f"SELECT individual_1,individual_2 FROM assertions WHERE assertion_name = '{axiom.get_left_side().get_name()}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) != 0:
            assertion_name = axiom.get_right_side().get_name()
            for row in rows:
                if row[1] == None or row[1] == 'None':
                    ind_name = row[0]                    
                    new_assertion = assertion(assertion_name,ind_name)
                elif Modifier.projection in axiom.get_left_side().get_modifiers() and Modifier.inversion in axiom.get_left_side().get_modifiers():
                    ind_name = row[1]                    
                    new_assertion = assertion(assertion_name,ind_name)
                elif Modifier.projection in axiom.get_left_side().get_modifiers():
                    ind_name = row[0]                    
                    new_assertion = assertion(assertion_name,ind_name)
                else:
                    new_assertion = assertion(assertion_name,row[0],row[1])
                if new_assertion not in list_to_check:
                    list_to_check.append(new_assertion)
    return list_to_check

def get_all_assertions(cursor):
    assertions_list = []
    query = f"SELECT DISTINCT assertion_name,individual_1,individual_2 FROM assertions"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        if row[2] == None or row[2] == 'None':
            new_assertion = assertion(row[0],row[1])
            assertions_list.append(new_assertion)
        else:
            new_assertion = assertion(row[0],row[1],row[2])
            assertions_list.append(new_assertion)
    return assertions_list

def generate_assertions_naive(cursor, positive_axioms):
    generated_list = []
    individual_1_list = []
    individual_2_list = []
    assertion_names = list(set([axiom.get_right_side().get_name() for axiom in positive_axioms]))
    query_1 = f"SELECT DISTINCT individual_1 FROM assertions"
    query_2 = f"SELECT DISTINCT individual_2 FROM assertions"
    cursor.execute(query_1)
    rows = cursor.fetchall()
    for row in rows:
        individual_1_list.append(row[0])
    cursor.execute(query_2)
    rows = cursor.fetchall()
    for row in rows:
        individual_2_list.append(row[0])
    #for name in assertion_names:

