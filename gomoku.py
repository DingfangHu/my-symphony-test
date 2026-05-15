"""Gomoku (five-in-a-row) mini-game: human vs computer."""


class Gomoku:
    """Human-vs-computer Gomoku game.

    Played on a 15x15 board. The human plays 'X' (first) and the
    computer plays 'O'. The first player to get five in a row
    horizontally, vertically, or diagonally wins.
    """

    def __init__(self, size=15):
        """Initialize a new game with the given board size.

        Args:
            size: Board dimension (must be >= 5).

        Raises:
            ValueError: If size is less than 5.
        """
        if size < 5:
            raise ValueError("Board size must be at least 5 for Gomoku.")
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self._current_player = 'X'  # Human starts
        self._winner = None
        self._game_over = False
        self._move_count = 0

    def get_board(self):
        """Return a deep copy of the current board."""
        return [row[:] for row in self.board]

    @property
    def current_player(self):
        """Return the player whose turn it is ('X' or 'O')."""
        return self._current_player

    @property
    def winner(self):
        """Return the winner ('X', 'O', or None if not yet decided)."""
        return self._winner

    @property
    def is_game_over(self):
        """Return True if the game has ended."""
        return self._game_over

    @property
    def move_count(self):
        """Return the number of moves played so far."""
        return self._move_count

    def is_valid_move(self, row, col):
        """Check if placing a piece at (row, col) is legal.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            True if the cell is within bounds and empty.
        """
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        return self.board[row][col] == ''

    def place_piece(self, row, col):
        """Human places a piece at (row, col).

        The human always plays 'X'. After the human move, the computer
        automatically responds with a move.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            tuple: (valid, state, comp_row, comp_col) where
                valid is True if the human move was accepted;
                state is 'ongoing', 'human_wins', 'computer_wins', or 'draw';
                comp_row, comp_col are the computer's reply (or None, None).
        """
        if self._game_over:
            return (False, 'ongoing', None, None)

        if not self.is_valid_move(row, col):
            return (False, 'ongoing', None, None)

        # Place human piece
        self.board[row][col] = 'X'
        self._move_count += 1

        # Check for human win
        if self._check_win(row, col, 'X'):
            self._winner = 'X'
            self._game_over = True
            return (True, 'human_wins', None, None)

        # Check for draw (board full)
        if self._is_board_full():
            self._game_over = True
            return (True, 'draw', None, None)

        # Computer moves
        comp_row, comp_col, comp_state = self._computer_move()

        return (True, comp_state, comp_row, comp_col)

    def place_piece_human_only(self, row, col):
        """Place a human piece without triggering computer response.

        Useful for testing and for setting up board positions.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            True if the move was valid, False otherwise.
        """
        if self._game_over:
            return False
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = 'X'
        self._move_count += 1
        if self._check_win(row, col, 'X'):
            self._winner = 'X'
            self._game_over = True
        elif self._is_board_full():
            self._game_over = True
        return True

    def place_computer_piece_only(self, row, col):
        """Place a computer piece without other logic.

        Useful for testing and for setting up board positions.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            True if the move was valid, False otherwise.
        """
        if self._game_over:
            return False
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = 'O'
        self._move_count += 1
        if self._check_win(row, col, 'O'):
            self._winner = 'O'
            self._game_over = True
        elif self._is_board_full():
            self._game_over = True
        return True

    # ------------------------------------------------------------------
    # Win detection
    # ------------------------------------------------------------------

    def _check_win(self, row, col, player):
        """Check if player has five in a row through (row, col).

        Args:
            row: Row of the last placed piece.
            col: Column of the last placed piece.
            player: 'X' or 'O'.

        Returns:
            True if the player has five or more in a row.
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Positive direction
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            # Negative direction
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def check_win_at(self, row, col, player):
        """Public wrapper for testing: check if player wins through (row, col)."""
        return self._check_win(row, col, player)

    # ------------------------------------------------------------------
    # Board state helpers
    # ------------------------------------------------------------------

    def _is_board_full(self):
        """Return True if no empty cells remain."""
        for row in self.board:
            if '' in row:
                return False
        return True

    # ------------------------------------------------------------------
    # Computer AI
    # ------------------------------------------------------------------

    def _computer_move(self):
        """Compute and execute the computer's move.

        Strategy (in priority order):
          1. Win immediately if possible.
          2. Block human from winning.
          3. Choose the best cell using a pattern-based heuristic.

        Returns:
            tuple: (row, col, state) where state is 'ongoing',
                   'computer_wins', or 'draw'.
        """
        size = self.size
        board = self.board

        # --- Pass 1: can the computer win in one move? ---
        for r in range(size):
            for c in range(size):
                if board[r][c] == '':
                    board[r][c] = 'O'
                    if self._check_win(r, c, 'O'):
                        self._move_count += 1
                        self._winner = 'O'
                        self._game_over = True
                        return (r, c, 'computer_wins')
                    board[r][c] = ''

        # --- Pass 2: must block human win? ---
        for r in range(size):
            for c in range(size):
                if board[r][c] == '':
                    board[r][c] = 'X'
                    if self._check_win(r, c, 'X'):
                        board[r][c] = 'O'
                        self._move_count += 1
                        return (r, c, 'ongoing')
                    board[r][c] = ''

        # --- Pass 3: heuristic evaluation ---
        best_score = -1
        best_r, best_c = -1, -1
        center = size // 2

        for r in range(size):
            for c in range(size):
                if board[r][c] == '':
                    off = self._score_cell(r, c, 'O')
                    defe = self._score_cell(r, c, 'X')
                    # Slight distance-from-centre bonus for tie-breaking
                    dist = abs(r - center) + abs(c - center)
                    score = off * 1.1 + defe - dist * 0.001

                    if score > best_score:
                        best_score = score
                        best_r, best_c = r, c

        if best_r >= 0:
            board[best_r][best_c] = 'O'
            self._move_count += 1
            if self._is_board_full():
                self._game_over = True
                return (best_r, best_c, 'draw')
            return (best_r, best_c, 'ongoing')

        # Board full
        self._game_over = True
        return (-1, -1, 'draw')

    # ------------------------------------------------------------------
    # Heuristic scoring
    # ------------------------------------------------------------------

    # Score values for different pattern strengths
    _SCORES = {
        'FIVE':         100000,
        'OPEN_FOUR':     10000,
        'BLOCKED_FOUR':   1000,
        'OPEN_THREE':     1000,
        'BLOCKED_THREE':   100,
        'OPEN_TWO':        100,
        'BLOCKED_TWO':      10,
        'OPEN_ONE':         10,
        'BLOCKED_ONE':       1,
    }

    def _score_cell(self, row, col, player):
        """Return a heuristic score for placing *player* at *(row, col)*.

        The score sums up pattern strengths in all four directions.
        """
        total = 0
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            total += self._score_direction(row, col, dr, dc, player)
        return total

    def _score_direction(self, row, col, dr, dc, player):
        """Score the line through (row,col) in direction (dr,dc) for player.

        Pretends a piece of *player* is at (row, col) and counts
        consecutive friendly pieces and open ends on both sides.
        """
        count = 1   # the hypothetical piece
        open_ends = 0

        # Positive direction
        for i in range(1, 5):
            r = row + dr * i
            c = col + dc * i
            if 0 <= r < self.size and 0 <= c < self.size:
                cell = self.board[r][c]
                if cell == player:
                    count += 1
                elif cell == '':
                    open_ends += 1
                    break
                else:
                    break  # blocked by opponent
            else:
                break  # blocked by wall

        # Negative direction
        for i in range(1, 5):
            r = row - dr * i
            c = col - dc * i
            if 0 <= r < self.size and 0 <= c < self.size:
                cell = self.board[r][c]
                if cell == player:
                    count += 1
                elif cell == '':
                    open_ends += 1
                    break
                else:
                    break
            else:
                break

        return self._pattern_score(count, open_ends)

    @staticmethod
    def _pattern_score(count, open_ends):
        """Convert (consecutive_count, open_ends) to a numeric score.

        This is a static method to allow direct testing of the pattern
        scoring logic without instantiating a full game.
        """
        if count >= 5:
            return 100000
        if count == 4:
            if open_ends == 2:
                return 10000
            if open_ends == 1:
                return 1000
            return 0
        if count == 3:
            if open_ends == 2:
                return 1000
            if open_ends == 1:
                return 100
            return 0
        if count == 2:
            if open_ends == 2:
                return 100
            if open_ends == 1:
                return 10
            return 0
        if count == 1:
            if open_ends == 2:
                return 10
            if open_ends == 1:
                return 1
            return 0
        return 0

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self):
        """Return a string representation of the board.

        Empty cells are shown as '.', human pieces as 'X',
        computer pieces as 'O'.
        """
        lines = []
        for row in self.board:
            lines.append(' '.join(cell if cell else '.' for cell in row))
        return '\n'.join(lines)
