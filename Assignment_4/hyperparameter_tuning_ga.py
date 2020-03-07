#!/usr/bin/python

import socket  # Import socket module
import numpy as np
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool
import random
import argparse
from assignment_4 import MancalaAI as Skynet


parser = argparse.ArgumentParser()
parser.add_argument('--adversarial', dest='adversarial', action='store_const',
                    default=False, const=True,
                    help='Tells the client that it train in adversarial mode against another AI. '
                         'This will make the AI wait for the server to assign it a player number '
                         'instead of assuming that it is player 2.')

args = parser.parse_args()


class Individual:
    def __init__(self, utility_weights, fitness=0):
        self.utility_weights = utility_weights
        self.fitness = fitness
        self.game_history = []

    def mutate(self):
        for _ in range(10):
            # Take a random weight and add a random number between -5 and 5 to it
            random_randint = random.randint(0, len(self.utility_weights) - 1)
            self.utility_weights[random_randint] = round(self.utility_weights[random_randint] + (random.random() - 0.5)*5, 3)
            # Take a random weight and change it's sign
            random_randint = random.randint(0, len(self.utility_weights) - 1)
            self.utility_weights[random_randint] *= -1


def crossover(first, second):
    r1 = random.randint(0, len(first.utility_weights) - 2)
    r2 = random.randint(r1, len(first.utility_weights) - 1)
    section1 = first.utility_weights[r1:r2]
    # section2 = [i for i in second.utility_weights if i not in section1]
    offspring_weights = second.utility_weights[:r1] + section1 + second.utility_weights[r2:]

    return Individual(offspring_weights)


def breed(first, second):
    MUTATION_CHANCE = 1

    offspring = crossover(first, second)
    if random.random() <= MUTATION_CHANCE:
        offspring.mutate()

    return offspring


def create_initial_population(size, num_weights):
    return [Individual([0 if (random.random()-0.5) < 0 else 1 for _ in range(num_weights)]) for _ in range(size)]
    # return [Individual([(random.random()-0.5)*10 for _ in range(num_weights)]) for _ in range(size)]


def write_individuals_to_file(player_num, individuals, generation_num):
    timestamp = datetime.now()
    print("WRITING TO FILE")
    gen = f"G{generation_num}:     "[:6]
    info = f"{timestamp} - {gen}"
    filler = " "*len(info)
    with open(f"p{player_num}_evolution_data.txt", "a") as f:
        f.write(f"{info}")
        for i, individual in enumerate(individuals):
            f.write(f"{filler if i else ''}Rank {i} fitness={individual.fitness}\t"
                    f"weights={individual.utility_weights}\t game_history={individual.game_history}\n")


def receive(socket):
    msg = ''.encode()  # type: str

    try:
        data = socket.recv(1024)  # type: object
        msg += data
    except:
        pass
    # print(f"Received message: {msg}")
    return msg.decode()


def send(socket, msg):
    # print(f"Sending message: {msg}")
    socket.sendall(msg.encode())


# VARIABLES
playerName = 'Big_Brain_AI'
player_num = 2  # Default is player 2
host = '127.0.0.1'
port = 30000  # Reserve a port for your service.
s = socket.socket()  # Create a socket object
pool = ThreadPool(processes=1)
MAX_RESPONSE_TIME = 10


# GA Variables
ELITISM = 7
POPULATION_SIZE = 50
NUM_ALPHAS = 5
NUM_WEIGHTS = 19
breed_offset = 0
mancala_ai = Skynet(2, [])
population = create_initial_population(POPULATION_SIZE, NUM_WEIGHTS)
generation_best = []

print('The player: ' + playerName + ' starts!')
s.connect((host, port))
print('The player: ' + playerName + ' connected!')

if args.adversarial:
    print(f"Waiting to be assigned a player number . . .")
    data = receive(s)
    if data[0] != "P":
        raise Exception(f"Expected a player number. Got: {data}")
    else:
        player_num = int(data[1])
        print(f"I was assigned the number {player_num}")

generation = -1
prev_best = -9001
generations_without_improvement = 0
while True:
    generation += 1
    if generation != 0:
        # Sort the population based on fitness (we want to maximize fitness)
        population.sort(key=lambda i: i.fitness, reverse=True)
        print(f"Gen {generation} - Best in population: {population[0].fitness}. Weights = {population[0].utility_weights}")
        write_individuals_to_file(player_num, population[0:5], generation+1)
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
                player_points = [int(i) for i in data.split()[1:3]]
                game_values.append(player_points[player_num-1] - player_points[(player_num % 2 + 1)-1])
                print(f"Game {games_played+1} ended. (Player 1) {player_points[0]} - {player_points[1]} (Player 2) "
                      f"- I am player {player_num}")
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
                ################
                # if mancala_ai.game_state is not None:
                #     print("Board before updating:")
                #     mancala_ai.game_state.print_board()
                mancala_ai.update_state(board, playerTurn)
                # print("Board after updating:")
                # mancala_ai.game_state.print_board()
                move = str(mancala_ai.get_best_move())
                # print(f"Best move is:{move} (I am player {player_num})")

                ################
                send(s, move)

        # After 10 games are played, we evaluate the individual's fitness by
        # summing the game values (difference in points)
        individual.fitness = sum(game_values)
        individual.game_history = game_values
