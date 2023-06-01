from dl_lite.axiom import Modifier
from dl_lite.assertion import assertion, w_assertion
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
                            new_assertion = w_assertion(row[1],row[2],weight=row[4])
                        else:
                            new_assertion = w_assertion(row[1],row[2],row[3],weight=row[4])
                        supports.append(new_assertion)
            next_assertion = assertion(axiom.get_left_side().get_name(),find_assertion.get_individuals()[0],find_assertion.get_individuals()[1])
            supports += supports_deduction(next_assertion, positive_axioms, cursor)
    return supports

def compute_supports(target_assertion: assertion, positive_axioms: list(), cursor):
    supports = supports_deduction(target_assertion, positive_axioms, cursor)
    query = f"""SELECT * FROM assertions WHERE assertion_name = '{target_assertion.get_assertion_name()}' AND 
    individual_1 = '{target_assertion.get_individuals()[0]}' and individual_2 = '{target_assertion.get_individuals()[1]}'"""
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        if row[3] == 'None' or row[3] == None:
            new_assertion = w_assertion(row[1],row[2],weight=row[4])
        else:
            new_assertion = w_assertion(row[1],row[2],row[3],weight=row[4])
        supports.append(new_assertion)
    return supports