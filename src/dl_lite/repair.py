from abox import ABox
from assertion import assertion
from axiom import Axiom
from tbox import TBox

def same_individuals(axiom: Axiom, assertion_1: assertion, assertion_2: assertion):
    if assertion_1.is_role() == assertion_2.is_role() and assertion_1.get_individuals() == assertion_2.get_individuals():
        return True

def conflict_set(tbox: TBox, abox : ABox) -> list():
        conflicts = []
        assertions = abox.get_assertions()
        tbox.negative_closure()
        negative_axioms = tbox.get_negative_axioms()
        # Browse all negative axioms
        for axiom in negative_axioms:
            # Browse all assertions
            axiom_left_name = axiom.get_left_side().get_name()
            axiom_right_name = axiom.get_right_side().get_name()
            for assertion_1 in assertions:
                # Browse all assertions after the current assertion (to avoid duplicate verifications)
                for assertion_2 in assertions[assertions.index(assertion_1):] :
                    assertion_1_name = assertion_1.get_assertion_name()
                    assertion_2_name = assertion_2.get_assertion_name()        
                    # Check if (assertion_1 name in assertion_2 name) or (assertion_2 name in assertion_1 name)
                    if ( assertion_1_name == axiom_left_name and assertion_2_name == axiom_right_name) or \
                          (assertion_2_name == axiom_left_name and assertion_1_name == axiom_right_name) :
                        # replace the following call for a function in assertion to compare the individuals 
                        # if both are concepts or both are roles compare individuals
                        if same_individuals(axiom, assertion_1, assertion_2):
                            conflicts.append((axiom, assertion_1, assertion_2))
        return conflicts