import argparse
import random
from math import sqrt
import copy


class City:
    def __init__(self, id_, x, y):
        self.id = id_
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"ID: {self.id}, x: {self.x}, y: {self.y}"


class Ant:
    def __init__(self, location):

        self.location = location
        self.visited = [self.location]


def distance(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def calc_distances(city_edges, cities_ref):
    for i, ce in enumerate(city_edges):
        for e in ce:
            a = cities_ref[i]
            b =e["to_city"]
            e["distance"] = distance(cities_ref[i], cities_ref[e["to_city"]])


def main():
    cities = []
    city_edges = [{"to_city": i, "distance": 0, "pheromone": 0} for i in range(52)]
    city_edges = [copy.deepcopy(city_edges) for _ in range(52)]
    # Load the data
    with open("Assignment 3 berlin52.tsp") as f:
        lines = f.readlines()

    for line in lines:
        id_, x, y = line.split()
        cities.append(City(int(id_), x, y))

    calc_distances(city_edges, cities)

    print("asd")




if __name__ == '__main__':
    main()