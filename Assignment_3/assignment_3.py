import random
import copy
from math import sqrt


class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"ID: {self.id}, x: {self.x}, y: {self.y}"


class Individual:
    def __init__(self, route, cities_ref):
        self.route = route
        self.cities_ref = cities_ref
        self.fitness = self.evaluate_fitness()

    def evaluate_fitness(self):
        fitness = 0
        # Loop the cities in the route and calculate the distance between each city
        for i in range(1, len(self.route)):
            from_ = self.cities_ref[self.route[i-1]]
            to = self.cities_ref[self.route[i]]
            d = sqrt((to.x - from_.x)**2 + (to.y - from_.y)**2)
            fitness += d

        return fitness


def create_random_population(cities, population_size):
    c_indices = [i for i in range(len(cities))]
    population = []
    for i in range(population_size):
        route = copy.copy(c_indices)
        random.shuffle(route)
        population.append(Individual(route, cities))

    return population


def main():
    POPULATION_SIZE = 100

    cities = []
    # Load the data
    with open("Assignment 3 berlin52.tsp") as f:
        lines = f.readlines()

    for line in lines:
        id_, x, y = line.split()
        cities.append(City(id_, x, y))

    # Create initial population

    # The population is a list of Individuals. An individual
    # has a list of city indices (0 to len(cities)-1) that each represent a
    # city in the cities list and the order they are visited by this individual, aka the route
    population = create_random_population(cities, POPULATION_SIZE)

    print(population)

    generation = 0
    best_individual = population[0]



    # Evaluate fitness of each individual
    # for route, fitness in population:


    # Termination criteria satisfied?
        # Return best of population for

    # Select parents according to fitness

    # Recombine parent to generate a set of offspring
    # CX2: https://www.hindawi.com/journals/cin/2017/7430125/#computational-experiments-and-discussion

    # Mutate offspring

    # Replace population by the set of new offspring


if __name__ == '__main__':
    main()

