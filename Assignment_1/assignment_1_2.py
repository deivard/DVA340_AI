from queue import PriorityQueue
import time

class City:
    def __init__(self, name, ):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Vertex):
            return self.name == other.city.name


class Vertex:
    def __init__(self, city, straight_line_distance=None, edges=None):
        self.city = city
        if edges is None:
            edges = []
        self.edges = edges
        self.straight_line_distance = straight_line_distance

    def add_edge(self, edge):
        self.edges += [edge]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.city.name == other.city.name
        if isinstance(other, str):
            return self.city.name == other
        if isinstance(other, City):
            return self.city.name == other.name


class Edge:
    def __init__(self, destination, weight):
        self.destination = destination  # Vertex
        self.weight = weight

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.destination == other.destination and self.weight == other.weight
            # return ((self.destination[0] == other.destination[0] and self.destination[1] == other.destination[1])
            #         or (self.destination[0] == other.destination[1] and self.destination[1] == other.destination[0]))


def parse_city(line_read, **kwargs):
    if len(line_read) > 2:  # To skip blank lines
        cities = kwargs["cities"]
        vertices = kwargs["vertices"]
        split = line_read.strip().split(" ")
        # Check if the line is valid
        if len(split) == 3:
            a, b, d = split

            if a in cities:
                a = cities[cities.index(a)]
            else:
                a = City(a)
                cities.append(a)

            if b in cities:
                b = cities[cities.index(b)]
            else:
                b = City(b)
                cities.append(b)

            if a in vertices:
                a_v = vertices[vertices.index(a)]
            else:
                a_v = Vertex(a)
                vertices.append(a_v)

            if b in vertices:
                b_v = vertices[vertices.index(b)]
            else:
                b_v = Vertex(b)
                vertices.append(b_v)

            edge_a = Edge(b_v, int(d))
            edge_b = Edge(a_v, int(d))
            if edge_a not in a_v.edges:
                a_v.add_edge(edge_a)
            if edge_b not in b_v.edges:
                b_v.add_edge(edge_b)


class Solution:
    def __init__(self, current, visited=None, distance_traveled=0, heuristic=0):
        if visited is None:
            visited = []
        self.visited = visited  # Vertices
        self.current = current  # Vertex
        self.distance_traveled = distance_traveled
        self.heuristic = heuristic

    def print(self):
        print("Path distance: {}".format(self.distance_traveled))
        print("Path: ", end="")
        for i in range(len(self.visited)):
            print("{} -> ".format(self.visited[i].city.name), end="")
        print(self.current.city.name)

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __le__(self, other):
        return self.heuristic <= other.heuristic

    def __gt__(self, other):
        return self.heuristic > other.heuristic

    def __ge__(self, other):
        return self.heuristic >= other.heuristic


def greedy_best_first_search(vertices, start, goal):
    prio_q = PriorityQueue()
    # Find the start vertex
    start = vertices[vertices.index(start)]
    # Turn the start vertex Add the start vertex to the queue
    prio_q.put(Solution(start))

    while prio_q.not_empty:
        solution = prio_q.get()
        if solution.current == goal:
            return solution
        for edge in solution.current.edges:
            if edge.destination not in solution.visited:
                prio_q.put(Solution(edge.destination, solution.visited + [solution.current],
                                    heuristic=edge.destination.straight_line_distance,
                                    distance_traveled=solution.distance_traveled+edge.weight))
    return None


def a_star(vertices, start, goal):
    prio_q = PriorityQueue()
    # Find the start vertex
    start = vertices[vertices.index(start)]
    # Turn the start vertex Add the start vertex to the queue
    prio_q.put(Solution(start))

    while prio_q.not_empty:
        solution = prio_q.get()
        if solution.current == goal:
            return solution
        for edge in solution.current.edges:
            if edge.destination not in solution.visited:
                prio_q.put(Solution(edge.destination, solution.visited + [solution.current],
                                    heuristic=solution.distance_traveled + edge.destination.straight_line_distance,
                                    distance_traveled=solution.distance_traveled + edge.weight))
    return None


def parse_std(line_read, **kwargs):
    if len(line_read) > 2:  # To skip blank lines
        split = line_read.strip().split(" ")
        # Check if the line is valid
        if len(split) == 2:
            city, std = split
            v_index = kwargs["vertices"].index(city)
            if v_index != -1:
                vertex = vertices[v_index]
                vertex.straight_line_distance = int(std)


if __name__ == "__main__":
    # Read the data
    with open('Assignment 1 Spain map.txt') as f:
        read_data = f.read().splitlines()

    cities = []
    vertices = []
    parse_function = None
    kwargs = None

    for l in read_data:
        if l.startswith("A B Distance"):
            parse_function = parse_city
            kwargs = {"vertices": vertices, "cities": cities}
            continue
        if l.startswith("Straight line Distances"):
            parse_function = parse_std
            kwargs = {"vertices": vertices}
            continue
        if parse_function is not None and kwargs is not None:
            parse_function(l, **kwargs)

    t_start = time.time()
    solution = greedy_best_first_search(vertices, "Malaga", "Valladolid")
    t_end = time.time()
    print("Greedy best first search - Malaga to Valladolid")
    solution.print()
    print("Elapsed time: {}\n".format(t_end - t_start))

    t_start = time.time()
    solution = a_star(vertices, "Malaga", "Valladolid")
    t_end = time.time()
    print("A* - Malaga to Valladolid")
    solution.print()
    print("Elapsed time: {}\n".format(t_end - t_start))




