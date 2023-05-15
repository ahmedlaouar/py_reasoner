from dl_lite.abox import ABox
from dl_lite.assertion import assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox

def same_individuals(axiom: Axiom, assertion_1: assertion, assertion_2: assertion):
    
    # Check if assertions match with axiom sides 
    if (assertion_1.get_assertion_name() == axiom.get_left_side().get_name() and assertion_2.get_assertion_name() == axiom.get_right_side().get_name()):
        
        # Check if both assertions are concepts or both are roles and compare individuals
        if assertion_1.is_role() == assertion_2.is_role() and assertion_1.get_individuals() == assertion_2.get_individuals():
            return True
        
        # Check if assertion_1 is role and assertion_2 is concept
        if assertion_1.is_role():
            if Modifier.projection in axiom.get_left_side().get_modifiers():
                
                if Modifier.inversion in axiom.get_left_side().get_modifiers() and \
                        assertion_1.get_individuals()[1] == assertion_2.get_individuals()[0]:
                    return True
                if Modifier.inversion not in axiom.get_left_side().get_modifiers() and assertion_1.get_individuals()[0] == assertion_2.get_individuals()[0]:
                    return True
                
        # Check if assertion_1 is concept and assertion_2 is role
        if assertion_2.is_role():
            if Modifier.projection in axiom.get_right_side().get_modifiers():
                
                if Modifier.inversion in axiom.get_right_side().get_modifiers() and \
                        assertion_1.get_individuals()[0] == assertion_2.get_individuals()[1]:
                    return True
                if Modifier.inversion not in axiom.get_right_side().get_modifiers() and assertion_1.get_individuals()[0] == assertion_2.get_individuals()[0]:
                    return True

def conflict_set(tbox: TBox, abox : ABox) -> list():
        print("---------- Start of conflict set computation ----------")
        conflicts = []
        assertions = abox.get_assertions()
        #tbox.negative_closure()
        negative_axioms = tbox.get_negative_axioms()
        # Browse all negative axioms
        for axiom in negative_axioms:
            # Browse all assertions
            for assertion_1 in assertions:
                # Browse all assertions after the current assertion (to avoid duplicate verifications)
                for assertion_2 in assertions[assertions.index(assertion_1):] :
                    # replace the following call for a function in assertion to compare the individuals 
                    if same_individuals(axiom, assertion_1, assertion_2) or same_individuals(axiom, assertion_2, assertion_1):
                        conflicts.append((axiom, assertion_1, assertion_2))
        print("---------- End of conflict set computation ----------")
        return conflicts


def supports_deduction(find_assertion: assertion, positive_axioms: list(), abox: ABox):
    supports = []
    for axiom in positive_axioms:
        if axiom.get_right_side().get_name() == find_assertion.get_assertion_name() :
            if find_assertion.is_role():
                new = assertion(axiom.get_left_side().get_name(), find_assertion.get_individuals()[0], find_assertion.get_individuals()[1])
            else:
                new = assertion(axiom.get_left_side().get_name(), find_assertion.get_individuals()[0])
            for abox_assertion in abox.get_assertions():
                if new.get_assertion_name() == abox_assertion.get_assertion_name() and new.get_individuals() == abox_assertion.get_individuals() :
                    supports.append(abox_assertion)
            supports += supports_deduction(new, positive_axioms, abox)
    return supports

def compute_supports(target_assertion: assertion, positive_axioms: list(), abox: ABox):
    supports = supports_deduction(target_assertion, positive_axioms, abox)
    if target_assertion in abox.get_assertions():
        supports.append(target_assertion)
    return supports

def check_all_dominance(abox, conflicts, supports):
    for conflict in conflicts:
        conflict_supported = False
        for support in supports:
            if abox.is_strictly_preferred(support, conflict[1]) or abox.is_strictly_preferred(support, conflict[2]):
                conflict_supported = True
                break
        if not conflict_supported:
            return False
    return True

def check_assertion_in_cpi_repair(abox, tbox, check_assertion):
    tbox.negative_closure()
    conflicts = conflict_set(tbox,abox)
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),abox)
    if check_all_dominance(abox, conflicts, supports):
        print(f"{check_assertion} is in the Cpi-repair of the abox")