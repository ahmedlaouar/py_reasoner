from dl_lite.assertion import w_assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox
from repair.dominance import is_strictly_preferred, is_strictly_preferred_pos

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
        #print(f"Axiom number = {counter}")
        counter += 1
        # For each axiom, take left and right side, according to each case generate a query to the database and retreive the result of a select statement
        query = generate_query(axiom)
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            continue
        else:
            for row in rows:
                if row[3] == 'None' or row[3] == None:
                    assertion_1 = w_assertion(row[1],row[2],weight=row[4])
                else:
                    assertion_1 = w_assertion(row[1],row[2],row[3],weight=row[4])
                if row[8] == 'None' or row[8] == None:
                    assertion_2 = w_assertion(row[6],row[7],weight=row[9])
                else:
                    assertion_2 = w_assertion(row[6],row[7],row[8],weight=row[9])
                conflicts.append((assertion_1,assertion_2))        
    return conflicts

def reduced_conflict_set(tbox: TBox, cursor, pos) -> list():
    print("------------ Computation of conflicts set -----------")
    conflicts = []
    negative_axioms = tbox.get_negative_axioms()
    # Browse all negative axioms
    counter = 1
    for axiom in negative_axioms:
        #print(f"Axiom number = {counter}")
        counter += 1
        # For each axiom, take left and right side, according to each case generate a query to the database and retreive the result of a select statement
        query = generate_query(axiom)
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            continue
        else:
            for row in rows:
                if row[3] == 'None' or row[3] == None:
                    assertion_1 = w_assertion(row[1],row[2],weight=row[4])
                else:
                    assertion_1 = w_assertion(row[1],row[2],row[3],weight=row[4])
                if row[8] == 'None' or row[8] == None:
                    assertion_2 = w_assertion(row[6],row[7],weight=row[9])
                else:
                    assertion_2 = w_assertion(row[6],row[7],row[8],weight=row[9])
                dominated = False
                for conf in conflicts:
                    if (is_strictly_preferred(cursor, pos, conf[0], assertion_1) or is_strictly_preferred(cursor, pos, conf[0], assertion_2)) and (is_strictly_preferred(cursor, pos, conf[1], assertion_1) or is_strictly_preferred(cursor, pos, conf[1], assertion_2)):
                        dominated = True
                if not dominated:
                    conflicts.append((assertion_1,assertion_2))        
    return conflicts

# This function computes the conflicts yeld by one negative axiom and ensures a reduced set of conflicts (ignore a conflict if it is dominated by an already present conflict)
def conflicts_one_axiom(negative_axiom, cursor, pos) -> list():
    conflicts = []
    query = generate_query(negative_axiom)
    cursor.execute(query)
    rows = cursor.fetchall()
    if len(rows) != 0:
        for row in rows:
            if row[3] == 'None' or row[3] == None:
                assertion_1 = w_assertion(row[1],row[2],weight=row[4])
            else:
                assertion_1 = w_assertion(row[1],row[2],row[3],weight=row[4])
            if row[8] == 'None' or row[8] == None:
                assertion_2 = w_assertion(row[6],row[7],weight=row[9])
            else:
                assertion_2 = w_assertion(row[6],row[7],row[8],weight=row[9])
            dominated = False
            for conf in conflicts:
                if (is_strictly_preferred_pos(cursor, pos, conf[0], assertion_1) or is_strictly_preferred_pos(cursor, pos, conf[0], assertion_2)) and (is_strictly_preferred_pos(cursor, pos, conf[1], assertion_1) or is_strictly_preferred_pos(cursor, pos, conf[1], assertion_2)):
                    dominated = True
            if not dominated:
                conflicts.append((assertion_1,assertion_2))        
    return conflicts