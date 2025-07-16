class MegaTicTacToe:
    def __init__(self):
        self.boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.current_player = 'X'
    
    def make_move(self, board_index, cell_index, player):
        mini_board = self.boards[board_index]
        row, col = divmod(cell_index, 3)
        if mini_board[row][col] == '':
            mini_board[row][col] = player
            return True
        return False
