from abox import ABox
from assertion import assertion
from axiom import Axiom, Modifier
from tbox import TBox

def same_individuals(axiom: Axiom, assertion_1: assertion, assertion_2: assertion):
    # Check if assertions match with axiom sides 
    if (assertion_1.get_assertion_name() == axiom.get_left_side().get_name() and assertion_2.get_assertion_name() == axiom.get_right_side().get_name()): #or (assertion_2_name == axiom_left_name and assertion_1_name == axiom_right_name) :
        # if both are concepts or both are roles compare individuals
        if assertion_1.is_role() == assertion_2.is_role() and assertion_1.get_individuals() == assertion_2.get_individuals():
            return True
        # if assertion_1 is role and assertion_2 is concept
        if assertion_1.is_role():
            if Modifier.projection in axiom.get_left_side().get_modifiers() and Modifier.inversion in axiom.get_left_side().get_modifiers():
                if assertion_1.get_individuals()[1] == assertion_2.get_individuals():
                    return True
            if Modifier.projection in axiom.get_left_side().get_modifiers:
                if assertion_1.get_individuals()[0] == assertion_2.get_individuals():
                    return True
        # if assertion_1 is concept and assertion_2 is role
        if assertion_2.is_role():
            if Modifier.projection in axiom.get_right_side().get_modifiers() and Modifier.inversion in axiom.get_right_side().get_modifiers():
                if assertion_1.get_individuals() == assertion_2.get_individuals()[1]:
                    return True
            if Modifier.projection in axiom.get_right_side().get_modifiers:
                if assertion_1.get_individuals() == assertion_2.get_individuals()[0]:
                    return True

def conflict_set(tbox: TBox, abox : ABox) -> list():
        conflicts = []
        assertions = abox.get_assertions()
        tbox.negative_closure()
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
        return conflicts