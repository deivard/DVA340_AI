import argparse
import random
from math import sqrt
from functools import reduce
import copy


class City:
    def __init__(self, id_, x, y):
        self.id = id_
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"ID: {self.id}, x: {self.x}, y: {self.y}"


class Ant:
    def __init__(self, name, location, city_edges_ref):
        self.name = name
        self.city_edges_ref = city_edges_ref
        self.location = location
        self.start = location
        self.visited = [self.location]
        self.distance_traveled = 0

    def move(self, alpha, beta):
        nxt = self.chose_next_city(alpha, beta)
        if nxt is not None:
            self.distance_traveled += self.city_edges_ref[self.location][nxt]["distance"]
            self.visited.append(nxt)
            self.location = nxt
        else:
            self.distance_traveled += self.city_edges_ref[self.location][self.start]["distance"]
            self.visited.append(self.start)
            self.location = self.start

        return self.location

    def has_visited_edge(self, from_, to):
        for i in range(1, len(self.visited)):
            if self.visited[i-1] == from_ and self.visited[i] == to:
                return True
        return False

    def chose_next_city(self, alpha, beta):
        probabilities = []
        for e in self.city_edges_ref[self.location]:
            if e["to_city"] not in self.visited:
                probabilities.append({"to_city": e["to_city"], "probability": (e["pheromone"]**alpha) * ((1/e["distance"])**beta)})

        sum_ = sum([p["probability"] for p in probabilities])
                   # (lambda p,_: p, probabilities)["probability"]

        for p in probabilities:
            p["probability"] = p["probability"] / sum_

        probabilities.sort(key=lambda p: p["probability"], reverse=True)


        fix this
        dice = random.random()
        for p in probabilities:
            if dice > p["probability"]:
                return p["to_city"]

        return None


def distance(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def calc_distances(city_edges, cities_ref):
    for i, ce in enumerate(city_edges):
        for e in ce:
            e["distance"] = distance(cities_ref[i], cities_ref[e["to_city"]])


def initialize_ants(num_ants, cities, city_edges_ref, random_names):
    return [Ant(random_names[random.randint(0, len(random_names)-1)],
                random.randint(0, len(cities)-1),
                city_edges_ref) for _ in range(num_ants)]


def update_pheromone(ants, city_edges, evaporation_rate):
    for i,ce in enumerate(city_edges):
        for j in range(len(ce)):
            sum_p = 0
            for ant in ants:
                if ant.has_visited_edge(i, j):
                    sum_p += 1/ant.distance_traveled
            ce[j]["pheromone"] = (1 - evaporation_rate) * ce[j]["pheromone"] + sum_p


def main():
    ALPHA = 0.5
    EVAPORATION_RATE = 0.2
    BETA = 0.5
    cities = []
    city_edges = [{"to_city": i, "distance": 0, "pheromone": 1} for i in range(52)]
    city_edges = [copy.deepcopy(city_edges) for _ in range(52)]
    # random_names = []
    with open("orc_names.txt") as f:
        random_names = [line.rstrip("\n") for line in f.readlines()]
    # Load the data
    with open("Assignment 3 berlin52.tsp") as f:
        lines = f.readlines()

    for line in lines:
        id_, x, y = line.split()
        cities.append(City(int(id_), x, y))

    calc_distances(city_edges, cities)


    while True:
        antz = initialize_ants(100, cities, city_edges, random_names)
        for _ in range(len(cities)):
            for ant in antz:
                ant.move(ALPHA, BETA)

        antz.sort(key=lambda a: a.distance_traveled)
        best_ant = antz[0]
        print(f"{best_ant.name} is the best ant! Path distance: {best_ant.distance_traveled}")
        update_pheromone(antz, city_edges, EVAPORATION_RATE)


if __name__ == '__main__':
    main()