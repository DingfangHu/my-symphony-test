#!/usr/bin/env python3
"""Minimal smoke test for the project.

Verifies:
  - Core 2048 game logic works end-to-end
  - All project modules can be compiled
"""

import subprocess
import sys
import unittest

import game2048


class SmokeTestGame2048(unittest.TestCase):
    """End-to-end smoke tests for the 2048 game core flow."""

    def test_init_board_produces_playable_state(self):
        """A freshly initialized board should have two tiles and not be game over."""
        board = game2048.init_board()
        non_zero = sum(
            1 for r in range(game2048.SIZE)
            for c in range(game2048.SIZE)
            if board[r][c] != 0
        )
        self.assertEqual(non_zero, 2)
        self.assertFalse(game2048.is_game_over(board))
        self.assertFalse(game2048.has_won(board))

    def test_full_game_loop_simulates_without_errors(self):
        """Simulate a short sequence of moves to verify core flow."""
        board = game2048.init_board()
        score = 0

        moves = ['a', 'd', 'w', 's']  # left, right, up, down

        for move in moves:
            new_board, gained = game2048.MOVE_MAP[move](board)
            if not game2048._same_board(board, new_board):
                board = new_board
                score += gained
                game2048.spawn_tile(board)

        # The game should not crash; board should still be valid SIZE x SIZE
        self.assertEqual(len(board), game2048.SIZE)
        for row in board:
            self.assertEqual(len(row), game2048.SIZE)

    def test_move_updates_score(self):
        """A merge should increase the score."""
        board = game2048.new_board()
        board[0][0] = 2
        board[0][1] = 2
        _, score = game2048.move_left(board)
        self.assertEqual(score, 4)

    def test_game_over_detection(self):
        """A completely blocked board with no merges should be game over."""
        board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game2048.is_game_over(board))

    def test_win_detection(self):
        """Reaching 2048 should be detected as a win."""
        board = game2048.new_board()
        board[0][0] = 2048
        self.assertTrue(game2048.has_won(board))


class SmokeTestCompilation(unittest.TestCase):
    """Verify all project modules compile."""

    def test_all_modules_compile(self):
        """Run compileall to verify all Python files compile without errors."""
        result = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", "."],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0,
                         f"compileall failed:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
