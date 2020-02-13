import numpy as np

class Sudoku:
    def __init__(self, id, board):
        self.id = id
        self.board = board
        self.board_transposed = np.transpose(self.board)
        self.latest_empty_square = {"x": 0, "y": 0}

    def get_first_empty_square(self):
        row_num_start = self.latest_empty_square // 9
        col_num_start = self.latest_empty_square % 9

        # Check if the next empty square is in the same row as the last one
        for x in range(self.latest_empty_square[0], 9):
            if board[x][self.latest_empty_square[1]] == 0:
                self.latest_empty_square[0] = x
                return self.latest_empty_square

        # If we didnt find the square in the same row, we need to loop all indices for the remaining rows
        for x in range(9):
            for y in range(self.latest_empty_square[1], 9):
                if board[x][y] == 0:
                    self.latest_empty_square





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

    print(sudokus)





