"""2048 mini-game implementation."""

import random


class Game2048:
    """2048 puzzle game implementation.

    A sliding tile puzzle where the player moves tiles on a grid.
    Tiles with the same value merge into one when they collide.
    The goal is to reach the 2048 tile.
    """

    def __init__(self, size=4):
        """Initialize a new game with the given board size.

        Args:
            size: Board dimension (must be >= 2).

        Raises:
            ValueError: If size is less than 2.
        """
        if size < 2:
            raise ValueError("Board size must be at least 2.")
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self._won = False
        self._spawn()
        self._spawn()

    def get_board(self):
        """Return a deep copy of the current board."""
        return [row[:] for row in self.board]

    def has_won(self):
        """Return True if a 2048 (or larger) tile has been created."""
        return self._won

    def is_game_over(self):
        """Return True if no valid moves remain."""
        return not self.can_move()

    def can_move(self):
        """Return True if at least one move is possible.

        A move is possible if there is an empty cell or adjacent
        equal tiles that can merge.
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return True
                if j + 1 < self.size and self.board[i][j] == self.board[i][j + 1]:
                    return True
                if i + 1 < self.size and self.board[i][j] == self.board[i + 1][j]:
                    return True
        return False

    def move(self, direction):
        """Slide all tiles in the given direction.

        Args:
            direction: One of 'left', 'right', 'up', 'down'.

        Returns:
            True if the board changed, False otherwise.

        Raises:
            ValueError: If direction is not valid.
        """
        if direction not in ('left', 'right', 'up', 'down'):
            raise ValueError(f"Invalid direction: {direction}")

        original = self.get_board()

        if direction == 'left':
            for i in range(self.size):
                self.board[i], gained = self._slide_row_with_score(self.board[i])
                self.score += gained
        elif direction == 'right':
            for i in range(self.size):
                reversed_row = self.board[i][::-1]
                new_row, gained = self._slide_row_with_score(reversed_row)
                self.board[i] = new_row[::-1]
                self.score += gained
        elif direction == 'up':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)]
                new_col, gained = self._slide_row_with_score(col)
                self.score += gained
                for i in range(self.size):
                    self.board[i][j] = new_col[i]
        elif direction == 'down':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)]
                reversed_col = col[::-1]
                new_col, gained = self._slide_row_with_score(reversed_col)
                new_col = new_col[::-1]
                self.score += gained
                for i in range(self.size):
                    self.board[i][j] = new_col[i]

        changed = self.board != original

        # Check for a new win
        if not self._won:
            for row in self.board:
                if any(cell >= 2048 for cell in row):
                    self._won = True
                    break

        if changed:
            self._spawn()

        return changed

    @staticmethod
    def _slide_row(row):
        """Slide a row to the left, merging equal adjacent tiles.

        This is a public static method for testing purposes.

        Args:
            row: List of tile values.

        Returns:
            The row after sliding left with merges.
        """
        return Game2048._slide_row_with_score(row)[0]

    @staticmethod
    def _slide_row_with_score(row):
        """Slide a row left, merging equal adjacent tiles, and return score gained.

        Args:
            row: List of tile values.

        Returns:
            A tuple of (new_row, score_gained).
        """
        non_zero = [x for x in row if x != 0]
        result = []
        score = 0
        skip = False
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged = non_zero[i] * 2
                result.append(merged)
                score += merged
                skip = True
            else:
                result.append(non_zero[i])
        result.extend([0] * (len(row) - len(result)))
        return result, score

    def _spawn(self):
        """Spawn a new tile (2 with 90% probability, 4 with 10%) in a random empty cell.

        Returns:
            True if a tile was spawned, False if the board is full.
        """
        empty_cells = [
            (i, j)
            for i in range(self.size)
            for j in range(self.size)
            if self.board[i][j] == 0
        ]
        if not empty_cells:
            return False
        i, j = random.choice(empty_cells)
        self.board[i][j] = 4 if random.random() < 0.1 else 2
        return True

    def __str__(self):
        """Return a string representation of the board.

        Non-zero cells show their value; empty cells show '.'.
        """
        lines = []
        for row in self.board:
            lines.append(' '.join(str(cell) if cell != 0 else '.' for cell in row))
        return '\n'.join(lines)
