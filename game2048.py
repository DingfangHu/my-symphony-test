#!/usr/bin/env python3
"""2048 mini-game: a command-line implementation of the classic sliding tile puzzle.

Use WASD keys to move tiles. Merge equal tiles to reach 2048.
"""

import os
import random
import sys

SIZE = 4
WIN_TILE = 2048


def new_board():
    """Return an empty 4x4 board filled with zeros."""
    return [[0] * SIZE for _ in range(SIZE)]


def spawn_tile(board):
    """Place a 2 (90%) or 4 (10%) tile at a random empty cell.

    Returns the board (mutated in place).
    """
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if not empty:
        return board
    r, c = random.choice(empty)
    board[r][c] = 2 if random.random() < 0.9 else 4
    return board


def init_board():
    """Create a new board with two starting tiles."""
    board = new_board()
    spawn_tile(board)
    spawn_tile(board)
    return board


def _compact(row):
    """Remove zeros and slide tiles to the left. Returns a new list."""
    return [v for v in row if v != 0]


def _merge(row):
    """Merge equal adjacent tiles in a compacted row. Returns (new_row, score_gained)."""
    result = []
    score = 0
    i = 0
    while i < len(row):
        if i + 1 < len(row) and row[i] == row[i + 1]:
            merged = row[i] * 2
            result.append(merged)
            score += merged
            i += 2
        else:
            result.append(row[i])
            i += 1
    return result, score


def _pad_right(row):
    """Pad the row with zeros on the right to reach SIZE length."""
    return row + [0] * (SIZE - len(row))


def move_left(board):
    """Slide and merge all rows to the left. Returns (new_board, score_gained)."""
    result = new_board()
    total_score = 0
    for r in range(SIZE):
        compacted = _compact(board[r])
        merged, score = _merge(compacted)
        result[r] = _pad_right(merged)
        total_score += score
    return result, total_score


def move_right(board):
    """Slide and merge all rows to the right. Returns (new_board, score_gained)."""
    result = new_board()
    total_score = 0
    for r in range(SIZE):
        row = list(reversed(board[r]))
        compacted = _compact(row)
        merged, score = _merge(compacted)
        result[r] = list(reversed(_pad_right(merged)))
        total_score += score
    return result, total_score


def _transpose(board):
    """Return a new transposed board (rows become columns)."""
    return [[board[r][c] for r in range(SIZE)] for c in range(SIZE)]


def move_up(board):
    """Slide and merge all columns upward. Returns (new_board, score_gained)."""
    transposed = _transpose(board)
    new_transposed, score = move_left(transposed)
    return _transpose(new_transposed), score


def move_down(board):
    """Slide and merge all columns downward. Returns (new_board, score_gained)."""
    transposed = _transpose(board)
    new_transposed, score = move_right(transposed)
    return _transpose(new_transposed), score


def has_empty(board):
    """Return True if there is at least one empty cell."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
    return False


def _has_mergeable(board):
    """Return True if any two adjacent tiles can be merged."""
    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            if val == 0:
                continue
            if c + 1 < SIZE and board[r][c + 1] == val:
                return True
            if r + 1 < SIZE and board[r + 1][c] == val:
                return True
    return False


def is_game_over(board):
    """Return True if no valid moves remain."""
    if has_empty(board):
        return False
    return not _has_mergeable(board)


def has_won(board):
    """Return True if the board contains the WIN_TILE (2048)."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] >= WIN_TILE:
                return True
    return False


def _clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def _print_board(board, score):
    """Pretty-print the board and score."""
    _clear_screen()
    print("=" * 29)
    print("          2048")
    print("=" * 29)
    print(f"  Score: {score:>6d}")
    print("-" * 29)
    for row in board:
        print("|", end="")
        for cell in row:
            if cell == 0:
                print("      |", end="")
            else:
                print(f"{cell:^6d}|", end="")
        print()
        print("-" * 29)
    print("  W/A/S/D to move | Q to quit")


MOVE_MAP = {
    'w': move_up,
    'a': move_left,
    's': move_down,
    'd': move_right,
}


def _read_move():
    """Read a single-character move from stdin."""
    try:
        ch = sys.stdin.read(1)
        return ch.lower() if ch else 'q'
    except (EOFError, KeyboardInterrupt):
        return 'q'


def _same_board(a, b):
    """Check if two boards are identical."""
    for r in range(SIZE):
        for c in range(SIZE):
            if a[r][c] != b[r][c]:
                return False
    return True


def main():
    """Run the 2048 game loop."""
    board = init_board()
    score = 0

    while True:
        _print_board(board, score)

        if has_won(board):
            print("\n*** You reached 2048! You win! ***")
            print("Keep playing to beat your high score, or press Q to quit.")
        elif is_game_over(board):
            print("\n*** Game Over! No moves left. ***")
            print(f"Final score: {score}")
            break

        ch = _read_move()

        if ch == 'q':
            print(f"\nThanks for playing! Final score: {score}")
            break

        if ch not in MOVE_MAP:
            continue

        new_board, gained = MOVE_MAP[ch](board)
        if not _same_board(board, new_board):
            board = new_board
            score += gained
            spawn_tile(board)


if __name__ == "__main__":
    main()
