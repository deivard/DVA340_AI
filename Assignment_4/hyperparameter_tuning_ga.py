#!/usr/bin/python

import socket  # Import socket module
import numpy as np
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool
import os
import random
from assignment_4 import MancalaAI as Skynet


class Individual:
    def __init__(self, utility_weights, fitness=0):
        self.utility_weights = utility_weights
        self.fitness = fitness
        self.game_history = []

    def mutate(self):
        # Take a random weight and add a random number between -5 and 5 to it
        self.utility_weights[random.randint(0, len(self.utility_weights)-1)] += (random.random()-0.5)


def crossover(first, second):
    r1 = random.randint(1, len(first.utility_weights) - 2)
    r2 = random.randint(r1, len(first.utility_weights) - 1)
    section1 = first.utility_weights[r1:r2]
    # section2 = [i for i in second.utility_weights if i not in section1]
    offspring_weights = second.utility_weights[:r1] + section1 + second.utility_weights[r1:]

    return Individual(offspring_weights)


def breed(first, second):
    MUTATION_CHANCE = 0.5

    offspring = crossover(first, second)
    if random.random() <= MUTATION_CHANCE:
        offspring.mutate()

    return offspring


def create_initial_population(size, num_weights):
    return [Individual([(random.random()-0.5)*5 for _ in range(num_weights)]) for _ in range(size)]


def write_individual_to_file(individual, generation_num):
    timestamp = datetime.now()
    print("WRITING TO FILE")
    with open("evolution_data.txt", "a") as f:
        f.write(f"{timestamp} - G{generation_num}: best_fitness={individual.fitness}\t"
                f"best_weights={individual.utility_weights}\t game_history={individual.game_history}\n")


def receive(socket):
    msg = ''.encode()  # type: str

    try:
        data = socket.recv(1024)  # type: object
        msg += data
    except:
        pass
    return msg.decode()


def send(socket, msg):
    socket.sendall(msg.encode())


# VARIABLES
playerName = 'Big_Brain_AI'
host = '127.0.0.1'
port = 30000  # Reserve a port for your service.
s = socket.socket()  # Create a socket object
pool = ThreadPool(processes=1)
MAX_RESPONSE_TIME = 10

# GA Variables
ELITISM = 3
POPULATION_SIZE = 10
NUM_ALPHAS = 2
breed_offset = 0
mancala_ai = Skynet(2, [])
population = create_initial_population(POPULATION_SIZE, 5)
generation_best = []

print('The player: ' + playerName + ' starts!')
s.connect((host, port))
print('The player: ' + playerName + ' connected!')

generation = -1
prev_best = -9000
generations_without_improvement = 0
while True:
    generation += 1
    if generation != 0:
        # Sort the population based on fitness (we want to maximize fitness)
        population.sort(key=lambda i: i.fitness, reverse=True)
        print(f"Gen {generation} - Best in population: {population[0].fitness}. Weights = {population[0].utility_weights}")
        write_individual_to_file(population[0], generation+1)
        # Check if we improved or not
        if population[0].fitness == prev_best:
            generations_without_improvement += 1
        else:
            generations_without_improvement = 0
        # Adjust the breed offset if we haven't improved for a while
        if generations_without_improvement > 10:
            breed_offset += 1
        prev_best = population[0].fitness

        # Select the alphas
        alphas = population[:NUM_ALPHAS]

        new_generation = []
        # Now kiss!
        for i, individual in enumerate(population):
            new_generation.append(breed(alphas[(i+breed_offset) % (len(alphas)-1)], individual))

        new_generation.sort(key=lambda i: i.fitness, reverse=True)

        # Select the ELITISM best from new generation and the rest from the best of the old generation
        population = population[:ELITISM] + new_generation[:len(population)-ELITISM]

    # Let each individual play against the AI so we can evaluate their fitness
    for individual in population:
        game_values = []
        games_played = 0
        # Set the individual's utility_weights as the utility_weights to use for the Mancala AI
        mancala_ai.utility_weights = individual.utility_weights
        # Each individual should play 4 games to be evaluated
        while games_played < 2:
            # print(f"Utility weights: {mancala_ai.utility_weights}")
            asyncResult = pool.apply_async(receive, (s,))
            startTime = time.time()
            currentTime = 0
            received = 0
            data = []
            while received == 0 and currentTime < MAX_RESPONSE_TIME:
                if asyncResult.ready():
                    data = asyncResult.get()
                    received = 1
                currentTime = time.time() - startTime

            if received == 0:
                print('No response in ' + str(MAX_RESPONSE_TIME) + ' sec')
                gameEnd = 1

            if data == 'N':
                send(s, playerName)

            if data[0] == 'E':
                player_points, other_points = [int(i) for i in data.split()[1:3]]
                game_values.append(player_points - other_points)
                print(f"Game {games_played+1} ended. (Player) {player_points} - {other_points} (Opponent)")
                games_played += 1


                # Acknowledge that the game ended and that a new game will start
                send(s, "OK")
                continue

            if len(data) > 1:
                # Read the board and player turn
                board = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                playerTurn = int(data[0])
                i = 0
                j = 1
                while i <= 13:
                    board[i] = int(data[j]) * 10 + int(data[j + 1])
                    i += 1
                    j += 2

                # Using your intelligent bot, assign a move to "move"
                #
                # example: move = '1';  Possible moves from '1' to '6' if the game's rules allows those moves.
                # TODO: Change this
                ################
                mancala_ai.update_state(board, playerTurn)
                move = str(mancala_ai.get_best_move())
                # print(f"Best move is:{move}")
                ################
                send(s, move)

        # After 10 games are played, we evaluate the individual's fitness by
        # summing the game values (difference in points)
        individual.fitness = sum(game_values)
        individual.game_history = game_values
