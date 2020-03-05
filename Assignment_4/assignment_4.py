

class GameState:
    def __init__(self, board, player_turn):
        self.board = board
        self.player_turn = player_turn
        self.game_ended = False
        self.winner = 0  # 0 == draw, 1 = player 1, 2 = player 2

    def calculate_winner(self):
        self.winner = 0 if self.board[6] == self.board[13] else 1 if self.board[6] > self.board[13] else 2
        return self.winner

    def get_available_moves(self):
        return [i for i in self.board[7*(self.player_turn-1):6*(self.player_turn-1)] if self.board[i] != 0]

    def print_board(self):
       print("  ", end="")
       for i in range(12,6,-1):
          print(self.board[i], end=" ")
       print("\n" + str(self.board[13]) + "          " + str(self.board[6]) + "\n   ")
       for i in range(6):
          print(self.board[i], end=" ")
       print("\n")

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
            return True
        # Check condition 2
        elif self.board[6] > 24 or self.board[13] > 24:
            return True
        else:
            return False

    def move(self, pit):
        ending_pit = None
        i = 0
        while self.board[pit] > 0:
            if (pit+i) % 14 != self.mancala_index(self.opposite_player()):
                self.board[(pit+i) % 14] += 1
                self.board[pit] -= 1
                ending_pit = (pit+i) % 14
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
    def __init__(self, player_num, game_state, utility_weights):
        self.utility_weights = utility_weights
        self.player_num = player_num
        self.game_state = game_state


    def heuristic(self):
        """
        H0 = First valid move
        H1 = How far ahead of opponent I am
        H2 = How close I am to winning
        H3 = How close opponent is to winning
        H4 = Number of stones close to my Mancala
        H5 = Number of stones far away from my Mancala
        H6 = Number of stones in middle of board (neither far nor close)
        H7 = Number of empty pits on my side
        H8 = Number of empty pits on opponent side
        H9 = Last pit empty
        """
        my_mancala_index = GameState.mancala_index(self.player_num)
        opponent_mancala_index = GameState.mancala_index(self.game_state.opposite_player(self.player_num))

        H1 = self.my_score() - self.opponent_score()
        H2 = 48 - self.my_score()
        H3 = 48 - self.opponent_score()
        H4 = sum(self.game_state.board[my_mancala_index-2:my_mancala_index])
        H5 = sum(self.game_state.board[my_mancala_index-6:my_mancala_index-4])
        H6 = sum(self.game_state.board[my_mancala_index-4:my_mancala_index-2])
        H7 = len([p for p in self.game_state.board[my_mancala_index-6:my_mancala_index] if p == 0])
        H8 = len([p for p in self.game_state.board[opponent_mancala_index-6:opponent_mancala_index] if p == 0])
        H9 = int(self.game_state.board[my_mancala_index] == 0)

        pass

    def my_score(self):
        return self.game_state.board[GameState.mancala_index(self.player_num)]

    def opponent_score(self):
        return self.game_state.board[GameState.mancala_index(self.game_state.opposite_player(self.player_num))]

    def get_best_move(self):
        pass

    def possible_moves(self):
        return self.game_state.get_available_moves()

    def move(self):
        pass



