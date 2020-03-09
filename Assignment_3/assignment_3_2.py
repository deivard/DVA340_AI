import random
from math import sqrt
import copy
import matplotlib.pyplot as plt


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

        for p in probabilities:
            p["probability"] = p["probability"] / sum_

        probabilities.sort(key=lambda p: p["probability"], reverse=True)
        for i in range(1, len(probabilities)):
            probabilities[i]["probability"] = probabilities[i-1]["probability"] + probabilities[i]["probability"]

        dice = random.random()
        for i in range(len(probabilities)-1, 0, -1):
            if probabilities[i]["probability"] > dice > probabilities[i - 1]["probability"]:
                return probabilities[i]["to_city"]

        return probabilities[0]["to_city"] if len(probabilities) else None


def distance(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def calc_distances(city_edges, cities_ref):
    for i, ce in enumerate(city_edges):
        for e in ce:
            e["distance"] = distance(cities_ref[i], cities_ref[e["to_city"]])


def initialize_ants(num_ants, city_edges_ref, random_names):
    return [Ant(random_names[random.randint(0, len(random_names)-1)],
                0, city_edges_ref) for _ in range(num_ants)]


def update_pheromone(ants, city_edges, evaporation_rate):
    for ce in city_edges:
        for j in range(len(ce)):
            ce[j]["pheromone"] = (1 - evaporation_rate) * ce[j]["pheromone"]  # + sum_p

    for ant in ants:
        for i in range(1, len(ant.visited)):
            city_edges[ant.visited[i-1]][ant.visited[i]]["pheromone"] += 1/ant.distance_traveled
            city_edges[ant.visited[i]][ant.visited[i-1]]["pheromone"] += 1/ant.distance_traveled


def main():
    best_in_iterations = []
    ALPHA = 1.3
    EVAPORATION_RATE = 0.3
    BETA = 1.5
    cities = []
    city_edges = [{"to_city": i, "distance": 0, "pheromone": 4} for i in range(52)]
    city_edges = [copy.deepcopy(city_edges) for _ in range(52)]
    with open("orc_names.txt") as f:
        random_names = [line.rstrip("\n") for line in f.readlines()]
    # Load the data
    with open("Assignment 3 berlin52.tsp") as f:
        lines = f.readlines()

    for line in lines:
        id_, x, y = line.split()
        cities.append(City(int(id_), x, y))

    calc_distances(city_edges, cities)

    while len(best_in_iterations) < 150:
        antz = initialize_ants(50, city_edges, random_names)
        for _ in range(len(cities)):
            for ant in antz:
                ant.move(ALPHA, BETA)

        antz.sort(key=lambda a: a.distance_traveled)
        best_ant = antz[0]
        best_in_iterations.append(antz[0].distance_traveled)
        print(f"{best_ant.name} is the best ant! Path distance: {best_ant.distance_traveled}")
        update_pheromone(antz, city_edges, EVAPORATION_RATE)


    plt.plot([i for i in range(len(best_in_iterations))],best_in_iterations)
    plt.xlabel('Iteration')
    plt.ylabel('Best distance')
    plt.title("ACO")
    plt.savefig('graph.png')

if __name__ == '__main__':
    main()