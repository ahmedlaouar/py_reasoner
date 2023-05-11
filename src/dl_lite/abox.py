class Abox:
    # This implementation of the ABox considers a partially ordered ABox
    # I made the choice of using a directed graph to represent the partial order
    # and the choice of using a list adjacency in python (effective when the number of vertices is large here, our assertions), another possible representation is the adjacency matrix (effective when the number of edges is large)
    def __init__(self) -> None:
        # The attribute represents the set of assertions, each assertion is associated with an integer identifier and its adjacency list in the form of a tuple : { assertion1 : (0, []), assertion2 : (1, [0,2]), assertion3 : (2,[0]), ....}
        self.__assertions = {}

    def add_assertion(self, assertion):
        if assertion not in self.__assertions:
            assertion_id = len(self.__assertions)
            self.__assertions[assertion] = (assertion_id, [])

    def get_assertion_by_id(self,id):
        for assertion, (assertion_id, _) in self.__assertions.items():
            if assertion_id == id:
                return assertion
        return None  # ID not found
    
    def get_assertion_id(self, assertion):
        return self.__assertions[assertion][0]
    
    def get_assertion_successors(self, assertion):
        return self.__assertions[assertion][1]

    def add_directed_edge(self, from_assertion, to_assertion):
        if from_assertion in self.__assertions and to_assertion in self.__assertions:
            to_vertex = self.get_assertion_id(to_assertion)
            self.__assertions[from_assertion][1].append(to_vertex)

    def get_assertions(self):
        # a function returning the list of assertions
        #return list(self.__assertions.keys())
        return self.__assertions

    def is_strictly_preferred(self, assertion_1, assertion_2, first_call=True):
        if assertion_1 in self.__assertions and assertion_2 in self.__assertions:
            vertex_1 = self.get_assertion_id(assertion_1)
            vertex_2 = self.get_assertion_id(assertion_2)
            successors_1 = self.get_assertion_successors(assertion_1)
            successors_2 = self.get_assertion_successors(assertion_2)

            if first_call and vertex_2 in successors_1 and vertex_1 not in successors_2:
                return True

            if not first_call and vertex_2 in successors_1:
                return True

            for vertex in successors_1:
                new_assertion = self.get_assertion_by_id(vertex)
                if self.is_strictly_preferred(new_assertion, assertion_2, False):
                    return True

        return False

    
abox = Abox()
# Add assertions
abox.add_assertion('E')
abox.add_assertion('A')
abox.add_assertion('B')
abox.add_assertion('C')
abox.add_assertion('D')
# Add edges
abox.add_directed_edge('E','A')
abox.add_directed_edge('E','B')
abox.add_directed_edge('A','C')
abox.add_directed_edge('B','D')
# Get assertions :
print(abox.get_assertions())
# Check if preferred
print(abox.is_strictly_preferred('E','A'))
print(abox.is_strictly_preferred('E','B'))
print(abox.is_strictly_preferred('E','C'))
print(abox.is_strictly_preferred('E','D'))
print(abox.is_strictly_preferred('A','E'))
print(abox.is_strictly_preferred('A','B'))
print(abox.is_strictly_preferred('A','C'))
print(abox.is_strictly_preferred('A','D'))
print(abox.is_strictly_preferred('D','E'))