from dl_lite.axiom import Axiom, Modifier, Side
from dl_lite.assertion import assertion
from dl_lite.abox import ABox
from dl_lite.tbox import TBox
from dl_lite.repair import check_assertion_in_cpi_repair
# Individuals
f78 = "F78"
bob = "Bob"
# Concepts
reports = "Reports"
manager = "Manager"
sales = "Sales"
staff = "Staff"
# Roles
sign = "Sign"
edit = "Edit"
# Tbox axioms
side1 = Side(manager)
side2 = Side(edit, [Modifier.negation, Modifier.projection])
side3= Side(sales)
side4 = Side(sign, [Modifier.negation, Modifier.projection])
side5 = Side(staff)
axiom1 = Axiom(side1,side2)
axiom2 = Axiom(side3,side4)
axiom3 = Axiom(side1,side5)
axiom4= Axiom(side3,side5)
# TBox
axioms = [axiom1,axiom2,axiom3,axiom4]
tbox = TBox()
for axiom in axioms:
    tbox.add_axiom(axiom)
print(tbox)
# Assertions
assertion1 = assertion(reports,f78)
assertion2 = assertion(manager,bob)
assertion3 = assertion(sales,bob)
assertion4 = assertion(sign,bob,f78)
assertion5 = assertion(edit,bob,f78)
# Abox
abox = ABox()
abox.add_assertion(assertion1)
abox.add_assertion(assertion2)
abox.add_assertion(assertion3)
abox.add_assertion(assertion4)
abox.add_assertion(assertion5)

# Partial order
abox.add_directed_edge(assertion1,assertion2)
#print(abox.get_all_graph())
abox.add_directed_edge(assertion1,assertion3)
abox.add_directed_edge(assertion2,assertion4)
abox.add_directed_edge(assertion3,assertion5)

assertions_list = abox.get_assertions()
for ass in assertions_list:
    print(ass)
preference_relation = abox.get_directed_edges()
for edge1,edge2 in preference_relation:
    print(edge1, " -> ",edge2)

assertion6 = assertion(staff,bob)
print(f"Checking if {assertion6} is in Cpirepair de abox:")
check_assertion_in_cpi_repair(abox,tbox,assertion6)

# Compute conflicts set 
#tbox.negative_closure()

#conflict_set = conflict_set(tbox,abox)
#for conf in conflict_set :
#    print("Axiom : ", conf[0], " | Conflict : (", conf[1], ", ", conf[2],")")

#supports = compute_supports(assertion6, tbox.get_positive_axioms(),abox)
#print(f"The supports of {assertion6} are:")
#for support in supports:
#    print(support)

# Checking if Staff(Bob) is in Cpirepair de abox:
#if check_all_dominance(abox, conflict_set, supports):
#    print(f"{assertion6} is in the Cpi-repair of the abox")