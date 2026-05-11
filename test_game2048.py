"""Unit tests for the 2048 mini-game."""

import unittest
from game2048 import Game2048


class TestGame2048Init(unittest.TestCase):
    """Tests for game initialization."""

    def test_new_game_has_two_tiles(self):
        game = Game2048(seed=42)
        non_zero = sum(1 for r in range(4) for c in range(4) if game.grid[r][c] != 0)
        self.assertEqual(non_zero, 2)

    def test_new_game_score_zero(self):
        game = Game2048()
        self.assertEqual(game.score, 0)

    def test_new_game_not_won(self):
        game = Game2048()
        self.assertFalse(game.won)

    def test_new_game_not_over(self):
        game = Game2048()
        self.assertFalse(game.is_over)

    def test_initial_tiles_are_2_or_4(self):
        game = Game2048(seed=42)
        for r in range(4):
            for c in range(4):
                self.assertIn(game.grid[r][c], (0, 2, 4))


class TestSlideRowLeft(unittest.TestCase):
    """Tests for the _slide_row_left static method."""

    def test_slide_empty(self):
        row, pts, win = Game2048._slide_row_left([0, 0, 0, 0])
        self.assertEqual(row, [0, 0, 0, 0])
        self.assertEqual(pts, 0)
        self.assertFalse(win)

    def test_slide_no_merge(self):
        row, pts, win = Game2048._slide_row_left([0, 2, 0, 4])
        self.assertEqual(row, [2, 4, 0, 0])
        self.assertEqual(pts, 0)

    def test_slide_single_merge(self):
        row, pts, win = Game2048._slide_row_left([2, 2, 0, 0])
        self.assertEqual(row, [4, 0, 0, 0])
        self.assertEqual(pts, 4)

    def test_slide_double_merge(self):
        row, pts, win = Game2048._slide_row_left([2, 2, 4, 4])
        self.assertEqual(row, [4, 8, 0, 0])
        self.assertEqual(pts, 12)

    def test_slide_triple_no_double_merge(self):
        """Three same values: first two merge, third stands alone."""
        row, pts, win = Game2048._slide_row_left([2, 2, 2, 0])
        self.assertEqual(row, [4, 2, 0, 0])
        self.assertEqual(pts, 4)

    def test_slide_full_row(self):
        row, pts, win = Game2048._slide_row_left([4, 4, 8, 8])
        self.assertEqual(row, [8, 16, 0, 0])
        self.assertEqual(pts, 24)


class TestMoveLeft(unittest.TestCase):
    """Tests for left-direction moves."""

    def test_left_move_merges_and_adds_tile(self):
        game = Game2048(seed=123)
        # Manually set up a known board
        game.grid = [[2, 2, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        old_score = game.score
        moved = game.move('left')
        self.assertTrue(moved)
        # First row should be [4, 0, 0, 0] plus a new tile somewhere
        self.assertEqual(game.grid[0][0], 4)
        self.assertGreater(game.score, old_score)

    def test_left_move_no_change_returns_false(self):
        game = Game2048(seed=42)
        game.grid = [[2, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        # Remove any tiles that interfere by clearing non-row-0
        for r in range(1, 4):
            for c in range(4):
                game.grid[r][c] = 0
        moved = game.move('left')
        # Moving left on [2, 0, 0, 0] doesn't change anything
        # But _add_random_tile may change it... 
        # Actually, move compares old vs new grid before adding random tile.
        # [2, 0, 0, 0] sliding left stays [2, 0, 0, 0] -> no change
        self.assertFalse(moved)


class TestMoveRight(unittest.TestCase):
    """Tests for right-direction moves."""

    def test_right_move_slides_to_right(self):
        game = Game2048(seed=100)
        game.grid = [[0, 0, 2, 2],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('right')
        self.assertEqual(game.grid[0][3], 4)


class TestMoveUp(unittest.TestCase):
    """Tests for up-direction moves."""

    def test_up_move_slides_upward(self):
        game = Game2048(seed=200)
        game.grid = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 2, 0, 0]]
        game.move('up')
        self.assertEqual(game.grid[0][1], 2)


class TestMoveDown(unittest.TestCase):
    """Tests for down-direction moves."""

    def test_down_move_slides_downward(self):
        game = Game2048(seed=300)
        game.grid = [[0, 2, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('down')
        self.assertEqual(game.grid[3][1], 2)


class TestInvalidMove(unittest.TestCase):
    """Tests for invalid directions."""

    def test_invalid_direction_raises_valueerror(self):
        game = Game2048()
        with self.assertRaises(ValueError):
            game.move('diagonal')


class TestGameOver(unittest.TestCase):
    """Tests for game-over detection."""

    def test_full_board_with_no_moves_is_over(self):
        game = Game2048(seed=42)
        # Fill board with alternating values that can't merge
        game.grid = [[2, 4, 2, 4],
                     [4, 2, 4, 2],
                     [2, 4, 2, 4],
                     [4, 2, 4, 2]]
        game._over = not game._can_move()
        self.assertTrue(game.is_over)

    def test_full_board_with_moves_is_not_over(self):
        game = Game2048(seed=42)
        game.grid = [[2, 2, 2, 2],
                     [4, 4, 4, 4],
                     [2, 2, 2, 2],
                     [4, 4, 4, 4]]
        self.assertTrue(game._can_move())
        self.assertFalse(game.is_over)

    def test_move_when_over_returns_false(self):
        game = Game2048(seed=42)
        game._over = True
        result = game.move('left')
        self.assertFalse(result)


class TestWinDetection(unittest.TestCase):
    """Tests for the win condition (reaching a 2048 tile)."""

    def test_merge_to_1024_then_1024_sets_won(self):
        """Simulate a move that creates 2048."""
        game = Game2048(seed=500)
        game.grid = [[1024, 1024, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('left')
        self.assertTrue(game.won)

    def test_win_tile_present_in_grid(self):
        game = Game2048(seed=500)
        game.grid = [[1024, 1024, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('left')
        self.assertEqual(game.grid[0][0], 2048)


class TestScore(unittest.TestCase):
    """Tests for score accumulation."""

    def test_merge_adds_to_score(self):
        game = Game2048(seed=42)
        game.grid = [[2, 2, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('left')
        self.assertEqual(game.score, 4)

    def test_multiple_merges_accumulate_score(self):
        game = Game2048(seed=42)
        game.grid = [[2, 2, 4, 4],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        game.move('left')
        # 2+2=4, 4+4=8 -> total score = 12
        self.assertEqual(game.score, 12)


class TestGetState(unittest.TestCase):
    """Tests for the get_state method."""

    def test_get_state_returns_dict_with_correct_keys(self):
        game = Game2048(seed=42)
        state = game.get_state()
        self.assertIn('grid', state)
        self.assertIn('score', state)
        self.assertIn('won', state)
        self.assertIn('is_over', state)

    def test_get_state_grid_is_deep_copy(self):
        game = Game2048(seed=42)
        state = game.get_state()
        state['grid'][0][0] = 999
        self.assertNotEqual(game.grid[0][0], 999)


class TestDeterministicSeed(unittest.TestCase):
    """Tests that seeding produces reproducible boards."""

    def test_same_seed_produces_same_board(self):
        g1 = Game2048(seed=42)
        g2 = Game2048(seed=42)
        self.assertEqual(g1.grid, g2.grid)

    def test_different_seeds_produce_different_boards(self):
        g1 = Game2048(seed=42)
        g2 = Game2048(seed=99)
        # Extremely unlikely to be identical
        self.assertNotEqual(g1.grid, g2.grid)


if __name__ == '__main__':
    unittest.main()
