"""Tests for the 2048 mini-game."""

import unittest
from game2048 import Game2048


class TestGame2048(unittest.TestCase):
    """Unit tests for the Game2048 class."""

    def test_initial_board_has_two_tiles(self):
        """Board starts with exactly two non-zero tiles."""
        game = Game2048()
        board = game.get_board()
        non_zero = [cell for row in board for cell in row if cell != 0]
        self.assertEqual(len(non_zero), 2)

    def test_initial_score_zero(self):
        """Score starts at zero."""
        game = Game2048()
        self.assertEqual(game.score, 0)

    def test_initial_not_won(self):
        """Game is not won initially."""
        game = Game2048()
        self.assertFalse(game.has_won())

    def test_initial_not_game_over(self):
        """Game is not over initially (empty cells + valid moves)."""
        game = Game2048()
        self.assertFalse(game.is_game_over())

    def test_board_size_default(self):
        """Default board is 4x4."""
        game = Game2048()
        board = game.get_board()
        self.assertEqual(len(board), 4)
        self.assertEqual(len(board[0]), 4)

    def test_board_size_custom(self):
        """Custom board size works."""
        game = Game2048(size=5)
        board = game.get_board()
        self.assertEqual(len(board), 5)
        self.assertEqual(len(board[0]), 5)

    def test_size_too_small_raises(self):
        """Board size < 2 raises ValueError."""
        with self.assertRaises(ValueError):
            Game2048(size=1)

    def test_invalid_direction_raises(self):
        """Invalid direction raises ValueError."""
        game = Game2048()
        with self.assertRaises(ValueError):
            game.move('diagonal')

    def test_move_left_basic(self):
        """A basic left move slides tiles correctly (deterministic)."""
        # Use _slide_row directly to test slide logic without random spawn
        result = Game2048._slide_row([0, 0, 0, 2])
        self.assertEqual(result, [2, 0, 0, 0])

    def test_move_left_merge(self):
        """Left move merges two equal adjacent tiles."""
        game = Game2048()
        game.board = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('left')
        self.assertEqual(game.board[0][0], 4)

    def test_move_left_no_double_merge(self):
        """A merge only happens once per tile pair (no chain merge)."""
        # Use _slide_row directly to test merge logic without random spawn
        result = Game2048._slide_row([2, 2, 4, 0])
        # [2,2,4,0] should become [4,4,0,0], not [8,0,0,0]
        self.assertEqual(result, [4, 4, 0, 0])

    def test_move_right_basic(self):
        """Right move slides tiles to the right."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('right')
        self.assertEqual(game.board[0][3], 2)

    def test_move_right_merge(self):
        """Right move merges two equal adjacent tiles."""
        game = Game2048()
        game.board = [
            [0, 0, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('right')
        self.assertEqual(game.board[0][3], 4)

    def test_move_up_basic(self):
        """Up move slides tiles upward."""
        game = Game2048()
        game.board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
        ]
        game.move('up')
        self.assertEqual(game.board[0][0], 2)

    def test_move_up_merge(self):
        """Up move merges two equal adjacent tiles."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('up')
        self.assertEqual(game.board[0][0], 4)

    def test_move_down_basic(self):
        """Down move slides tiles downward."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('down')
        self.assertEqual(game.board[3][0], 2)

    def test_move_down_merge(self):
        """Down move merges two equal adjacent tiles."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('down')
        self.assertEqual(game.board[3][0], 4)

    def test_move_returns_true_when_changed(self):
        """A successful move returns True."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        # Move the tile downward -- slides from row 0 to row 3
        result = game.move('down')
        self.assertTrue(result)

    def test_move_returns_false_when_unchanged(self):
        """A move that does nothing returns False."""
        game = Game2048()
        game.board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
        ]
        result = game.move('down')  # Already at bottom row
        self.assertFalse(result)

    def test_new_tile_spawned_after_move(self):
        """After a valid move, exactly 2 non-zero tiles remain."""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('down')
        non_zero = [cell for row in game.board for cell in row if cell != 0]
        self.assertEqual(len(non_zero), 2)

    def test_score_after_merge(self):
        """Score increases correctly after a merge."""
        game = Game2048()
        game.board = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('left')
        self.assertGreater(game.score, 0)
        # Merged 2+2 -> score += 4
        self.assertEqual(game.score, 4)

    def test_can_move_with_empty_cell(self):
        """can_move returns True when an empty cell exists."""
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 0],
        ]
        self.assertTrue(game.can_move())

    def test_can_move_with_adjacent_equal(self):
        """can_move returns True when adjacent equal tiles exist."""
        game = Game2048()
        game.board = [
            [2, 2, 4, 8],
            [16, 32, 64, 128],
            [256, 512, 1024, 4],
            [8, 16, 32, 64],
        ]
        self.assertTrue(game.can_move())

    def test_game_over_full_no_moves(self):
        """is_game_over returns True when board is full with no adjacent matches."""
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game.is_game_over())

    def test_win_detection(self):
        """A 2048 tile triggers has_won."""
        game = Game2048()
        game.board = [
            [1024, 1024, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        game.move('left')
        self.assertTrue(game.has_won())

    def test_get_board_returns_copy(self):
        """get_board returns a copy, not a reference to the internal board."""
        game = Game2048()
        board_copy = game.get_board()
        board_copy[0][0] = 9999
        self.assertNotEqual(game.board[0][0], 9999)

    def test_str_representation(self):
        """__str__ returns a string representation."""
        game = Game2048()
        rep = str(game)
        self.assertIsInstance(rep, str)
        self.assertIn(".", rep)  # Empty cells shown as dots

    def test_play_multiple_moves(self):
        """Multiple moves can be played without error."""
        game = Game2048()
        for _ in range(20):
            moved = False
            for direction in ('left', 'right', 'up', 'down'):
                if game.is_game_over():
                    break
                moved = game.move(direction)
                if moved:
                    break
            if game.is_game_over():
                break
        # Should not crash
        self.assertTrue(True)

    def test_spawn_produces_2_or_4(self):
        """Spawned tiles are only 2 or 4."""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        success = game._spawn()
        self.assertTrue(success)
        non_zero = [cell for row in game.board for cell in row if cell != 0]
        self.assertEqual(len(non_zero), 1)
        self.assertIn(non_zero[0], (2, 4))

    def test_spawn_returns_false_when_full(self):
        """_spawn returns False when the board is full."""
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        result = game._spawn()
        self.assertFalse(result)

    def test_no_new_tile_when_move_does_nothing(self):
        """When a move does not change the board, no new tile is spawned."""
        game = Game2048()
        game.board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 2],
        ]
        result = game.move('right')
        self.assertFalse(result)
        non_zero = [cell for row in game.board for cell in row if cell != 0]
        self.assertEqual(len(non_zero), 1)  # Still just 1 tile, no spawn


if __name__ == "__main__":
    unittest.main()
