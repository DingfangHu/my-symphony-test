#!/usr/bin/env python3
"""A 2048 mini-game playable in the terminal.

Use WASD keys to move tiles (W=up, A=left, S=down, D=right).
Press Q to quit. Combine tiles to reach 2048!

Usage:
    python3 game2048.py          # play the game
    python3 game2048.py --test   # run self-tests
"""

import os
import random
import sys
import termios
import tty


class Game2048:
    """Core 2048 game logic with a 4x4 grid."""

    def __init__(self):
        self.size = 4
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.won = False
        self.game_over = False
        self.move_count = 0
        # Spawn two initial tiles
        self._spawn_tile()
        self._spawn_tile()

    def _spawn_tile(self):
        """Spawn a 2 (90%) or 4 (10%) in a random empty cell."""
        empty = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.board[r][c] == 0
        ]
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

    def _slide_row(self, row):
        """Slide and merge a single row to the left. Returns the new row."""
        tiles = [v for v in row if v != 0]
        merged = []
        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                merged.append(tiles[i] * 2)
                self.score += tiles[i] * 2
                if tiles[i] * 2 >= 2048:
                    self.won = True
                i += 2
            else:
                merged.append(tiles[i])
                i += 1
        return merged + [0] * (self.size - len(merged))

    def move(self, direction):
        """Move tiles in the given direction ('up','down','left','right').

        Returns True if the board changed, False otherwise.
        """
        old_board = [row[:] for row in self.board]

        if direction == "left":
            for r in range(self.size):
                self.board[r] = self._slide_row(self.board[r])

        elif direction == "right":
            for r in range(self.size):
                reversed_row = self.board[r][::-1]
                slid = self._slide_row(reversed_row)
                self.board[r] = slid[::-1]

        elif direction == "up":
            for c in range(self.size):
                col = [self.board[r][c] for r in range(self.size)]
                slid = self._slide_row(col)
                for r in range(self.size):
                    self.board[r][c] = slid[r]

        elif direction == "down":
            for c in range(self.size):
                col = [self.board[r][c] for r in range(self.size - 1, -1, -1)]
                slid = self._slide_row(col)
                for r in range(self.size):
                    self.board[r][c] = slid[self.size - 1 - r]

        changed = self.board != old_board
        if changed:
            self._spawn_tile()
            self.move_count += 1
            self.game_over = self._check_game_over()

        return changed

    def _check_game_over(self):
        """Return True if no more moves are possible."""
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return False
                if c + 1 < self.size and self.board[r][c] == self.board[r][c + 1]:
                    return False
                if r + 1 < self.size and self.board[r][c] == self.board[r + 1][c]:
                    return False
        return True

    def get_board(self):
        """Return a safe copy of the current board."""
        return [row[:] for row in self.board]


# ---------------------------------------------------------------------------
# Terminal UI helpers
# ---------------------------------------------------------------------------

def getch():
    """Read a single character from stdin without waiting for Enter."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Handle escape sequences (arrow keys produce ESC [ A/B/C/D)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                mapping = {"A": "up", "B": "down", "C": "right", "D": "left"}
                return mapping.get(ch3, ch3)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def clear_screen():
    """Clear the terminal."""
    os.system("clear" if os.name == "posix" else "cls")


TILE_COLORS = {
    0:    ("\033[90m", "    ."),          # dark gray
    2:    ("\033[97m", "    2"),           # white
    4:    ("\033[93m", "    4"),           # yellow
    8:    ("\033[33m", "    8"),           # orange
    16:   ("\033[91m", "   16"),           # red
    32:   ("\033[31m", "   32"),           # dark red
    64:   ("\033[95m", "   64"),           # magenta
    128:  ("\033[92m", "  128"),           # green
    256:  ("\033[94m", "  256"),           # blue
    512:  ("\033[96m", "  512"),           # cyan
    1024: ("\033[35m", " 1024"),           # purple
    2048: ("\033[1;33m", " 2048"),         # bold yellow
}

RESET = "\033[0m"


def render(game):
    """Print the current board state to the terminal."""
    clear_screen()
    print(f"\n{'=' * 28}")
    print(f"  SCORE: {game.score:<6}  MOVES: {game.move_count}")
    print(f"{'=' * 28}\n")

    for r in range(game.size):
        print("  +-------+-------+-------+-------+")
        row_str = "  "
        for c in range(game.size):
            val = game.board[r][c]
            color, label = TILE_COLORS.get(val, (RESET, f" {val:4d}"))
            row_str += f"|{color}{label}{RESET} "
        row_str += "|"
        print(row_str)
    print("  +-------+-------+-------+-------+")

    if game.won:
        print("\n  YOU REACHED 2048!  Keep going or press Q to quit.\n")
    if game.game_over:
        print(f"\n  GAME OVER!  Final score: {game.score}\n")
        return False
    return True


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def run_game():
    """Run the interactive 2048 game."""
    random.seed()
    game = Game2048()

    key_map = {
        "w": "up",    "W": "up",
        "a": "left",  "A": "left",
        "s": "down",  "S": "down",
        "d": "right", "D": "right",
        "up":    "up",
        "down":  "down",
        "left":  "left",
        "right": "right",
    }

    while True:
        alive = render(game)
        if not alive:
            break

        print("\n  [WASD] to move  |  [Q] to quit")
        ch = getch()

        if ch in ("q", "Q"):
            print(f"\n  Quit. Final score: {game.score}\n")
            break
        elif ch in key_map:
            game.move(key_map[ch])
        else:
            pass


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def run_tests():
    """Run self-tests on the game logic."""
    print("Running 2048 game tests...\n")
    failures = 0

    # Test 1: Initial board has two non-zero tiles
    g = Game2048()
    non_zero = sum(1 for r in g.board for c in r if c != 0)
    assert non_zero == 2, f"Expected 2 initial tiles, got {non_zero}"
    print("  PASS: test_initial_two_tiles")

    # Test 2: Move left merges two equal tiles
    g = Game2048()
    g.board = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    g.won = False
    changed = g.move("left")
    assert changed, "Board should have changed"
    assert g.board[0][0] == 4, f"Expected 4 at (0,0), got {g.board[0][0]}"
    assert g.board[0][1] == 0, "Expected 0 after merge"
    assert g.score == 4, f"Expected score 4, got {g.score}"
    print("  PASS: test_left_merge")

    # Test 3: Move right merges
    g = Game2048()
    g.board = [
        [0, 0, 2, 2],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    g.move("right")
    assert g.board[0][3] == 4, f"Expected 4 at (0,3), got {g.board[0][3]}"
    print("  PASS: test_right_merge")

    # Test 4: Move up merges
    g = Game2048()
    g.board = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    g.move("up")
    assert g.board[0][0] == 4, f"Expected 4 at (0,0), got {g.board[0][0]}"
    print("  PASS: test_up_merge")

    # Test 5: Move down merges
    g = Game2048()
    g.board = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    g.move("down")
    assert g.board[3][0] == 4, f"Expected 4 at (3,0), got {g.board[3][0]}"
    print("  PASS: test_down_merge")

    # Test 6: New tile spawns after a valid move
    g = Game2048()
    g.board = [
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    g.move("right")
    non_zero = sum(1 for r in g.board for c in r if c != 0)
    assert non_zero == 2, f"Expected 2 non-zero after spawn, got {non_zero}"
    print("  PASS: test_spawn_after_move")

    # Test 7: No change for invalid move
    g = Game2048()
    g.board = [
        [2, 0, 2, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    g.score = 0
    changed = g.move("up")
    assert not changed, "Board should not change for invalid up move"
    print("  PASS: test_no_change_invalid_move")

    # Test 8: Game over detection
    g = Game2048()
    g.board = [
        [2,  4,  8,  16],
        [32, 64, 128, 256],
        [2,  4,  8,  16],
        [32, 64, 128, 256],
    ]
    assert g._check_game_over(), "Should be game over"
    print("  PASS: test_game_over_detection")

    # Test 9: Not game over when moves exist
    g = Game2048()
    g.board = [
        [2,  2,  8,  16],
        [32, 64, 128, 256],
        [2,  4,  8,  16],
        [32, 64, 128, 256],
    ]
    assert not g._check_game_over(), "Should NOT be game over (2,2 can merge)"
    print("  PASS: test_not_game_over")

    # Test 10: Win detection
    g = Game2048()
    g.board = [
        [1024, 1024, 0, 0],
        [0,    0,    0, 0],
        [0,    0,    0, 0],
        [0,    0,    0, 0],
    ]
    g.score = 0
    g.won = False
    g.move("left")
    assert g.won, "Should detect win (2048 tile created)"
    print("  PASS: test_win_detection")

    # Test 11: get_board returns a copy
    g = Game2048()
    b = g.get_board()
    b[0][0] = 999
    assert g.board[0][0] != 999, "get_board should return a copy"
    print("  PASS: test_get_board_copy")

    print(f"\nAll tests passed! (11/11)\n")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        try:
            run_game()
        except KeyboardInterrupt:
            print("\n\n  Interrupted.\n")
