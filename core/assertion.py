from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

OLD_SOURCE = 'instance_types_lhd_dbo_en'
NEW_SOURCE = 'instance-types_lang=en_specific'

class assertion:
    def __init__(self, assertion_name, individual_0, individual_1 = None, derivationTimestamp = None, wikiTimestamp = None, source = None, weight = -1, id = -1):
        self.__assertion_name = assertion_name
        self.__individual_0 = individual_0
        self.__individual_1 = individual_1
        self.__source = source
        self.__derivationTimestamp = derivationTimestamp
        self.__wikiTimestamp = wikiTimestamp
        self.__is_role = (self.__individual_1  is not None)
        self.__weight = weight
        self.id = id
        
    def get_assertion_name(self):
        return self.__assertion_name
    
    def get_assertion_id(self):
        return self.id

    def get_individuals(self):
        if self.__is_role:
            return self.__individual_0,self.__individual_1
        else:
            return self.__individual_0,None
        
    def get_derivationTimestamp(self):
        return self.__derivationTimestamp
    
    def get_wikiTimestamp(self):
        return self.__wikiTimestamp
    
    def get_source(self):
        return self.__source
    
    def get_weight(self):
        return self.__weight

    def is_role(self):
        return self.__is_role
    
    def __str__(self) -> str:
        if self.__is_role:
            text = "{}({},{})".format(self.__assertion_name,self.__individual_0,self.__individual_1)
        else:
            text = "{}({})".format(self.__assertion_name,self.__individual_0)
        if self.__derivationTimestamp:
            text += ", Derivation timestamp: {}".format(self.__derivationTimestamp)
        if self.__wikiTimestamp:
            text += ", Wikipedia timestamp: {}".format(self.__wikiTimestamp)
        if self.__source:
            text += ", source: {}".format(self.__source)
        if self.__weight != -1:
            text += ", weight: {}".format(self.__weight)
        return text
        
    def __eq__(self, __value: object) -> bool:
        return self.get_assertion_name() == __value.get_assertion_name() and self.get_individuals() == __value.get_individuals()

    def __hash__(self):
        return hash((self.get_assertion_name(),self.get_individuals()[0],self.get_individuals()[1]))
    
    def isStrictlyPreferredTo(self, other) -> bool:
        """Compares timestamps and source of assertions to check strict preference"""
        src1 = self.get_source()
        src2 = other.get_source()
        #fmt = "%Y-%m-%dT%H:%M:%SZ"  # Define the format
        fmt = "%Y-%m-%d %H:%M:%S%z"  # Note space, no 'T', and %z for timezone offset
        dt1 = self.get_derivationTimestamp() if self.get_derivationTimestamp() else None # datetime.strptime(self.get_derivationTimestamp(), fmt) if self.get_derivationTimestamp() else None
        dt2 = other.get_derivationTimestamp() if other.get_derivationTimestamp() else None # datetime.strptime(other.get_derivationTimestamp(), fmt) if other.get_derivationTimestamp() else None
        wt1 = self.get_wikiTimestamp() if self.get_wikiTimestamp() else None # datetime.strptime(self.get_wikiTimestamp(), fmt) if self.get_wikiTimestamp() else None
        wt2 = other.get_wikiTimestamp() if other.get_wikiTimestamp() else None # datetime.strptime(other.get_wikiTimestamp(), fmt) if other.get_wikiTimestamp() else None
        
        # return ((dt1 and dt2 and dt1 > dt2) or (wt1 and wt2 and wt1 > wt2) or (src1 == NEW_SOURCE and src2 == OLD_SOURCE))

        return ((dt1 and dt2 and dt1 > dt2) or (wt1 and wt2 and wt1 > wt2) or (src1 == NEW_SOURCE and src2 == OLD_SOURCE)) and not((src2 == NEW_SOURCE and src1 == OLD_SOURCE) or (dt1 and dt2 and dt2 > dt1) or (wt1 and wt2 and wt2 > wt1))

class SupportedAssertion:
    def __init__(self, assertion_name, individual_0, individual_1=None):
        self.assertion_name = assertion_name
        self.individual_0 = individual_0
        self.individual_1 = individual_1
        self.supports = []  # List of assertion instances

    def add_support(self, support_assertion: assertion):
        self.supports.append(support_assertion)

    def is_role(self):
        return (self.individual_1 is not None)
    
    def get_assertion_name(self):
        return self.assertion_name

    def get_individuals(self):
        if self.is_role():
            return self.individual_0,self.individual_1
        else:
            return self.individual_0,None
        
    def get_all_sources(self):
        return [s.get_source() for s in self.supports]

    def get_all_derivationTimestamps(self):
        return [s.get_derivationTimestamp() for s in self.supports]
    
    def get_all_wikiTimestamps(self):
        return [s.get_wikiTimestamp() for s in self.supports]

    def get_all_weights(self):
        return [s.get_weight() for s in self.supports]
    
    def isStrictlyPreferredTo(self, other_assertion) -> bool:
        """Returns True if any support is strictly preferred to the given assertion"""
        return any(support.isStrictlyPreferredTo(other_assertion) for support in self.supports)
    
    def __eq__(self, __value: object) -> bool:
        return self.get_assertion_name() == __value.get_assertion_name() and self.get_individuals() == __value.get_individuals()

    def __hash__(self):
        return hash((self.get_assertion_name(),self.get_individuals()[0],self.get_individuals()[1]))
    
    def __str__(self) -> str:
        if self.is_role():
            text = "{}({},{})".format(self.assertion_name,self.individual_0,self.individual_1)
        else:
            text = "{}({})".format(self.assertion_name,self.individual_0)
        return text