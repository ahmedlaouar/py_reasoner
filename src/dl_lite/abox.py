from assertion import assertion
from tbox import TBox

class ABox:
    # This implementation of the ABox considers a partially ordered ABox
    # I made the choice of using a directed graph to represent the partial order
    # and the choice of using a list adjacency in python (effective when the number of vertices is large here, our assertions), another possible representation is the adjacency matrix (effective when the number of edges is large)
    def __init__(self) -> None:
        # The attribute represents the set of assertions, each assertion is associated with an integer identifier and its adjacency list in the form of a tuple : { assertion1 : (0, []), assertion2 : (1, [0,2]), assertion3 : (2,[0]), ....}
        self.__assertions = {}

    def add_assertion(self, assertion: assertion) -> None:
        # This function adds assertions to the ABox, the id associated with each assertion is obtained here automatically
        if assertion not in self.__assertions:
            assertion_id = len(self.__assertions)
            self.__assertions[assertion] = (assertion_id, [])

    def get_assertion_by_id(self,id) -> assertion:
        for assertion, (assertion_id, _) in self.__assertions.items():
            if assertion_id == id:
                return assertion
        return None  # ID not found
    
    def get_assertion_id(self, assertion) -> int:
        return self.__assertions[assertion][0]
    
    def get_assertion_successors(self, assertion) -> list():
        return self.__assertions[assertion][1]

    def add_directed_edge(self, from_assertion, to_assertion) -> None:
        # If from_assertion is strictly preferred to to_assertion we add an edge from the 1st to the second
        # In order to represent equalit we add the edge in both directions, so we need to call this function twice with reversed parameters, this is discussed mor in the documentation
        if from_assertion in self.__assertions and to_assertion in self.__assertions:
            to_vertex = self.get_assertion_id(to_assertion)
            self.__assertions[from_assertion][1].append(to_vertex)

    def get_assertions(self) -> list():
        # a function returning the list of assertions
        return list(self.__assertions.keys())
    
    def get_directed_edges(self) -> list():
        # a function returning the list of all the edges
        edges = []
        for from_assertion, (assertion_id, successors) in self.__assertions.items():
            for successor in successors:
                to_assertion = self.get_assertion_by_id(successor)
                edges.append((from_assertion, to_assertion))
        return edges

    def is_strictly_preferred(self, assertion_1, assertion_2, first_call=True) -> bool:
        # a test if assertion_1 is strictly preferred to assertion_2
        if assertion_1 in self.__assertions and assertion_2 in self.__assertions:
            vertex_1 = self.get_assertion_id(assertion_1)
            vertex_2 = self.get_assertion_id(assertion_2)
            successors_1 = self.get_assertion_successors(assertion_1)
            successors_2 = self.get_assertion_successors(assertion_2)
            # in the first call, we don' need the two assertions to be equivalent (both in each one successors)
            if first_call and vertex_2 in successors_1 and vertex_1 not in successors_2:
                return True
            # in the rest of the subsequent recursive calls if the assertion is equivalent to one of our assertions successors (or their successors) it is retianed
            if not first_call and vertex_2 in successors_1:
                return True
            # for all assertion successors and their successors we need to check if assertion_2 is their, the partial order is a transitive relation  
            for vertex in successors_1:
                new_assertion = self.get_assertion_by_id(vertex)
                if self.is_strictly_preferred(new_assertion, assertion_2, False):
                    return True

        return False