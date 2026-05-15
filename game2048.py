"""2048 mini-game implementation.

A simple, self-contained 2048 game with no external dependencies.
"""

import random


class Game2048:
    """Core logic for a 2048 puzzle game.

    The game is played on a square grid. Tiles slide and merge when the player
    moves in one of four directions. After each valid move a new tile (2 or 4)
    appears in a random empty cell. The goal is to create a tile with value 2048.
    """

    def __init__(self, size=4):
        if size < 2:
            raise ValueError("Board size must be at least 2")
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.won = False
        self._spawn()
        self._spawn()

    def _spawn(self):
        """Spawn a new tile (2 or 4) in a random empty cell.

        Returns:
            bool: True if a tile was spawned, False if the board is full.
        """
        empty = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.board[r][c] == 0
        ]
        if not empty:
            return False
        r, c = random.choice(empty)
        self.board[r][c] = 4 if random.random() < 0.1 else 2
        return True

    @staticmethod
    def _slide_row(row):
        """Slide and merge a single row to the left.

        Args:
            row: A list of integers representing one row of the board.

        Returns:
            list: The row after sliding and merging to the left.
        """
        non_zero = [x for x in row if x != 0]
        merged = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged.append(non_zero[i] * 2)
                i += 2
            else:
                merged.append(non_zero[i])
                i += 1
        return merged + [0] * (len(row) - len(merged))

    def move(self, direction):
        """Move all tiles in the given direction.

        Tiles slide as far as possible in the given direction.  Adjacent tiles
        of equal value merge into a tile with double the value (scored).  After
        each successful move a new tile is spawned.

        Args:
            direction: One of 'up', 'down', 'left', 'right'.

        Returns:
            bool: True if the move changed the board, False otherwise.

        Raises:
            ValueError: If direction is not one of the four valid values.
        """
        if direction not in ('up', 'down', 'left', 'right'):
            raise ValueError(
                f"Invalid direction '{direction}'. "
                f"Use 'up', 'down', 'left', or 'right'."
            )

        original = [row[:] for row in self.board]

        if direction == 'left':
            for r in range(self.size):
                self.board[r] = self._slide_row(self.board[r])

        elif direction == 'right':
            for r in range(self.size):
                self.board[r] = self._slide_row(
                    self.board[r][::-1]
                )[::-1]

        elif direction == 'up':
            for c in range(self.size):
                col = self._slide_row(
                    [self.board[r][c] for r in range(self.size)]
                )
                for r in range(self.size):
                    self.board[r][c] = col[r]

        elif direction == 'down':
            for c in range(self.size):
                col = self._slide_row(
                    [self.board[r][c] for r in range(self.size - 1, -1, -1)]
                )
                for r in range(self.size):
                    self.board[r][c] = col[self.size - 1 - r]

        changed = self.board != original
        if changed:
            # Accumulate score from merges
            self._compute_score(original)
            self._spawn()
            # Check for win
            if not self.won:
                for row in self.board:
                    if 2048 in row:
                        self.won = True
                        break

        return changed

    def _compute_score(self, original):
        """Accumulate score by detecting which tiles were merged."""
        for r in range(self.size):
            for c in range(self.size):
                if original[r][c] != 0 and self.board[r][c] != original[r][c]:
                    # A tile at (r,c) was merged if the new board has a
                    # different (larger) value.  Count each merge once: when
                    # the merged tile is strictly larger than the original.
                    if self.board[r][c] > original[r][c]:
                        self.score += self.board[r][c]

    def can_move(self):
        """Check whether at least one legal move exists.

        Returns:
            bool: True if a move is possible, False if the game is over.
        """
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return True
                val = self.board[r][c]
                if c + 1 < self.size and self.board[r][c + 1] == val:
                    return True
                if r + 1 < self.size and self.board[r + 1][c] == val:
                    return True
        return False

    def is_game_over(self):
        """Return True if no legal moves remain."""
        return not self.can_move()

    def has_won(self):
        """Return True if the 2048 tile has been reached."""
        return self.won

    def get_board(self):
        """Return a deep copy of the current board state.

        Returns:
            list of list of int: The 2-D board.
        """
        return [row[:] for row in self.board]

    def __str__(self):
        lines = []
        for row in self.board:
            lines.append(
                " ".join(str(cell).rjust(4) if cell else "    ." for cell in row)
            )
        return "\n".join(lines)


def play_cli():
    """Simple command-line interface for playing 2048."""
    game = Game2048()
    move_map = {
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right',
        'q': 'quit',
    }
    print("Welcome to 2048!")
    print("Controls: w=up, s=down, a=left, d=right, q=quit")
    print()
    print(game)
    print(f"Score: {game.score}")
    print()

    while not game.is_game_over():
        choice = input("Move (w/a/s/d/q): ").strip().lower()
        if choice not in move_map:
            print("Invalid input. Use w/a/s/d to move or q to quit.")
            continue
        if choice == 'q':
            print("Goodbye!")
            return

        direction = move_map[choice]
        moved = game.move(direction)
        if not moved:
            print("(no move possible)")
            continue

        print()
        print(game)
        print(f"Score: {game.score}")
        print()

        if game.has_won():
            print("*** You reached 2048! Congratulations! ***")

    print("Game over!")
    print(f"Final score: {game.score}")


if __name__ == "__main__":
    play_cli()
