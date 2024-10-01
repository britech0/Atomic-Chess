class ChessVar:
    """Atomic Chess Game with methods for initialization, movement, game state handling, and visualizing the board."""

    def __init__(self):
        """Initializes the chess board, game state, and sets the current turn to white."""

        self._board = self.initialize_board()
        self._turn = "white"
        self._current_game_state = "UNFINISHED"
        self._columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self._columns_indexes = {col: x for x, col in enumerate(self._columns)}

    def initialize_board(self):
        """Initializes the board with pieces in standard chess starting positions."""

        board = [["." for _ in range(8)] for _ in range(8)]
        special_pieces = 'RNBQKBNR'

        for i, x in enumerate(special_pieces):
            board[0][i] = x.lower()
            board[1][i] = 'p'
            board[6][i] = 'P'
            board[7][i] = x
        return board

    def position_index(self, position):
        """Converts user input (e.g., 'e2') to board indices."""

        if len(position) != 2 or position[0] not in self._columns or not position[1].isdigit():
            return None, None

        col, row = position[0], position[1]
        col_index = self._columns_indexes[col]
        row_index = 8 - int(row)

        if not (0 <= col_index < 8 and 0 <= row_index < 8):
            return None, None

        return row_index, col_index

    def clear_path(self, from_position, to_position):
        """Checks if the path between two positions is clear (no pieces in the way)."""
        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        current_row, current_col = from_row + row_step, from_col + col_step

        while (current_row != to_row or current_col != to_col):
            if self._board[current_row][current_col] != '.':
                return False
            current_row += row_step
            current_col += col_step

        return True

    def pawn_move(self, from_row, from_col, to_row, to_col):
        """Handles pawn movement, including capturing diagonally."""
        piece = self._board[from_row][from_col]

        if piece.isupper():
            # White pawn
            direction = -1
            start_row = 6
            opponent_piece = lambda x: x.islower()
        else:
            # Black pawn
            direction = 1
            start_row = 1
            opponent_piece = lambda x: x.isupper()

        # Move forward
        if to_col == from_col:
            if to_row == from_row + direction and self._board[to_row][to_col] == '.':
                return True
            if from_row == start_row and to_row == from_row + 2 * direction and self._board[from_row + direction][to_col] == '.' and self._board[to_row][to_col] == '.':
                return True
        # Capture
        elif abs(to_col - from_col) == 1 and to_row == from_row + direction:
            if self._board[to_row][to_col] != '.' and opponent_piece(self._board[to_row][to_col]):
                return True

        return False

    def rook_move(self, from_position, to_position):
        """Handles rook movement."""
        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        if from_row == to_row or from_col == to_col:
            return self.clear_path(from_position, to_position)
        return False

    def knight_move(self, from_position, to_position):
        """Handles knight movement."""
        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)

        return (row_diff, col_diff) in [(2, 1), (1, 2)]

    def bishop_move(self, from_position, to_position):
        """Handles bishop movement."""
        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        if abs(to_row - from_row) == abs(to_col - from_col):
            return self.clear_path(from_position, to_position)
        return False

    def queen_move(self, from_position, to_position):
        """Handles queen movement."""
        return self.rook_move(from_position, to_position) or self.bishop_move(from_position, to_position)

    def king_move(self, from_position, to_position):
        """Handles king movement."""
        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

    def valid_move(self, from_position, to_position):
        """Checks if a move is valid."""

        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        if from_row is None or to_row is None:
            return False

        piece = self._board[from_row][from_col]
        target = self._board[to_row][to_col]

        if piece == '.':
            return False

        if (self._turn == 'white' and piece.islower()) or (self._turn == 'black' and piece.isupper()):
            return False

        if (self._turn == 'white' and target.isupper()) or (self._turn == 'black' and target.islower()):
            return False

        move_funcs = {
            'P': self.pawn_move,
            'R': self.rook_move,
            'N': self.knight_move,
            'B': self.bishop_move,
            'Q': self.queen_move,
            'K': self.king_move
        }

        piece_type = piece.upper()
        if piece_type in move_funcs:
            if piece_type == 'P':
                return move_funcs[piece_type](from_row, from_col, to_row, to_col)
            else:
                return move_funcs[piece_type](from_position, to_position)
        return False

    def move_piece(self, from_position, to_position):
        """Moves a piece on the board."""

        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)

        self._board[to_row][to_col] = self._board[from_row][from_col]
        self._board[from_row][from_col] = '.'

    def explode_capture(self, position):
        """Handles explosion in atomic chess."""

        row, col = self.position_index(position)

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self._board[r][c]
                    if piece != '.':
                        if piece.upper() == 'K':
                            self._current_game_state = 'BLACK_WON' if piece.islower() else 'WHITE_WON'
                        self._board[r][c] = '.'

    def make_move(self, from_position, to_position):


        if self._current_game_state != 'UNFINISHED':
            print("Game Over!")
            return False

        if not self.valid_move(from_position, to_position):
            print("Invalid move. Try again.")
            return False

        from_row, from_col = self.position_index(from_position)
        to_row, to_col = self.position_index(to_position)
        target_piece = self._board[to_row][to_col]
        moving_piece = self._board[from_row][from_col]

        self.move_piece(from_position, to_position)

        if target_piece != '.':
            # Explosion occurs; destroy pieces in 3x3 area
            self.explode_capture(to_position)
        else:
            # Handle pawn promotion
            if moving_piece.upper() == 'P':
                if (moving_piece.isupper() and to_row == 0) or (moving_piece.islower() and to_row == 7):
                    self._board[to_row][to_col] = 'Q' if moving_piece.isupper() else 'q'

        # Check win condition
        if not any('K' in row for row in self._board):
            self._current_game_state = 'BLACK_WON'
        elif not any('k' in row for row in self._board):
            self._current_game_state = 'WHITE_WON'

        if self._current_game_state == 'UNFINISHED':
            self._turn = 'black' if self._turn == 'white' else 'white'

        return True

    def get_game_state(self):
        """Returns the current game state."""

        return self._current_game_state


    def print_board(self):
        """Prints the board."""

        print('  a b c d e f g h')
        for row in range(8):
            row_str = str(8 - row) + ' '
            for col in range(8):
                row_str += self._board[row][col] + ' '
            print(row_str)
        print()

if __name__ == "__main__":
    game = ChessVar()
    while game.get_game_state() == 'UNFINISHED':
        game.print_board()
        print(f"{game._turn.capitalize()}'s turn.")
        from_pos = input("Enter the position of the piece you want to move (ex: e2): ").strip()
        to_pos = input("Enter the position to move to (ex: e4): ").strip()

        if not game.make_move(from_pos, to_pos):
            continue

    game.print_board()
    print("Game Over!")
    print(f"Result: {game.get_game_state()}")
