import random
from copy import copy
from math import sqrt
import random



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

    def __repr__(self):
        return f"Distance: {self.fitness} \nRoute: {self.route}"

    def mutate(self, type):
        # print("Mutating")
        if type == "revseq":
            # print("downs")
            r1 = random.randint(1, len(self.route)-2)
            r2 = random.randint(r1, len(self.route)-1)
            self.route = self.route[:r1] + self.route[r2-1:r1-1:-1] + self.route[r2:]
        elif type == "swap":
            r1 = random.randint(1, len(self.route)-2)
            r2 = random.randint(1, len(self.route)-2)
            self.route[r1], self.route[r2] = self.route[r2], self.route[r1]
            self.evaluate_fitness()


def breed(parent_a, parent_b, adaptive_mutation_rate):
    MUTATION_CHANCE = 0.4 + adaptive_mutation_rate
    UBER_MUTATION_CHANCE = 0.1 #+ adaptive_mutation_rate * 0.1

    o1, o2 = crossover(parent_a, parent_b)
    # Mutate
    if random.random() <= MUTATION_CHANCE:
        o1.mutate("swap")
    if random.random() <= MUTATION_CHANCE:
        o2.mutate("swap")
    if random.random() <= UBER_MUTATION_CHANCE:
        o1.mutate("revseq")
    if random.random() <= UBER_MUTATION_CHANCE:
        o1.mutate("revseq")

    return [o1, o2]


# Cycle Crossover
def crossover(first, second):
    # Chromosomes of parents (don't include the start and end cities since they always will be the same)
    c1 = first.route[1:-1]
    c2 = second.route[1:-1]
    cycles = [[]]
    cycle = 0
    while len(c1) and len(c2):
        cycle_start_value = c1[0]
        cycles[cycle].append(c1[0])

        last_added = c1[0]
        # Complete one cycle
        while True:
            v1 = c2[c1.index(last_added)]
            v2 = c2[c1.index(v1)]
            if v1 not in cycles[cycle]:
                cycles[cycle].append(v1)
                last_added = v1
            if v2 not in cycles[cycle]:
                cycles[cycle].append(v2)
                last_added = v2
            # Check if the cycle is complete
            if v1 == cycle_start_value:
                break
        # Remove used values from both chromosomes
        c1 = [i for i in c1 if i not in cycles[cycle]]
        c2 = [i for i in c2 if i not in cycles[cycle]]
        # Advance cycle counter
        cycle += 1
        cycles.append([])
        if len(c2) == 1 and len(c1) == 1:
            cycles[cycle].append(c1[0])
            break

    # Recreate the original chromosomes (since we "removed" values before)
    c1 = first.route[1:-1]
    c2 = second.route[1:-1]
    # Construct the offspring
    # Offspring
    o1 = [-1] * (len(c1))
    o2 = [-1] * (len(c2))
    for i, cycle in enumerate(cycles):
        for j in cycle:
            # If we are on an even cycle
            if i % 2 == 0:
                o2[c1.index(j)] = j
                o1[c2.index(j)] = j
            # Odd cycle
            else:
                o1[c1.index(j)] = j
                o2[c2.index(j)] = j

    return [Individual([0]+o1+[0], first.cities_ref), Individual([0]+o2+[0], second.cities_ref)]

# def crossover(first, second):
#     offspring1_route = []
#     offspring2_route = []
#     route_len = len(first.route)
#
#     first_route = copy(first.route[1:-1])
#     second_route = copy(second.route[1:-1])
#     # Step 2. Select 1st bit from second parent as a 1st bit of first offspring.
#     # offspring1_route.append(second.route[1])
#     # Step 3. The selected bit from Step 2 would be found in first parent and pick the
#     # exact same position bit which is in second parent and that bit would be found
#     # again in the first parent and, finally, the exact same position bit which is in second
#     # parent will be selected for 1st bit of second offspring.
#
#     offspring1_route.append(second_route[0])
#
#
#     last_added_in_second = -1
#     removed_to_index = 0
#     times_called = -1
#     while len(offspring1_route) < route_len-2:
#         # Step 6
#         for i in offspring1_route[removed_to_index+1:]:
#             try:
#                 second_route.remove(i)
#                 first_route.remove(i)
#             except ValueError as err:
#                 pass
#         # for i in offspring2_route[removed_to_index+1:]:
#         #     try:
#         #         first_route.remove(i)
#         #     except ValueError as err:
#         #         pass
#         # Save the index we removed until, so we don't have to raise so many exceptions
#         removed_to_index = len(offspring2_route)-1
#         times_called += 1
#         # for i in offspring1_route:
#         #     try:
#         #         second.route.remove(i)
#         #     except ValueError as err:
#         #         pass
#
#         # Step 2
#         offspring1_route.append(second_route[1])
#
#         # One cycle (Step 5: repeating step 3 and 4)
#         while len(offspring1_route) < route_len-2:  #first.route[1] != last_added_in_second:
#             try:
#                 # bit_in_second_1 = second.route[first.route.index(offspring1_route[-1])]
#                 # bit_in_second_2 = second.route[first.route.index(bit_in_second_1)]
#                 # offspring2_route.append(bit_in_second_2)
#                 # offspring2_route.append(second.route[first.route.index(bit_in_second)])
#                 #
#                 index1 = first_route.index(offspring1_route[-1])
#                 bit1 = second_route[index1]
#                 index2 = first_route.index(bit1)
#                 bit2 = second_route[index2]
#                 offspring2_route.append(copy(bit2))
#                 last_added_in_second = bit2
#             except ValueError as err:
#                 print(err)
#             # Step 3
#
#             if first_route[1] == last_added_in_second:
#                 break
#             else:
#                 # Step 4
#                 offspring1_route.append(second_route[first_route.index(copy(offspring2_route[-1]))])
#
#     # bit_in_second =
#     offspring2_route.append(copy(second_route[first_route.index(second_route[first_route.index(offspring1_route[-1])])]))
#
#     ordered = sorted(offspring1_route)
#     ordered2 = sorted(offspring2_route)
#
#     return [Individual(offspring1_route, first.cities_ref), Individual(offspring2_route, second.cities_ref)]


def create_random_population(cities, population_size):
    c_indices = [i for i in range(1, len(cities))]
    population = []
    for i in range(population_size):
        route = copy(c_indices)
        random.shuffle(route)
        population.append(Individual([0] + route + [0], cities))

    return population


def main():
    adaptive_mutation_rate = 0
    breed_offset = 0
    POPULATION_SIZE = 1000
    ELITISM = 100
    NUM_ALPHAS = 50
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

    # crossover(Individual([0,1,2,3,4,5,6,7,8,0], cities), Individual([0,2,7,5,8,4,1,6,3,0], cities))
    # crossover(Individual([0,3,4,8,2,7,1,6,5,0], cities), Individual([0,4,2,5,1,6,8,3,7,0], cities))
    # crossover(Individual([0,8,4,7,3,6,2,5,1,9,0,0], cities), Individual([0,0,1,2,3,4,5,6,7,8,9,0], cities))

    generation = 0
    best_individual = population[0]
    prev_best = population[0].fitness
    generations_without_improvement = 0
    # Termination criteria satisfied?
    while True:
        generation += 1
        # Sort the population based on their fitness
        population.sort(key=lambda i: i.fitness)
        print(f"Gen {generation} - Best in population: {population[0].fitness}")
        # print(population)
        new_generation = []
        # Select the NUM_ALPHAS best parents according to fitness and two random individuals
        r1, r2 = random.randint(NUM_ALPHAS,POPULATION_SIZE-1), random.randint(NUM_ALPHAS,POPULATION_SIZE-1)
        alphas = population[:NUM_ALPHAS]#-2] + [population[r1]] + [population[r2]]#(POPULATION_SIZE//4)]

        # Roulette wheel selection
        # fit_sum = 0
        # for i in population:
        #     fit_sum += (1/i.fitness)
        # # Probabilities
        # prob = []
        # prev_prob = 0
        # for i in population:
        #     i_prob = prev_prob + ((1/i.fitness)/fit_sum)
        #     prob.append(i_prob)
        #     prev_prob = i_prob
        # selected_individual = population[0]
        # rand_num = random.random()
        # for i in range(len(prob[:-1])-1):
        #     if rand_num > prob[i] and rand_num < prob[i+1]:
        #         selected_individual = population[i]

        # Queue the sexy music and let the breeding begin
        for i, individual in enumerate(population[::-1]):
        # for i in range(0, len(population)//2):
            # selected_individual = population[0]
            # rand_num = random.random()
            # for j in range(len(prob[:-1]) - 1):
            #     if prob[j] < rand_num < prob[j + 1]:
            #         selected_individual = population[j]
            #         break
            # rand_individual = population[random.randint(0, len(population)-1)]
            # new_generation.extend(breed(population[i+1], individual))#alphas[i % (len(alphas)-1)], individual))
            new_generation.extend(breed(alphas[(i+breed_offset) % (len(alphas)-1)], individual, adaptive_mutation_rate))
            # new_generation.extend(breed(alphas[0], alphas[1]))
            # new_generation.extend(breed(population[i], individual))
            # new_generation.extend(breed(selected_individual, rand_individual))

        # population = sorted((new_generation+population),key=lambda i: i.fitness)[:POPULATION_SIZE]
        new_generation.sort(key=lambda i: i.fitness)
        # Select the 75 best from new generation and 25 best from old generation
        population = population[:ELITISM] + new_generation[:len(population)-ELITISM] #alphas[:ELITISM] + new_generation[:len(population)-len(alphas[:ELITISM])] #[:POPULATION_SIZE//2] + population[:POPULATION_SIZE//2] #[:(POPULATION_SIZE // 4) * 3] + population[:POPULATION_SIZE // 4]  #sorted(new_generation + population, key=lambda i: i.fitness)[:200]
        # population = new_generation[:ELITISM] + population[:len(population)-ELITISM] #alphas[:ELITISM] + new_generation[:len(population)-len(alphas[:ELITISM])] #[:POPULATION_SIZE//2] + population[:POPULATION_SIZE//2] #[:(POPULATION_SIZE // 4) * 3] + population[:POPULATION_SIZE // 4]  #sorted(new_generation + population, key=lambda i: i.fitness)[:200]
        # population = new_generation[:POPULATION_SIZE] # + population[:len(population)-ELITISM] #alphas[:ELITISM] + new_generation[:len(population)-len(alphas[:ELITISM])] #[:POPULATION_SIZE//2] + population[:POPULATION_SIZE//2] #[:(POPULATION_SIZE // 4) * 3] + population[:POPULATION_SIZE // 4]  #sorted(new_generation + population, key=lambda i: i.fitness)[:200]

        if population[0].fitness == prev_best:
            generations_without_improvement += 1
        else:
            generations_without_improvement = 0
        adaptive_mutation_rate = 0.1 * generations_without_improvement
        if generations_without_improvement > 10:
            # breed_offset += 1
            print(f"Adaptive mutation rate: {adaptive_mutation_rate}")
        prev_best = population[0].fitness  # sorted(population,key=lambda i: i.fitness)[0]


if __name__ == '__main__':
    main()

