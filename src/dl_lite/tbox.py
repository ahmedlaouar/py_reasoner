from axiom import Axiom, Side
from typing import List
class TBox:
    # the TBox contains a list of axioms, in order to simplify things, two lists one storing negative axioms and the other storing the positive axioms are created
    def __init__(self, axioms: List[Axiom]) -> None:
        self.__positive_axioms = []
        self.__negative_axioms = []
        for axiom in axioms:
            if axiom.is_negative_axiom():
                self.__negative_axioms.append(axiom)
            else:
                self.__positive_axioms.append(axiom)

    def get_negative_axioms(self):
        return self.__negative_axioms
    
    def get_positive_axioms(self):
        return self.__positive_axioms
    
    def tbox_size(self):
        return len(self.__positive_axioms) + len(self.__negative_axioms)
    
    def negative_closure(self):
        # This function computes the negative closure of the TBox
        # The negative closure starts with the set of all negative axioms, need to check if an axiom is already here before adding it (doing a copy or not depends on multiple criteria here)
        cln = self.__negative_axioms
        # For each negative axiom, we check if there is a positive axiom that extends it 
        for negative_axiom in cln:
            # new negative axioms are appended directly to the browsed list, so the browsing is expected to take more than the length of the initial list, the closure is completed automatically once no negative axiom is added
            # the number of the positive axioms is fixed
            for positive_axiom in self.__positive_axioms:
                # first condition checks if the left side of the negative axiom is the right side of a positive axiom
                # we check for names here, and for roles and concepts equivalently
                # Indeed in both conditions, when names match between positive and negative axioms, modifiers from the negative axiom are used in the negative new axiom and negation is applied when needed
                # Both types of rules are discussed in the documentation, this is a shortcut I made thanks to the implementation that seperates names and modifiers in both sides of an axiom    
                if negative_axiom.get_left_side().get_name() == positive_axiom.get_right_side().get_name():
                    new_side = Side(positive_axiom.get_left_side().get_name(),negative_axiom.get_left_side().get_modifiers().copy())
                    new_axiom = Axiom(new_side,negative_axiom.get_right_side())
                    cln.append(new_axiom)
                elif negative_axiom.get_right_side().get_name() == positive_axiom.get_right_side().get_name():
                    new_side = Side(positive_axiom.get_left_side().get_name(),negative_axiom.get_right_side().negate().get_modifiers())
                    new_axiom = Axiom(new_side,negative_axiom.get_left_side().negate())
                    cln.append(new_axiom)

        #return cln

    def __str__(self) -> str:
        s = "TBox Axioms : \n"
        for axiom in self.__positive_axioms + self.__negative_axioms:
            s += axiom.__str__() + "\n"
        return s