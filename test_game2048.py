#!/usr/bin/env python3
"""Unit tests for the 2048 mini-game logic."""

import unittest
import game2048

SIZE = game2048.SIZE


class TestBoardInit(unittest.TestCase):
    """Tests for board initialization."""

    def test_new_board_is_empty(self):
        board = game2048.new_board()
        self.assertEqual(len(board), SIZE)
        for row in board:
            self.assertEqual(len(row), SIZE)
            self.assertTrue(all(cell == 0 for cell in row))

    def test_init_board_has_two_tiles(self):
        board = game2048.init_board()
        non_zero = sum(1 for r in range(SIZE) for c in range(SIZE) if board[r][c] != 0)
        self.assertEqual(non_zero, 2)

    def test_init_board_tiles_are_valid(self):
        board = game2048.init_board()
        for r in range(SIZE):
            for c in range(SIZE):
                self.assertIn(board[r][c], (0, 2, 4))


class TestSpawnTile(unittest.TestCase):
    """Tests for spawn_tile."""

    def test_spawn_adds_one_tile(self):
        board = game2048.new_board()
        board[0][0] = 2
        non_zero_before = sum(1 for r in range(SIZE) for c in range(SIZE) if board[r][c] != 0)
        game2048.spawn_tile(board)
        non_zero_after = sum(1 for r in range(SIZE) for c in range(SIZE) if board[r][c] != 0)
        self.assertEqual(non_zero_after, non_zero_before + 1)

    def test_spawn_on_full_board_does_nothing(self):
        board = [[2] * SIZE for _ in range(SIZE)]
        board_copy = [row[:] for row in board]
        game2048.spawn_tile(board)
        self.assertEqual(board, board_copy)

    def test_spawned_tile_is_2_or_4(self):
        board = game2048.new_board()
        game2048.spawn_tile(board)
        values = [board[r][c] for r in range(SIZE) for c in range(SIZE) if board[r][c] != 0]
        self.assertEqual(len(values), 1)
        self.assertIn(values[0], (2, 4))


class TestMoveLeft(unittest.TestCase):
    """Tests for move_left."""

    def test_move_left_slides_tiles(self):
        board = game2048.new_board()
        board[0][2] = 2
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0][0], 2)
        self.assertEqual(score, 0)

    def test_move_left_merges_equal_tiles(self):
        board = game2048.new_board()
        board[0][0] = 2
        board[0][1] = 2
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0][0], 4)
        self.assertEqual(new_board[0][1], 0)
        self.assertEqual(score, 4)

    def test_move_left_double_merge(self):
        board = game2048.new_board()
        board[0] = [2, 2, 2, 2]
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0], [4, 4, 0, 0])
        self.assertEqual(score, 8)

    def test_move_left_no_merge_with_gap(self):
        board = game2048.new_board()
        board[0] = [2, 0, 2, 4]
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0], [4, 4, 0, 0])
        self.assertEqual(score, 4)

    def test_move_left_triple_no_double_merge(self):
        board = game2048.new_board()
        board[0] = [2, 2, 2, 0]
        new_board, score = game2048.move_left(board)
        # First two merge to 4, third stays as 2
        self.assertEqual(new_board[0], [4, 2, 0, 0])
        self.assertEqual(score, 4)

    def test_move_left_full_row(self):
        board = game2048.new_board()
        board[0] = [2, 2, 4, 8]
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0], [4, 4, 8, 0])
        self.assertEqual(score, 4)

    def test_move_left_no_change_on_full_no_merge(self):
        board = game2048.new_board()
        board[0] = [2, 4, 8, 16]
        new_board, score = game2048.move_left(board)
        self.assertEqual(new_board[0], [2, 4, 8, 16])
        self.assertEqual(score, 0)


class TestMoveRight(unittest.TestCase):
    """Tests for move_right."""

    def test_move_right_slides_tiles(self):
        board = game2048.new_board()
        board[0][1] = 2
        new_board, score = game2048.move_right(board)
        self.assertEqual(new_board[0][3], 2)
        self.assertEqual(score, 0)

    def test_move_right_merges_equal_tiles(self):
        board = game2048.new_board()
        board[0][2] = 2
        board[0][3] = 2
        new_board, score = game2048.move_right(board)
        self.assertEqual(new_board[0][3], 4)
        self.assertEqual(score, 4)


class TestMoveUp(unittest.TestCase):
    """Tests for move_up."""

    def test_move_up_slides_tiles(self):
        board = game2048.new_board()
        board[2][0] = 2
        new_board, score = game2048.move_up(board)
        self.assertEqual(new_board[0][0], 2)
        self.assertEqual(score, 0)

    def test_move_up_merges_equal_tiles(self):
        board = game2048.new_board()
        board[0][0] = 2
        board[1][0] = 2
        new_board, score = game2048.move_up(board)
        self.assertEqual(new_board[0][0], 4)
        self.assertEqual(new_board[1][0], 0)
        self.assertEqual(score, 4)


class TestMoveDown(unittest.TestCase):
    """Tests for move_down."""

    def test_move_down_slides_tiles(self):
        board = game2048.new_board()
        board[1][0] = 2
        new_board, score = game2048.move_down(board)
        self.assertEqual(new_board[3][0], 2)
        self.assertEqual(score, 0)

    def test_move_down_merges_equal_tiles(self):
        board = game2048.new_board()
        board[2][0] = 2
        board[3][0] = 2
        new_board, score = game2048.move_down(board)
        self.assertEqual(new_board[3][0], 4)
        self.assertEqual(score, 4)


class TestGameState(unittest.TestCase):
    """Tests for game state checks."""

    def test_has_empty_on_empty_board(self):
        board = game2048.new_board()
        self.assertTrue(game2048.has_empty(board))

    def test_has_empty_on_full_board(self):
        board = [[2] * SIZE for _ in range(SIZE)]
        self.assertFalse(game2048.has_empty(board))

    def test_is_game_over_on_empty_board(self):
        board = game2048.new_board()
        self.assertFalse(game2048.is_game_over(board))

    def test_is_game_over_on_full_no_moves(self):
        # Alternating values so no merges possible
        board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game2048.is_game_over(board))

    def test_is_game_over_full_with_merge(self):
        board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 4],  # Last two tiles mergeable
        ]
        self.assertFalse(game2048.is_game_over(board))

    def test_has_won_on_winning_board(self):
        board = game2048.new_board()
        board[0][0] = 2048
        self.assertTrue(game2048.has_won(board))

    def test_has_won_on_non_winning_board(self):
        board = game2048.new_board()
        board[0][0] = 1024
        self.assertFalse(game2048.has_won(board))

    def test_has_won_on_greater_than_2048(self):
        board = game2048.new_board()
        board[0][0] = 4096
        self.assertTrue(game2048.has_won(board))


class TestTranspose(unittest.TestCase):
    """Tests for the internal _transpose helper."""

    def test_transpose_identity(self):
        board = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
        ]
        transposed = game2048._transpose(board)
        expected = [
            [1, 5, 9, 13],
            [2, 6, 10, 14],
            [3, 7, 11, 15],
            [4, 8, 12, 16],
        ]
        self.assertEqual(transposed, expected)

    def test_transpose_twice_is_identity(self):
        board = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
        ]
        transposed = game2048._transpose(game2048._transpose(board))
        self.assertEqual(transposed, board)


class TestSameBoard(unittest.TestCase):
    """Tests for _same_board helper."""

    def test_same_board_identical(self):
        a = game2048.new_board()
        b = game2048.new_board()
        self.assertTrue(game2048._same_board(a, b))

    def test_same_board_different(self):
        a = game2048.new_board()
        b = game2048.new_board()
        b[0][0] = 2
        self.assertFalse(game2048._same_board(a, b))


class TestMoveImmutability(unittest.TestCase):
    """Tests that move functions do not mutate the input board."""

    def test_move_left_does_not_mutate_input(self):
        board = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        board_copy = [row[:] for row in board]
        game2048.move_left(board)
        self.assertEqual(board, board_copy)

    def test_move_right_does_not_mutate_input(self):
        board = [[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        board_copy = [row[:] for row in board]
        game2048.move_right(board)
        self.assertEqual(board, board_copy)

    def test_move_up_does_not_mutate_input(self):
        board = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        board_copy = [row[:] for row in board]
        game2048.move_up(board)
        self.assertEqual(board, board_copy)

    def test_move_down_does_not_mutate_input(self):
        board = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        board_copy = [row[:] for row in board]
        game2048.move_down(board)
        self.assertEqual(board, board_copy)


if __name__ == "__main__":
    unittest.main()
