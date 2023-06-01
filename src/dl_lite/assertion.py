class assertion:
    def __init__(self, assertion_name, individual_1, individual_2 = None):
        self.__assertion_name = assertion_name
        self.__individual_1 = individual_1
        self.__individual_2 = individual_2
        self.__is_role = (self.__individual_2  is not None)
        
    def get_assertion_name(self):
        return self.__assertion_name
    
    #def get_individuals(self):
    #    if self.__is_role:
    #        return self.__individual_1,self.__individual_2
    #    else:
    #        return self.__individual_1,

    def get_individuals(self):
        if self.__is_role:
            return self.__individual_1,self.__individual_2
        else:
            return self.__individual_1,None

    def is_role(self):
        return self.__is_role
    
    def __str__(self) -> str:
        if self.__is_role:
            return "{}({},{})".format(self.__assertion_name,self.__individual_1,self.__individual_2)
        else:
            return "{}({})".format(self.__assertion_name,self.__individual_1)
        
    def __eq__(self, __value: object) -> bool:
        if self.get_assertion_name() == __value.get_assertion_name() and self.get_individuals() == __value.get_individuals():
            return True

class w_assertion(assertion):
    def __init__(self, assertion_name, individual_1, individual_2 = None, weight=-1):
        if individual_2 is None:
            super().__init__(assertion_name, individual_1)
        else:
            super().__init__(assertion_name, individual_1, individual_2)
        self.__weight = weight

    def get_assertion_weight(self):
        return self.__weight
    
    def __str__(self) -> str:
        if self.is_role():
            return "{}({},{}),{}".format(super().get_assertion_name(),super().get_individuals()[0],super().get_individuals()[1],self.__weight)
        else:
            return "{}({}),{}".format(super().get_assertion_name(),super().get_individuals()[0],self.__weight)