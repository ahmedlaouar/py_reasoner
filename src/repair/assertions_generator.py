from dl_lite.assertion import assertion
from dl_lite.axiom import Modifier

def generate_recursive(cursor, positive_axioms, name, current_name):
    list_to_check = []

    for axiom in positive_axioms:
        if axiom.get_right_side().get_name() == current_name:
            new_name = axiom.get_left_side().get_name()
            if name == new_name:
                continue
            query = f"SELECT individual_1, individual_2 FROM assertions WHERE assertion_name = '{new_name}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if len(rows) != 0:
                for row in rows:
                    if row[1] == None or row[1] == 'None':
                        ind_name = row[0]
                        new_assertion = assertion(name, ind_name)
                    elif Modifier.projection in axiom.get_left_side().get_modifiers() and Modifier.inversion in axiom.get_left_side().get_modifiers():
                        ind_name = row[1]
                        new_assertion = assertion(name, ind_name)
                    elif Modifier.projection in axiom.get_left_side().get_modifiers():
                        ind_name = row[0]
                        new_assertion = assertion(name, ind_name)
                    else:
                        new_assertion = assertion(name, row[0], row[1])
                    
                    if new_assertion not in list_to_check:
                        list_to_check.append(new_assertion)
                    
            recursive_results = generate_recursive(cursor, positive_axioms, name, new_name)
            for item in recursive_results:
                if item not in list_to_check:
                    list_to_check.append(item)

    return list_to_check

def generate_possible_assertions_rec(cursor, positive_axioms):
    list_to_check = []
    for axiom in positive_axioms:
        if Modifier.projection in axiom.get_right_side().get_modifiers():
            continue
        name = axiom.get_right_side().get_name()
        recursive_results =  generate_recursive(cursor, positive_axioms, name, name)
        for item in recursive_results:
                if item not in list_to_check:
                    list_to_check.append(item)
    
    return list_to_check

def get_all_assertions(cursor):
    assertions_list = []
    query = f"SELECT DISTINCT assertion_name,individual_1,individual_2 FROM assertions"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        if row[2] == None or row[2] == 'None':
            new_assertion = assertion(row[0],row[1])
        else:
            new_assertion = assertion(row[0],row[1],row[2])
        assertions_list.append(new_assertion)
    return assertions_list
