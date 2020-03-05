# Spaghett carbonara a la Johannes and AT

import socket
import threading
import sys
import copy
from assignment_4 import GameState


port = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(('', port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

starting_player = 1
# playerTurn = 1
start_board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
game_state = GameState(copy.copy(start_board), starting_player)
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
    global game_state, connections, starting_player

    # If this thread handles the starting player, send the starting board to the player
    if starting_player == player:
        print("Starting game with player %s" % player)
        pt = str(game_state.player_turn)
        board = ''.join([('0' + str(i))[-2:] for i in game_state.board])
        data = pt + board
        send(conn, data)

    while True:
        # Receive a move
        data = receive(conn)
        print(f"Received data: {data} from player {player}")

        # If the data received was an acknowledge ("OK"), we know that the python player have
        # acknowledged that the previous game had ended and is ready to start a new game
        if data == "OK":
            game_state = GameState(copy.copy(start_board), starting_player)
            data = str(game_state.player_turn) + ''.join([('0' + str(i))[-2:] for i in game_state.board])
            print(f"Sending new game to player {starting_player}")
            send(connections[starting_player - 1], data)
            continue
        elif data == "QUIT":
            break

        # Get the requested move and translate it from 1-6 based to 0-13 indexed
        action = (int(data[0]) - 1) + 7*(player-1)

        print("Player %s wants to make action %s" % (player, action))
        print("Board before action:")
        game_state.print_board()
        # Perform the action
        game_state.move(action)
        print("Board after action:")
        game_state.print_board()

        if game_state.game_ended:
            print("\n--- Game ended. Starting a new game. ---\n")
            # Let the player the didn't go first go first the next time
            starting_player = (starting_player % 2) + 1

            # If this thread handles player 1 ...
            if player == 1:
                # ... it means that we received the last move from the bot
                # So we want to notify the python player that the game ended and what the final scores were
                data = "E " + str(game_state.board[6]) + " " + str(game_state.board[13])
                print("Sending end results to player 2")
                send(connections[1], data)
                continue

            # If this thread handles player 2 ...
            # if player == 2:
            #
            #     # we received from pythonplayer, we want to send something to the bot
            #     game_state = GameState(
            #         copy.copy(start_board), playerTurn)
            #     data = str(game_state.player_turn) + \
            #            ''.join([('0' + str(i))[-2:] for i in game_state.board])
            #     print("Sending new game to player 1")
            #     send(connections[0], data)
            #     continue

        pt = str(game_state.player_turn)
        board = ''.join([('0' + str(i))[-2:] for i in game_state.board])
        message = pt + board

        # Send the board and player turn to the player that this thread does NOT handle
        print(f"Sending message to player {game_state.player_turn}. Data: {message}")
        send(connections[game_state.player_turn-1], message)

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
