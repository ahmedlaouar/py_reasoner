from dl_lite.axiom import Axiom, Modifier, Side
from typing import List
class TBox:
    # the TBox contains a list of axioms, in order to simplify things, two lists one storing negative axioms and the other storing the positive axioms are created
    def __init__(self) -> None:
        self.__positive_axioms = []
        self.__negative_axioms = []

    def add_axiom(self, axiom: Axiom) -> None:
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
        print("---------- Computation of negative closure ----------")
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

                    new_modifiers = negative_axiom.get_left_side().get_modifiers().copy()
                    if Modifier.projection in new_modifiers:
                        new_modifiers.remove(Modifier.projection)
                    if Modifier.inversion in new_modifiers:
                        new_modifiers.remove(Modifier.inversion)

                    new_side = Side(positive_axiom.get_left_side().get_name(),new_modifiers)
                    new_axiom = Axiom(new_side,negative_axiom.get_right_side())
                    # need to find a way to avoid the following verification:
                    if new_axiom not in cln:
                        cln.append(new_axiom)
                        
                elif negative_axiom.get_right_side().get_name() == positive_axiom.get_right_side().get_name():
                    
                    new_modifiers = negative_axiom.get_right_side().negate().get_modifiers().copy()
                    if Modifier.projection in new_modifiers:
                        new_modifiers.remove(Modifier.projection)
                    if Modifier.inversion in new_modifiers:
                        new_modifiers.remove(Modifier.inversion)

                    new_side = Side(positive_axiom.get_left_side().get_name(),new_modifiers)
                    new_axiom = Axiom(new_side,negative_axiom.get_left_side().negate())
                    if new_axiom not in cln:
                        cln.append(new_axiom)
                        
        #return cln

    def __str__(self) -> str:
        s = "-------------------- TBOX Axioms --------------------\n"
        for axiom in self.__positive_axioms + self.__negative_axioms:
            s += axiom.__str__() + "\n"
        return s
    
    def check_circular(self, positive_axioms, current_axiom, visited, current_path, to_remove):
        visited.append(current_axiom)
        current_path.append(current_axiom)

        for next_axiom in positive_axioms:
            if current_axiom.get_right_side().get_name() == next_axiom.get_left_side().get_name():
                if next_axiom in current_path:
                    to_remove.clear()
                    to_remove.append(next_axiom)
                else:
                    self.check_circular(positive_axioms, next_axiom, visited, current_path, to_remove)
        
        current_path.remove(current_axiom)

    def resolve_circular(self):
        to_remove = []
        visited = []
        current_path = []
        for axiom_elem in self.get_positive_axioms():
            if axiom_elem not in visited:
                self.check_circular(self.get_positive_axioms(), axiom_elem, visited, current_path, to_remove)
        
        for re in to_remove : 
            if re in self.__positive_axioms:
                self.__positive_axioms.remove(re)
            print(re)