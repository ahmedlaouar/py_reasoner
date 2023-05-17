from dl_lite.abox import ABox
from dl_lite.assertion import assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox
import threading

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
                conflicts.append(row)
        counter += 1
    return conflicts