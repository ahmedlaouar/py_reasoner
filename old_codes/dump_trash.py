class PartialOrder:
    def __init__(self):
        self.vertices = {}
        self.adjacency_list = {}

    def add_element(self, element):
        if element not in self.vertices:
            vertex_id = len(self.vertices)
            self.vertices[element] = vertex_id
            self.adjacency_list[vertex_id] = []

    def add_directed_edge(self, from_element, to_element):
        if from_element in self.vertices and to_element in self.vertices:
            from_vertex = self.vertices[from_element]
            to_vertex = self.vertices[to_element]
            self.adjacency_list[from_vertex].append(to_vertex)

    def get_elements(self):
        return list(self.vertices.keys())

    def get_directed_edges(self):
        edges = []
        for from_vertex, neighbors in self.adjacency_list.items():
            from_element = next((element for element, vertex in self.vertices.items() if vertex == from_vertex), None)
            for neighbor in neighbors:
                to_element = next((element for element, vertex in self.vertices.items() if vertex == neighbor), None)
                edges.append((from_element, to_element))
        return edges

    def __str__(self):
        return str(self.adjacency_list)
    
# Create a new partial order
partial_order = PartialOrder()

# Add elements
partial_order.add_element('A')
partial_order.add_element('B')
partial_order.add_element('C')
partial_order.add_element('D')

# Add directed edges
partial_order.add_directed_edge('A', 'B')
partial_order.add_directed_edge('B', 'C')
partial_order.add_directed_edge('C', 'D')

# Get all elements
elements = partial_order.get_elements()
print(elements)  # Output: ['A', 'B', 'C', 'D']

# Get all directed edges
edges = partial_order.get_directed_edges()
print(edges)  # Output: [('A', 'B'), ('B', 'C'), ('C', 'D')]

# Print the adjacency list
print(partial_order)
# Output:
# {0: [1], 1: [2], 2: [3], 3: []}
