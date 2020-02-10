# import sys
# from queue import PriorityQueue
from collections import deque
from tabulate import tabulate
import time
from anytree import NodeMixin, RenderTree


class Item:
    def __init__(self, id, benefit, weight):
        self.id = id
        self.benefit = int(benefit)
        self.weight = int(weight)
        if self.weight == 0:
            self.BW = 0
        else:
            self.BW = self.benefit / self.weight

    def print(self):
        print("ID: {}, Benefit: {}, Weight: {}".format(self.id, self.benefit, self.weight))

    def to_array(self):
        return [self.id, self.benefit, self.weight, self.BW]


# Used to represent the graph that will be traversed
class Node:
    def __init__(self, data, edges=None):
        self.data = data
        self.edges = edges


class SolutionNode():
    def __init__(self, node, visited=None, parent=None, current_weight=0, total_benefit=0):
        if visited is None:
            visited = []
        self.visited = visited
        self.node = node  # Item
        self.parent = parent  # SolutionNode
        self.current_weight = current_weight
        self.total_benefit = total_benefit
        self.solution_added = False

    def has_visited(self, node):
        # print(self.visited)
        if self.visited is not None:
            for n in self.visited:
                if node.data.id == n.data.id:
                    return True
        return False

    def print(self):
        current = self
        num_items = 1
        items = []
        while current.parent is not None:
            num_items += 1
            items.append(current.node.data)
            current = current.parent

        headers = ["ID", "Benefit", "Weight", "B/W"]
        data = []
        [data.append(i.to_array()) for i in items]
        print("Solution:")
        table = tabulate(data, headers=headers, tablefmt="presto")
        print(table)

        print("Total benefit: {}\nTotal weight: {}\nNumber of items: {}\n".format(self.total_benefit, self.current_weight, num_items))


def search(graph, max_weight, algorithm="BFS"):

    queue = deque()
    if algorithm == "BFS":
        pop_function = queue.popleft
    elif algorithm == "DFS":
        pop_function = queue.pop
    else:
        raise ValueError("Invalid value for algorithm: {}\nSupported values are: \"BFS\" and \"DFS\""
                         .format(algorithm))

    # List that stores all found solutions (all paths that are within the weight limit)
    solutions = []
    root = SolutionNode(graph)
    queue.append(root)
    highest_benefit_solution = root

    while len(queue):
        # print("Queue length: {}".format(len(queue)))
        current = pop_function()
        # print("Popped from queue")
        if current.node.edges:
            for edge in current.node.edges:
                if not current.has_visited(edge):
                    if current.current_weight + edge.data.weight > max_weight:
                        if not current.solution_added:
                            solutions.append(current)
                            current.solution_added = True
                            if current.total_benefit > highest_benefit_solution.total_benefit:
                                highest_benefit_solution = current
                    else:
                        in_queue = False
                        for s in queue:
                            if s.node.data.id == edge.data.id:
                                in_queue = True
                                break
                        if not in_queue:
                            queue.append(SolutionNode(edge, current.visited + [current.node], current,
                                                    current.current_weight + edge.data.weight,
                                                    current.total_benefit + edge.data.benefit))

    # print(len(solutions))
    return highest_benefit_solution


if __name__ == "__main__":
    # Read the data
    with open('data.txt') as f:
        read_data = f.read().splitlines()

    items = []
    for l in read_data:
        i, b, w = l.split(' ')
        items.append(Item(i, b, w))

    # [i. for i in items]


    # Create the graph
    nodes = [Node(item) for item in items]
    root = Node(Item("", 0, 0), nodes)
    for i in range(len(nodes)):
        nodes[i].edges = [root] + nodes[:i] + nodes[i + 1:]

    print("Breadth first search\n")
    t_start = time.time()
    solution = search(root, 420, "BFS")
    t_end = time.time()
    solution.print()
    print("Elapsed time: {}".format(t_end-t_start))

    print("Depth first search\n")
    t_start = time.time()
    solution = search(root, 420, "DFS")
    t_end = time.time()
    solution.print()
    print("Elapsed time: {}".format(t_end-t_start))

















