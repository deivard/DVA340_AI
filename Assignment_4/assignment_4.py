from math import inf, exp
import copy


class GameState:
    def __init__(self, board, player_turn):
        self.board = board
        self.prev_board = copy.copy(board)
        self.player_turn = player_turn
        self.game_ended = False
        self.winner = 0  # 0 == draw, 1 = player 1, 2 = player 2

    def calculate_winner(self):
        self.winner = 0 if self.board[6] == self.board[13] else 1 if self.board[6] > self.board[13] else 2
        return self.winner

    def get_available_moves(self, player_num=None):
        if player_num is None:
            player_num = self.player_turn
        return [i for i in range(7*(player_num-1), (7*player_num)-1) if self.board[i] != 0]

    def print_board(self):
        print("  ", end="")
        for i in range(12, 6, -1):
            print(self.board[i], end=" ")
        print(" <- Player 2", end="")
        print("\n" + str(self.board[13]) + "             " + str(self.board[6]) + "\n  ", end="")
        for i in range(6):
            print(self.board[i], end=" ")
        print(" <- Player 1", end="")
        print("")

    def opposite_player(self, num=None):
        if num is None:
            num = self.player_turn
        return (num + 1) % 3 + num - 1

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
            self.final_capture()
            return True
        # # Check condition 2
        # elif self.board[6] > 24 or self.board[13] > 24:
        #     return True
        else:
            return False

    def move(self, pit):
        self.prev_board = copy.copy(self.board)
        # print(f"Player {self.player_turn}s turn.")
        ending_pit = None
        seeds = self.board[pit]
        self.board[pit] = 0
        i = 1
        while seeds > 0:
            if (pit+i) % 14 != self.mancala_index(self.opposite_player()):
                self.board[(pit+i) % 14] += 1
                seeds -= 1
                ending_pit = (pit+i) % 14
            # else:
            #     print(f"{(pit+i) % 14} is not player {self.player_turn}s Mancala")
            i += 1

        # Check if the ending pit belongs to the current player and if the pit was empty
        # when the last seed was placed in it.
        if self.pit_player(ending_pit) == self.player_turn and self.board[ending_pit] == 1 and\
                self.board[self.opposite_pit(ending_pit)] > 0 and ending_pit != 13 and ending_pit != 6:
            self.capture(ending_pit)

        # Check if we ended in our own Mancala, and let it be the next player's turn if we didn't
        if ending_pit != self.mancala_index(self.player_turn):
            # print("Next player's turn.")
            self.player_turn = self.opposite_player()

        if self.end_state_reached() or ending_pit is None:
            self.game_ended = True
            self.calculate_winner()
            # # If condition ii is reached, steal all seeds still left on the board,
            # # this is to reward quick wins more than slow one
            # if self.winner != 0:
            #     self.board[self.mancala_index(self.winner)] += sum(self.board[0:6]) + sum(self.board[7:13])

    def final_capture(self):
        """
        Each player captures all seeds on his/her side. This only happens when an end state is reached.
        """
        # Calculate score on each side and add to the corresponding pit
        self.board[6] += sum(self.board[0:6])
        self.board[13] += sum(self.board[7:13])
        # Empty the pits
        for i in list(range(6)) + list(range(7,13)):
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

        return (pit + (steps_to_mancala*2)) % 14  # 14 is len(self.board)

    def capture(self, pit):
        """
        :param pit: The index of the pit that is captured.
        """
        # Add the scores of the captured pit and the opposite of that pit (which is the pit that enabled
        # the capture, it will contain 1 point) to the player's Mancala
        self.board[self.mancala_index(self.player_turn)] += self.board[pit] + self.board[self.opposite_pit(pit)]
        self.board[pit] = 0
        self.board[self.opposite_pit(pit)] = 0


class MancalaAI:
    def __init__(self, player_num=2, utility_weights=None, game_state=None):
        if utility_weights is None or len(utility_weights) == 0:
            utility_weights = [
                # Utility weights arrays in "performance" order
                [1.795, -4.306, -0.169, -10.032, -5.039, -8.94, -2.98, -6.314, -0.714, 0.909, 0],  # Strong vs player 5
                [-0.218, -1.291, 0, 0, 0, 1.595, 0, 0, -3.013, 0, 1.14],  # Strong vs player 4
                [9.615, -14.415, -9.538, -1.696, 8.207, 0.299, 3.29, -10.084, 5.552, 1.545, -4.488]  # Strong vs player 3

            ]
        # If the weights isn't a list of lists, we just convert it to a list of losing_streak.
        elif not isinstance(utility_weights[0], list):
            utility_weights = [utility_weights]

        self.utility_weights = utility_weights
        self.current_weights_index = 0
        self.player_num = player_num
        self.game_state = game_state
        self.games_played = 0
        self.games_lost = 0
        self.losing_streak = 0

    def set_utility_weights(self, weights):
        if not isinstance(weights[0], list):
            weights = [weights]
        self.utility_weights = weights

    def update_state(self, board, player_turn):
        if self.game_state is None:
            self.game_state = GameState(board, player_turn)
        else:
            self.game_state.board = board
            self.game_state.player_turn = player_turn
            if self.game_state.board == [4,4,4,4,4,4,0,4,4,4,4,4,4,0]:
                print("Setting game state ended to false.")
                self.game_state.game_ended = False
                self.game_state.winner = -1

    def heuristic(self, game_state):
        """
        H1 = How far ahead of opponent I am
        # H2 = How close I am to winning
        # H3 = How close opponent is to winning
        # H4 = Number of stones close to my Mancala
        # H5 = Number of stones far away from my Mancala
        # H6 = Number of stones in middle of board (neither far nor close)
        H7 = Number of empty pits on my side
        # H8 = Number of empty pits on opponent side
        H9 = Number of stones on my side
        H10 = Number of stones on opponent's side
        # H11 = Last pit empty
        H12 = I won
        H13 = I lost
        # H14 = Game ended with a draw
        H15 = I got another turn
        H16 = Number of pits that can give me an extra turn by landing in my Mancala
        H17 = Number of pits that can give the opponent an extra turn by landing in his Mancala
        H18 = Number of pits that can give me a capture
        # H19 = Number of pits that can give opponent a capture
        H20 = Number of points I got from the move
        """
        my_mancala_index = GameState.mancala_index(self.player_num)
        opposite_player = game_state.opposite_player(self.player_num)
        opponent_mancala_index = GameState.mancala_index(opposite_player)

        H1 = game_state.board[my_mancala_index] - game_state.board[opponent_mancala_index]
        # H2 = game_state.board[my_mancala_index] - 24
        # H3 = game_state.board[opponent_mancala_index] - 24
        # H4 = sum(game_state.board[my_mancala_index-2:my_mancala_index])
        # H5 = sum(game_state.board[my_mancala_index-6:my_mancala_index-4])
        # H6 = sum(game_state.board[my_mancala_index-4:my_mancala_index-2])
        H7 = len([p for p in game_state.board[my_mancala_index-6:my_mancala_index] if p == 0])
        # H8 = len([p for p in game_state.board[opponent_mancala_index-6:opponent_mancala_index] if p == 0])
        H9 = sum(game_state.board[my_mancala_index-6:my_mancala_index])
        H10 = sum(game_state.board[opponent_mancala_index-6:opponent_mancala_index])
        # H11 = int(game_state.board[my_mancala_index] == 0)
        H12 = int(game_state.game_ended and game_state.winner == self.player_num)
        H13 = int(game_state.game_ended and game_state.winner != self.player_num)
        # H14 = int(game_state.game_ended and game_state.winner == 0)
        H15 = int(game_state.player_turn == self.player_num)
        H16 = sum([1 for m in game_state.get_available_moves(self.player_num) if (m+game_state.board[m] == my_mancala_index)])
        H17 = sum([1 for m in game_state.get_available_moves(opposite_player) if (m+game_state.board[m] == opponent_mancala_index)])
        H18 = sum([1 for m in game_state.get_available_moves(self.player_num) if game_state.board[(m+game_state.board[m])%14] == 0 and (m+game_state.board[m]%14) < my_mancala_index])
        # H19 = sum([1 for m in game_state.get_available_moves(opposite_player) if game_state.board[(m+game_state.board[m])%14] == 0 and my_mancala_index < (m+game_state.board[m]%14) < opponent_mancala_index])
        H20 = game_state.board[my_mancala_index] - game_state.prev_board[my_mancala_index]

        # heuristics = [H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11, H12, H13, H14, H15, H16, H17, H18, H19]
        # heuristics = [H1, H2, H3, H4, H7]
        heuristics = [H1, H7, H9, H10, H12, H13, H15, H16, H17, H18, H20]

        h_min = min(heuristics)
        h_max = max(heuristics)
        # Normalize data
        heuristics = [(H_i - h_min) / (h_max - h_min) for H_i in heuristics]

        # If we dont have enough weights (for some reason), add default weights of 0 to
        # the weights list until it is the same length as the heuristics list.
        for i in range(len(heuristics) - len(self.utility_weights[self.current_weights_index])):
            self.utility_weights.append(0)

        # print([h*w for h, w in zip(heuristics, self.utility_weights)])
        return sum([h*w for h, w in zip(heuristics, self.utility_weights[self.current_weights_index])])

    def my_score(self):
        return self.game_state.board[GameState.mancala_index(self.player_num)]

    def opponent_score(self):
        return self.game_state.board[GameState.mancala_index(self.game_state.opposite_player(self.player_num))]

    def guess_who_won(self):
        # This will be true if the AI was the last player that played before the game ended.
        # If that's the case, it would mean that we already know who won
        # (since the AI should have calculatead it already).
        if self.game_state.game_ended:
            return self.game_state.winner

        # If the AI wasn't the last player it would mean that the game ended on opponents turn.
        # Then we need to check what the best move for the opponent would be.
        else:
            # Store the actual board for later restoration
            actual_board = copy.copy(self.game_state.board)
            self.game_state.board = self.game_state.prev_board
            # This should now get (and perform) the best move for current player
            self.get_best_move()
            # If our predicted move was correct, we should have a winner calculated for us
            if self.game_state.winner != -1:
                self.game_state.board = actual_board
                return self.game_state.winner
            # If not, we need to calculate the winner manually based on the current sate of the board.
            # This means that the "guess" will not be as accurate and the winner is based on who currently has
            # the most score.
            else:
                # Base the winner of the "final capture" since we cant know what heuristics the opponent is using
                self.game_state.final_capture()
                self.game_state.calculate_winner()
                self.game_state.board = actual_board
                return self.game_state.winner

    def is_new_game(self):
        # This will be true if the AI was the last player that played before the game ended
        if self.game_state.game_ended:
            return True
        # If the AI wasn't the last player, we need to see if this is a new board, which would mean that the game ended on his turn
        elif self.game_state.board == [4,4,4,4,4,4,0,4,4,4,4,4,4,0] and self.game_state.prev_board != [4,4,4,4,4,4,0,4,4,4,4,4,4,0]:
            return True
        return False

    def fine_tune_weights(self):
        # Guess the winner, so we can keep track of how well the weights perform
        winner = self.guess_who_won()
        print(f"I guess that player {winner} won")
        self.game_state.game_ended = False
        if winner != self.player_num:
            self.games_lost += 1
            self.losing_streak += 1
            # If we lost, and the opponent is using a "simple" AI, it means that we would lose 50% of the time.
            # So we need to change the weights to introduce variation
            self.current_weights_index = (self.current_weights_index + 1) % len(self.utility_weights)
            # print(f"Switching to weights {self.current_weights_index}: {self.utility_weights[self.current_weights_index]}")
        else:
            self.losing_streak = 0

    def get_best_move(self):
        print(f"Current weights: {self.utility_weights[self.current_weights_index]}")
        # Check if it is a new game after someone has won
        if self.is_new_game():
            self.games_played += 1
            self.fine_tune_weights()
            # print(f"I am player {self.player_num}. It is currently player {self.game_state.player_turn}'s turn.")
        possible_moves = self.game_state.get_available_moves()
        # self.game_state.print_board()
        # print(possible_moves)
        move_evals = []
        max_eval = -inf
        best_move = None
        for m in possible_moves:
            new_state = copy.deepcopy(self.game_state)
            new_state.move(m)
            eval_ = self.minimax(new_state, 2, -inf, inf, True)
            # print(f"Heuristic: {eval_}")
            move_evals.append((m, eval_))
            if eval_ > max_eval:
                max_eval = eval_
                best_move = m

        # Perform the move, so the game_state is up to date (so we can track if we won easier)
        # (This actually don't belong here but here we are...)
        self.game_state.move(best_move)
        # print(f"Choose {best_move}")
        # print(move_evals)
        # Translate the best move to a 1-6 index, so it works with the server
        best_move = (best_move+1) % 7
        # if best_move > 6:
        #     best_move -= 7
        # best_move += 1

        return best_move

    def move(self):
        pass

    def minimax(self, game_state, depth, alpha, beta, maximize):
        if depth == 0 or game_state.game_ended:
            return self.heuristic(game_state)

        if maximize:
            max_eval = -inf
            for m in game_state.get_available_moves():
                new_state = copy.deepcopy(game_state)
                new_state.move(m)
                eval_ = self.minimax(new_state, depth-1, alpha, beta, new_state.player_turn == self.player_num)
                max_eval = max(max_eval, eval_)
                alpha = max(alpha, eval_)
                # Pruning
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = inf
            for m in game_state.get_available_moves():
                new_state = copy.deepcopy(game_state)
                new_state.move(m)
                eval_ = self.minimax(new_state, depth-1, alpha, beta, new_state.player_turn == self.player_num)
                min_eval = min(min_eval, eval_)
                beta = min(beta, eval_)
                # Pruning
                if beta <= alpha:
                    break
            return min_eval






