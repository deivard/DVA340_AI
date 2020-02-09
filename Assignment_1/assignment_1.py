# import sys
# from queue import PriorityQueue
from collections import deque
from anytree import NodeMixin, RenderTree


class Item:
    def __init__(self, id, benefit, weight):
        self.id = id
        self.benefit = benefit
        self.weight = weight

    def print(self):
        print("ID: {}, Benefit: {}, Weight: {}".format(self.id, self.benefit, self.weight))


class Node:
    def __init__(self, data, edges=None):
        self.data = data
        self.edges = edges
        self.visited = False


class ItemNode(NodeMixin):
    def __init__(self, data, parent=None, children=None):
        self.data = data
        self.parent = parent
        if children:
            self.children = children


class Solution:
    def __init__(self):
        self.visited = []



# BFS
def bfs(root):
    #
    paths = []
    [paths.append([edge]) for edge in root.edges]

    queue = deque()
    queue.append(root)

    while queue:
        node = queue.popleft()
        if node.edges:





if __name__ == "__main__":
    # Read the data
    with open('data.txt') as f:
        read_data = f.read().splitlines()

    items = []
    for l in read_data:
        i, b, w = l.split(' ')
        items.append(Item(i, b, w))

    # [i. for i in items]

    # Create the tree
    nodes = [Node(item) for item in items]
    root = Node(None, nodes)
    for i in range(len(nodes)):
        nodes[i].edges = [root] + nodes[:i] + nodes[i + 1:]

    print(nodes)
    bfs(root)

















