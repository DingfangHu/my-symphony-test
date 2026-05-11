"""2048 mini-game implementation.

A self-contained 2048 puzzle game module with a 4x4 grid. Supports
sliding tiles in four directions with merging when equal values collide.

Usage:
    game = Game2048()
    game.move('left')
    game.move('up')
    print(game)
    print(f'Score: {game.score}')
"""

import random


class Game2048:
    """Core 2048 game logic with a 4x4 grid.

    Tiles slide and merge according to the classic rules:
    - Two equal tiles merge into their sum.
    - A new tile (2 or 4) spawns after each valid move.
    - The player wins by creating a 2048 tile.
    - The game ends when no valid moves remain.
    """

    SIZE = 4
    WIN_VALUE = 2048

    def __init__(self, seed=None):
        """Initialize a new 2048 game with two starting tiles.

        Args:
            seed: Optional random seed for deterministic testing.
        """
        self.grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self.score = 0
        self.won = False
        self._over = False
        self._rng = random.Random(seed)
        self._add_random_tile()
        self._add_random_tile()

    def _empty_cells(self):
        """Return list of (row, col) tuples for cells with value 0."""
        return [
            (r, c)
            for r in range(self.SIZE)
            for c in range(self.SIZE)
            if self.grid[r][c] == 0
        ]

    def _add_random_tile(self):
        """Spawn a new tile: 2 with 90% probability, 4 with 10%."""
        empty = self._empty_cells()
        if not empty:
            return
        r, c = self._rng.choice(empty)
        self.grid[r][c] = 2 if self._rng.random() < 0.9 else 4

    @staticmethod
    def _slide_row_left(row):
        """Slide a row to the left and merge equal adjacent tiles.

        Args:
            row: A list of 4 integers representing one row.

        Returns:
            tuple: (new_row, points_gained, reached_win)
        """
        # Compact non-zero values
        compacted = [v for v in row if v != 0]
        merged = []
        points = 0
        reached_win = False
        i = 0
        while i < len(compacted):
            if i + 1 < len(compacted) and compacted[i] == compacted[i + 1]:
                merged_val = compacted[i] * 2
                merged.append(merged_val)
                points += merged_val
                if merged_val == Game2048.WIN_VALUE:
                    reached_win = True
                i += 2
            else:
                merged.append(compacted[i])
                i += 1
        # Pad with zeros to maintain row length
        return merged + [0] * (Game2048.SIZE - len(merged)), points, reached_win

    def _transform_for_direction(self, direction):
        """Apply pre-move grid transformation and return its inverse.

        The transformation maps the direction so that '_slide_row_left'
        handles the actual sliding for every direction.

        Args:
            direction: One of 'left', 'right', 'up', 'down'.

        Returns:
            callable: A function that reverses the transformation.
        """
        if direction == 'left':
            def undo():
                pass
            return undo
        elif direction == 'right':
            self._reverse_rows()
            def undo():
                self._reverse_rows()
            return undo
        elif direction == 'up':
            self._transpose()
            def undo():
                self._transpose()
            return undo
        elif direction == 'down':
            self._transpose()
            self._reverse_rows()
            def undo():
                self._reverse_rows()
                self._transpose()
            return undo
        else:
            raise ValueError(f"Unknown direction: {direction}")

    def _transpose(self):
        """Transpose the grid (swap rows and columns)."""
        self.grid = [list(col) for col in zip(*self.grid)]

    def _reverse_rows(self):
        """Reverse the order of elements in each row."""
        self.grid = [row[::-1] for row in self.grid]

    def move(self, direction):
        """Slide all tiles in the given direction.

        Args:
            direction: 'up', 'down', 'left', or 'right'.

        Returns:
            bool: True if the move changed the board, False otherwise.

        Raises:
            ValueError: If direction is not one of the four valid values.
        """
        if self._over:
            return False

        if direction not in ('up', 'down', 'left', 'right'):
            raise ValueError(
                f"Invalid direction '{direction}'. "
                f"Use 'up', 'down', 'left', or 'right'."
            )

        old_grid = [row[:] for row in self.grid]

        undo = self._transform_for_direction(direction)
        new_grid = []
        move_points = 0
        for row in self.grid:
            slid, pts, win_flag = self._slide_row_left(row)
            new_grid.append(slid)
            move_points += pts
            if win_flag:
                self.won = True
        self.grid = new_grid
        undo()
        self.score += move_points

        if self.grid != old_grid:
            self._add_random_tile()
            if not self._can_move():
                self._over = True
            return True
        return False

    def _can_move(self):
        """Check whether any valid move exists on the current board."""
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] == 0:
                    return True
                if c + 1 < self.SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r + 1 < self.SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    @property
    def is_over(self):
        """True when no further moves are possible."""
        return self._over

    def get_state(self):
        """Return the current game state as a dict.

        Returns:
            dict: Keys: 'grid' (4x4 list), 'score', 'won', 'is_over'.
        """
        return {
            'grid': [row[:] for row in self.grid],
            'score': self.score,
            'won': self.won,
            'is_over': self._over,
        }

    def __str__(self):
        """Pretty-print the board."""
        lines = []
        for row in self.grid:
            lines.append(
                ' '.join(f'{v:4d}' if v != 0 else '   .' for v in row)
            )
        return '\n'.join(lines)
