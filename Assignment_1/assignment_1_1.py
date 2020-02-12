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
    def __init__(self, depth=0, current_weight=0, total_benefit=0, items=None,):
        if items is None:
            items = []
        self.items = items
        self.current_weight = current_weight
        self.total_benefit = total_benefit
        self.depth = depth

    def print(self, items_list):
        if len(items_list) != len(self.items):
            raise ValueError("The provided items_list is not the same length as the taken items list.\n"
                             "Provided items_list length: {}\n"
                             "Taken items list length: {}".format(len(items_list), len(self.items)))
        in_knapsack = []
        for i in range(len(self.items)):
            if self.items[i] == 1:
                in_knapsack.append(items_list[i])

        headers = ["ID", "Benefit", "Weight", "B/W"]
        data = []
        [data.append(i.to_array()) for i in in_knapsack]
        table = tabulate(data, headers=headers, tablefmt="presto")
        print(table)

        print("Total benefit: {}\nTotal weight: {}\nNumber of items: {}\n".format(self.total_benefit,
                                                                                  self.current_weight, len(in_knapsack)))


def search(items, max_weight, algorithm="BFS"):
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
    root = SolutionNode()
    queue.append(root)
    highest_benefit_solution = root

    while len(queue):
        # print("Queue length: {}".format(len(queue)))
        current = pop_function()
        if current.total_benefit > highest_benefit_solution.total_benefit:
            highest_benefit_solution = current

        if current.depth < len(items):
            # Take item
            take = SolutionNode(current.depth+1, current.current_weight + items[current.depth].weight,
                                current.total_benefit + items[current.depth].benefit, current.items + [1])
            # Don't take item
            takent = SolutionNode(current.depth+1, current.current_weight,
                                  current.total_benefit, current.items + [0])
            # Don't add solution to the queue if it already is too heavy
            if take.current_weight <= max_weight:
                queue.append(take)
                # This must mean that the current is a solution, add it to the solutions list for evaluation purposes
                solutions.append(current)

            queue.append(takent)

    print("Found {} solutions.".format(len(solutions)))
    return highest_benefit_solution


if __name__ == "__main__":
    # Read the data
    with open('data.txt') as f:
        read_data = f.read().splitlines()

    items = []
    for l in read_data:
        i, b, w = l.split(' ')
        items.append(Item(i, b, w))

    print("Breadth first search\n")
    t_start = time.time()
    solution = search(items, 420, "BFS")
    t_end = time.time()
    print("\nHighest benefit solution:")
    solution.print(items)
    print("Elapsed time: {}\n".format(t_end-t_start))

    print("Depth first search:")
    t_start = time.time()
    solution = search(items, 420, "DFS")
    t_end = time.time()
    print("\nHighest benefit solution:")
    solution.print(items)
    print("Elapsed time: {}".format(t_end-t_start))

















