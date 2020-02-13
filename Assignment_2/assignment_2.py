import numpy as np
import time


def solve(sudoku):
    empty_square = sudoku.get_first_empty_square()
    if not empty_square:
        return True

    for i in range(1, 10):
        if sudoku.is_valid_value(i, empty_square):
            sudoku.set_value(i, empty_square)

            if solve(sudoku):
                return True
            else:
                sudoku.reset_value(empty_square)

    return False


class Sudoku:
    def __init__(self, id, board):
        self.id = id
        self.board = board
        # self.board_transposed = np.transpose(self.board)
        # self.latest_empty_square = (0, 0)  # x, y tuple

        # Lookup tables to make validity checks faster
        # (Note: Having 'valid_values' tables would probably be more efficient but I do not know
        # if that is allowed for the assignment)
        self.empty_squares = []  # x, y tuples
        self.invalid_values_row = [[] for _ in range(9)]
        self.invalid_values_col = [[] for _ in range(9)]
        self.invalid_values_box = [[] for _ in range(9)]
        self.initialize_lookup_tables()

    def initialize_lookup_tables(self):
        for y in range(9):
            for x in range(9):
                if self.board[y][x] == 0:
                    self.empty_squares.append((y,x))
                else:
                    self.invalid_values_col[x].append(self.board[y][x])
                    self.invalid_values_row[y].append(self.board[y][x])
                    self.invalid_values_box[(x // 3) + (y // 3) * 3].append(self.board[y][x])

    def print(self):
        print(" _________________________________ ")
        print("| Puzzle id: {}                    |".format(self.id))
        print("# # # # # # # # # # # # # # # # # #")
        for row in range(9):
            for i in range(9):
                if i == 0:
                    print("#  ", end="")
                print("{}  ".format(self.board[row][i]), end="")
                if (i+1) % 3 == 0 and i != 8:
                    print("  ", end="")
                if i == 8:
                    print("#")
            if (row+1) % 3 == 0 and row != 8:
                print("#                                 #")

        print("# # # # # # # # # # # # # # # # # #")

    def reset_value(self, pos):
        n = self.board[pos[0]][pos[1]]

        # Remove the value from the lookup tables
        # with suppress(ValueError):
        self.invalid_values_col[pos[1]].remove(n)
        # with suppress(ValueError):
        self.invalid_values_row[pos[0]].remove(n)
        # with suppress(ValueError):
        self.invalid_values_box[(pos[1] // 3) + (pos[0] // 3) * 3].remove(n)
        self.board[pos[0]][pos[1]] = 0
        self.empty_squares.insert(0, pos)

    def set_value(self, n, pos):
        self.board[pos[0]][pos[1]] = n
        # Update the lookup tables
        self.invalid_values_col[pos[1]].append(n)
        self.invalid_values_row[pos[0]].append(n)
        self.invalid_values_box[(pos[1] // 3) + (pos[0] // 3) * 3].append(n)
        self.empty_squares.pop(0)

    def is_valid_value(self, n, pos):
        box_index = pos[1] // 3 + ((pos[0] // 3) * 3)
        if n in self.invalid_values_row[pos[0]] or n in self.invalid_values_col[pos[1]] \
                or n in self.invalid_values_box[box_index]:
            return False
        return True

    def get_first_empty_square(self):
        if len(self.empty_squares):
            return self.empty_squares[0]
        else:
            return False



if __name__ == "__main__":
    # Read the data
    with open('Assignment 2 sudoku.txt') as f:
        read_data = f.read().splitlines()

    sudokus = []
    board = []
    id = None
    parse = False
    for l in read_data:
        if l.startswith("SUDOKU"):
            if len(board):
                sudokus.append(Sudoku(id, board.copy()))
            id = l[len(l)-1]
            board = []
            parse = True
            continue

        # Skip blank lines
        if len(l) < 2:
            parse = False

        if parse:
            row = [int(c) for c in l]
            board.append(row)

    t_start = time.time()
    for s in sudokus:
        solve(s)
    t_end = time.time()
    print("Solving 10 Sudoku puzzles")
    print("Elapsed time: {}\n".format(t_end - t_start))

    for s in sudokus:
        s.print()






