from enum import Enum
from collections import Counter

class Modifier(Enum):
    negation = "NOT"
    inversion = "INV"
    projection = "EXISTS"

class Side:
    def __init__(self, name, modifiers = list()):
        self.__name = name
        self.__modifiers = modifiers

    def get_name(self):
        return self.__name
    
    def get_modifiers(self):
        return self.__modifiers
    
    def is_negative(self):
        return Modifier.negation in self.__modifiers
    
    def negate(self):
        # this function returns a new side instance
        if self.is_negative():
            negated_modifier = self.__modifiers.copy()
            negated_modifier.remove(Modifier.negation)
            return Side(self.__name,negated_modifier)
        else:
            negated_modifier = self.__modifiers.copy()
            negated_modifier.append(Modifier.negation)
            return Side(self.__name,negated_modifier)
        
    def __str__(self) -> str:
        if not self.__modifiers:
            return self.__name
        else:
            return ' '.join([m.value for m in self.__modifiers]) + ' ' + self.__name
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Side):
            return self.__name == __value.get_name() and Counter(self.__modifiers) == Counter(__value.get_modifiers())
        return False
    
class Axiom:
    # In this function, no further verification of the validity of an axiom or side is done, even with the restrictions imposed by the DL-Lite_R syntax, I intend to move all verifications to the entry parsing process
    # The main assumption of this OBDA context is that the TBox is coherent and properly checked for errors by domain experts, thus any verification is done previously.
    def __init__(self, left_side: Side, right_side: Side):
        # an Axiom is formed of left and right sides, each Side is an isnstance of the class Side
        self.__left_side = left_side
        self.__right_side = right_side

    def get_left_side(self):
        return self.__left_side
    
    def get_right_side(self):
        return self.__right_side
    
    def is_negative_axiom(self):
        # a negative Axiom has one of its sides negated
        return self.__right_side.is_negative() or self.__left_side.is_negative()
    
    def negate(self):
        # returns a new negated axiom by negating the negative side if one is negative or negating the right side if none is negative
        if self.is_negative_axiom():
            if self.__left_side.is_negative():
                return Axiom(self.__left_side.negate(),self.__right_side)
            elif self.__right_side.is_negative() :
                return Axiom(self.__left_side,self.__right_side.negate())
        else:
            return Axiom(self.__left_side,self.__right_side.negate())
        
    def inverse_negative_axiom(self):
        # returns a new inversed axiom (left in right, right in left)
        return Axiom(self.__right_side.negate(),self.__left_side.negate())                

    def __str__(self) -> str:
        return "{} < {}".format(self.__left_side.__str__(), self.__right_side.__str__())
    
    def __eq__(self, __value: object) -> bool:
        if (isinstance(__value, Axiom)):
            return self.__left_side == __value.get_left_side() and self.__right_side == __value.get_right_side()
        return False