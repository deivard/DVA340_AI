import socket
import threading
import sys
import copy


class GameState:
    def __init__(self, board, player_turn):
        self.board = board
        self.player_turn = player_turn
        self.game_ended = False
        self.winner = 0  # 0 == draw, 1 = player 1, 2 = player 2

    def print_board(self):
        print("   ", end="")
        for i in range(12, 6, -1):
            print(self.board[i], end=" ")
        print("\n" + str(self.board[13]) + "             " + str(self.board[6]) + "    ")
        for i in range(6):
            print(self.board[i], end=" ")
        print("\n")

    def calculate_winner(self):
        self.winner = 0 if self.board[6] == self.board[13] else 1 if self.board[6] > self.board[13] else 2
        return self.winner

    def opposite_player(self):
        return (self.player_turn + 1) % 3 + self.player_turn - 1

    def get_available_moves(self):
        return [i + (self.player_turn - 1) * 7 for i in range(6) if self.board[i + (self.player_turn - 1) * 7]]

    def end_state_reached(self):
        """
        Check the board to see if an end state have been reached.
        The end states are:
        i) A player has no more seeds on his/her side
        ii) A player have more than 24 seeds in his/her Mancala
        :return: True or False dictating whether an end state has been reached or not
        """
        # Check condition 1
        if sum(self.board[0:6]) == 0 or sum(self.board[7:13]) == 0:
            return True
        # Check condition 2
        elif self.board[6] > 24 or self.board[13] > 24:
            return True
        else:
            return False

    def move(self, pit):
        ending_pit = None
        seeds_to_move = self.board[pit]
        self.board[pit] = 0
        i = 0
        while seeds_to_move > 0:
            current_pit = (pit + i) % 14
            if current_pit != self.mancala_index(self.opposite_player()):
                self.board[current_pit] += 1
                ending_pit = current_pit
            i += 1

        # Check if the ending pit belongs to the current player and if the pit was empty
        # when the last seed was placed in it.
        if self.pit_player(ending_pit) == self.player_turn and self.board[ending_pit] == 1:
            self.capture(ending_pit)

        # Check if we ended in our own Mancala, and let it be the next player's turn if we didn't
        if ending_pit != self.mancala_index(self.player_turn):
            self.player_turn = self.opposite_player()

        if self.end_state_reached() or ending_pit is None:
            self.game_ended = True
            self.final_capture()
            self.calculate_winner()

    def final_capture(self):
        """
        Each player captures all seeds on his/her side. This only happens when an end state is reached.
        """
        # Calculate score on each side and add to the corresponding pit
        self.board[6] += sum(self.board[0:6])
        self.board[13] += sum(self.board[7:13])
        # Empty the pits
        for i in list(range(6)) + list(range(7, 13)):
            self.board[i] = 0

    @staticmethod
    def pit_player(pit):
        """
        :param pit: A pit index on the Mancala board. Must be in the range [0,6] or [7,12].
        :return: The player id which the pit belongs to. A value in {1,2}.
        """
        return int(pit > 6) + 1

    @staticmethod
    def mancala_index(player):
        """
        :param player: The player id of the Mancala we want the index of.
        :return: The index of the Mancala belonging to the player.
        """
        return player * 6 + player - 1

    def opposite_pit(self, pit):
        steps_to_mancala = self.mancala_index(self.pit_player(pit)) - pit

        return (pit + (steps_to_mancala * 2)) % 14  # 14 is len(self.board)

    def capture(self, pit):
        """
        :param pit: The index of the pit that is captured.
        """
        # Add the scores of the captured pit and the opposite of that pit (which is the pit that enabled
        # the capture, it will contain 1 point) to the player's Mancala
        self.board[self.mancala_index(
            self.player_turn)] += self.board[pit] + self.board[self.opposite_pit(pit)]
        self.board[pit] = 0
        self.board[self.opposite_pit(pit)] = 0


port = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(('', port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

starting_player = 0
playerTurn = 1
start_board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
game_state = GameState(copy.copy(start_board), playerTurn)
connections = []


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


def threaded_client(conn, player):
    global playerTurn, game_state, connections, starting_player

    if starting_player + 1 == player:
        print("Starting game with player %s" % player)
        pt = str(game_state.player_turn)
        b = ''.join([('0' + str(i))[-2:] for i in game_state.board])
        data = pt + b
        send(conn, data)

    while True:
        # Receive move
        data = receive(conn)
        print(f"Received data: {data} from player {player}")

        if data == "OK":
            game_state = GameState(copy.copy(start_board), playerTurn)
            data = str(game_state.player_turn) + \
                   ''.join([('0' + str(i))[-2:] for i in game_state.board])
            print(f"Sending new game to player {player}")
            send(connections[playerTurn - 1], data)
            continue
        elif data == "QUIT":
            break

        move = int(data[0]) - 1
        action = move if player == 1 else move + 7

        print("Player %s wants to make action %s" % (player, action))
        # Make move
        game_state.move(action)
        game_state.print_board()

        if game_state.game_ended:
            print("\n--- Starting new game ---\n")

            if playerTurn == 1:
                playerTurn = 2
            else:
                playerTurn = 1

            if player == 1:
                # we received from bot, we want to send to pythonplayer
                data = "E " + \
                       str(game_state.board[6]) + \
                       " " + str(game_state.board[13])
                print("Sending end results to player 2")
                send(connections[1], data)
                continue
            if player == 2:
                # we received from pythonplayer, we want to send something to the bot
                game_state = GameState(
                    copy.copy(start_board), playerTurn)
                data = str(game_state.player_turn) + \
                       ''.join([('0' + str(i))[-2:] for i in game_state.board])
                print("Sending new game to player 1")
                send(connections[0], data)
                continue
                # send E points points

        pt = str(game_state.player_turn)
        b = ''.join([('0' + str(i))[-2:] for i in game_state.board])
        reply = pt + b

        if player == 1:
            print(f"Sent to player 2. Data: {reply}")
            send(connections[1], reply)
        elif player == 2:
            print(f"Sent to player 1. Data: {reply}")
            send(connections[0], reply)

    print("Lost connection")
    conn.close()


totalPlayers = 0
threads = []
while totalPlayers < 2:
    conn, addr = s.accept()
    connections.append(conn)
    print("Connected to:", addr)
    totalPlayers += 1

    x = threading.Thread(target=threaded_client, args=(conn, totalPlayers))

    threads.append(x)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("All threads finished. Exiting")
