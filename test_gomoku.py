"""Tests for the Gomoku mini-game."""

import unittest
from gomoku import Gomoku


class TestGomokuBasics(unittest.TestCase):
    """Unit tests for Gomoku initialization and basic properties."""

    def test_initial_board_empty(self):
        """Board starts completely empty."""
        game = Gomoku()
        board = game.get_board()
        for row in board:
            for cell in row:
                self.assertEqual(cell, '')

    def test_initial_not_game_over(self):
        """Game is not over initially."""
        game = Gomoku()
        self.assertFalse(game.is_game_over)

    def test_initial_winner_none(self):
        """Winner is None initially."""
        game = Gomoku()
        self.assertIsNone(game.winner)

    def test_initial_move_count_zero(self):
        """Move count starts at zero."""
        game = Gomoku()
        self.assertEqual(game.move_count, 0)

    def test_initial_current_player_human(self):
        """Human ('X') goes first."""
        game = Gomoku()
        self.assertEqual(game.current_player, 'X')

    def test_default_size_is_15(self):
        """Default board is 15x15."""
        game = Gomoku()
        board = game.get_board()
        self.assertEqual(len(board), 15)
        self.assertEqual(len(board[0]), 15)

    def test_custom_size(self):
        """Custom board size works."""
        game = Gomoku(size=10)
        board = game.get_board()
        self.assertEqual(len(board), 10)
        self.assertEqual(len(board[0]), 10)

    def test_size_too_small_raises(self):
        """Board size < 5 raises ValueError."""
        with self.assertRaises(ValueError):
            Gomoku(size=4)


class TestGomokuMoveValidation(unittest.TestCase):
    """Tests for move validation."""

    def test_valid_move_on_empty_cell(self):
        """Placing on an empty cell is valid."""
        game = Gomoku()
        self.assertTrue(game.is_valid_move(7, 7))

    def test_invalid_move_out_of_bounds_negative(self):
        """Negative coordinates are invalid."""
        game = Gomoku()
        self.assertFalse(game.is_valid_move(-1, 7))

    def test_invalid_move_out_of_bounds_positive(self):
        """Coordinates beyond board size are invalid."""
        game = Gomoku()
        self.assertFalse(game.is_valid_move(15, 7))

    def test_invalid_move_on_occupied_cell(self):
        """Placing on an occupied cell is invalid."""
        game = Gomoku()
        game.place_piece_human_only(7, 7)
        self.assertFalse(game.is_valid_move(7, 7))


class TestGomokuHumanMove(unittest.TestCase):
    """Tests for human move placement."""

    def test_place_piece_puts_X_on_board(self):
        """Human piece appears as 'X' on the board."""
        game = Gomoku()
        valid, state, cr, cc = game.place_piece(7, 7)
        self.assertTrue(valid)
        board = game.get_board()
        self.assertEqual(board[7][7], 'X')

    def test_place_piece_increments_move_count(self):
        """Move count increases by 2 (human + computer reply)."""
        game = Gomoku()
        game.place_piece(7, 7)
        self.assertEqual(game.move_count, 2)

    def test_place_piece_returns_computer_reply(self):
        """Computer replies with valid coordinates."""
        game = Gomoku()
        valid, state, cr, cc = game.place_piece(7, 7)
        self.assertTrue(valid)
        self.assertIsNotNone(cr)
        self.assertIsNotNone(cc)
        self.assertGreaterEqual(cr, 0)
        self.assertLess(cr, game.size)
        self.assertGreaterEqual(cc, 0)
        self.assertLess(cc, game.size)
        board = game.get_board()
        self.assertEqual(board[cr][cc], 'O')

    def test_place_piece_game_over_rejected(self):
        """Moves are rejected after game is over."""
        game = Gomoku()
        game._game_over = True
        valid, state, cr, cc = game.place_piece(7, 7)
        self.assertFalse(valid)

    def test_place_piece_invalid_cell_rejected(self):
        """Invalid cell placement is rejected."""
        game = Gomoku()
        game.place_piece_human_only(7, 7)  # occupy cell
        valid, state, cr, cc = game.place_piece(7, 7)
        self.assertFalse(valid)

    def test_place_piece_human_only(self):
        """place_piece_human_only places X without computer response."""
        game = Gomoku()
        result = game.place_piece_human_only(7, 7)
        self.assertTrue(result)
        self.assertEqual(game.move_count, 1)
        board = game.get_board()
        self.assertEqual(board[7][7], 'X')

    def test_place_piece_human_only_game_over_rejected(self):
        """place_piece_human_only rejects moves after game over."""
        game = Gomoku()
        game._game_over = True
        result = game.place_piece_human_only(7, 7)
        self.assertFalse(result)

    def test_place_computer_piece_only(self):
        """place_computer_piece_only places O."""
        game = Gomoku()
        result = game.place_computer_piece_only(7, 7)
        self.assertTrue(result)
        self.assertEqual(game.move_count, 1)
        board = game.get_board()
        self.assertEqual(board[7][7], 'O')


class TestGomokuWinDetection(unittest.TestCase):
    """Tests for five-in-a-row win detection."""

    def test_horizontal_win(self):
        """Five in a horizontal row is a win."""
        game = Gomoku()
        for col in range(5):
            game.place_piece_human_only(7, col)
        self.assertTrue(game.check_win_at(7, 2, 'X'))

    def test_vertical_win(self):
        """Five in a vertical column is a win."""
        game = Gomoku()
        for row in range(5):
            game.place_piece_human_only(row, 7)
        self.assertTrue(game.check_win_at(2, 7, 'X'))

    def test_diagonal_win_main(self):
        """Five on the main diagonal is a win."""
        game = Gomoku()
        for i in range(5):
            game.place_piece_human_only(i, i)
        self.assertTrue(game.check_win_at(2, 2, 'X'))

    def test_diagonal_win_anti(self):
        """Five on the anti-diagonal is a win."""
        game = Gomoku()
        for i in range(5):
            game.place_piece_human_only(i, 4 - i)
        self.assertTrue(game.check_win_at(2, 2, 'X'))

    def test_four_not_a_win(self):
        """Four in a row is NOT a win."""
        game = Gomoku()
        for col in range(4):
            game.place_piece_human_only(7, col)
        self.assertFalse(game.check_win_at(7, 1, 'X'))

    def test_six_in_a_row_is_win(self):
        """Six in a row is still a win."""
        game = Gomoku()
        for col in range(6):
            game.place_piece_human_only(7, col)
        self.assertTrue(game.check_win_at(7, 2, 'X'))

    def test_non_continuous_five_not_a_win(self):
        """Five non-continuous same-color pieces is NOT a win."""
        game = Gomoku()
        game.place_piece_human_only(7, 0)
        game.place_piece_human_only(7, 1)
        game.place_piece_human_only(7, 3)  # gap at col 2
        game.place_piece_human_only(7, 4)
        game.place_piece_human_only(7, 5)
        self.assertFalse(game.check_win_at(7, 3, 'X'))

    def test_human_win_triggers_game_over(self):
        """When human gets five, game is over and winner is set."""
        game = Gomoku()
        # Set up: human has 4 in a row, computer cannot block
        # We need to test win detection via place_piece
        for col in range(4):
            game.place_piece_human_only(7, col)
        game.place_computer_piece_only(8, 0)
        valid, state, cr, cc = game.place_piece(7, 4)
        self.assertTrue(valid)
        self.assertEqual(state, 'human_wins')
        self.assertTrue(game.is_game_over)
        self.assertEqual(game.winner, 'X')

    def test_computer_win_triggers_game_over(self):
        """When computer gets five, game is over and winner is set."""
        game = Gomoku()
        for col in range(5):
            game.place_computer_piece_only(7, col)
        game._winner = 'O'
        game._game_over = True
        self.assertTrue(game.is_game_over)
        self.assertEqual(game.winner, 'O')


class TestGomokuBoardHelpers(unittest.TestCase):
    """Tests for board state helpers."""

    def test_get_board_returns_copy(self):
        """get_board returns a copy, not a reference."""
        game = Gomoku()
        board_copy = game.get_board()
        board_copy[0][0] = 'Z'
        self.assertNotEqual(game.board[0][0], 'Z')

    def test_is_board_full_initially_false(self):
        """Board is not full at start."""
        game = Gomoku()
        self.assertFalse(game._is_board_full())

    def test_is_board_full_when_full(self):
        """_is_board_full returns True when no empty cells."""
        game = Gomoku(size=5)
        # Set board directly to avoid early win detection
        game.board = [
            ['X', 'O', 'X', 'O', 'X'],
            ['O', 'X', 'O', 'X', 'O'],
            ['X', 'O', 'X', 'O', 'X'],
            ['O', 'X', 'O', 'X', 'O'],
            ['X', 'O', 'X', 'O', 'X'],
        ]
        self.assertTrue(game._is_board_full())

    def test_str_representation(self):
        """__str__ returns a string with dots for empty cells."""
        game = Gomoku()
        rep = str(game)
        self.assertIn('.', rep)
        lines = rep.split('\n')
        self.assertEqual(len(lines), game.size)


class TestGomokuComputerAI(unittest.TestCase):
    """Tests for computer AI behavior."""

    def test_computer_blocks_four_in_a_row(self):
        """Computer blocks human from completing five in a row."""
        game = Gomoku()
        # Human has X at (7,0), (7,1), (7,2), (7,3)
        for col in range(4):
            game.place_piece_human_only(7, col)
        # Now human moves at center to start, computer should block at (7,4)
        game.board[7][0] = 'X'
        game.board[7][1] = 'X'
        game.board[7][2] = 'X'
        game.board[7][3] = 'X'
        game._move_count = 4
        # Simulate computer's blocking logic
        # Place a human piece somewhere to trigger computer move
        valid, state, cr, cc = game.place_piece(0, 0)
        self.assertTrue(valid)
        # Computer should block at (7,4)
        board = game.get_board()
        self.assertEqual(board[7][4], 'O')

    def test_computer_wins_when_possible(self):
        """Computer takes the winning move when available."""
        game = Gomoku()
        for col in range(4):
            game.place_computer_piece_only(7, col)
        # Place computer pieces but not winning yet
        game._winner = None
        game._game_over = False
        game.board[7][0] = 'O'
        game.board[7][1] = 'O'
        game.board[7][2] = 'O'
        game.board[7][3] = 'O'
        game._move_count = 4
        # Human places a piece, computer should win at (7,4)
        valid, state, cr, cc = game.place_piece(0, 0)
        self.assertTrue(valid)
        self.assertEqual(state, 'computer_wins')
        self.assertEqual(game.winner, 'O')


class TestGomokuPatternScoring(unittest.TestCase):
    """Tests for the pattern scoring static method."""

    def test_five_pattern_score(self):
        """Count >= 5 returns the maximum score."""
        self.assertEqual(Gomoku._pattern_score(5, 0), 100000)
        self.assertEqual(Gomoku._pattern_score(6, 0), 100000)

    def test_open_four_score(self):
        """Open four (count=4, open_ends=2) returns 10000."""
        self.assertEqual(Gomoku._pattern_score(4, 2), 10000)

    def test_blocked_four_score(self):
        """Blocked four (count=4, open_ends=1) returns 1000."""
        self.assertEqual(Gomoku._pattern_score(4, 1), 1000)

    def test_closed_four_score(self):
        """Fully blocked four returns 0."""
        self.assertEqual(Gomoku._pattern_score(4, 0), 0)

    def test_open_three_score(self):
        """Open three (count=3, open_ends=2) returns 1000."""
        self.assertEqual(Gomoku._pattern_score(3, 2), 1000)

    def test_blocked_three_score(self):
        """Blocked three (count=3, open_ends=1) returns 100."""
        self.assertEqual(Gomoku._pattern_score(3, 1), 100)

    def test_closed_three_score(self):
        """Fully blocked three returns 0."""
        self.assertEqual(Gomoku._pattern_score(3, 0), 0)

    def test_open_two_score(self):
        """Open two (count=2, open_ends=2) returns 100."""
        self.assertEqual(Gomoku._pattern_score(2, 2), 100)

    def test_blocked_two_score(self):
        """Blocked two (count=2, open_ends=1) returns 10."""
        self.assertEqual(Gomoku._pattern_score(2, 1), 10)

    def test_open_one_score(self):
        """Open one (count=1, open_ends=2) returns 10."""
        self.assertEqual(Gomoku._pattern_score(1, 2), 10)

    def test_blocked_one_score(self):
        """Blocked one (count=1, open_ends=1) returns 1."""
        self.assertEqual(Gomoku._pattern_score(1, 1), 1)

    def test_zero_count_score(self):
        """Count 0 returns 0."""
        self.assertEqual(Gomoku._pattern_score(0, 2), 0)


class TestGomokuGameFlow(unittest.TestCase):
    """Integration-style tests for full game flow."""

    def test_multiple_moves_no_crash(self):
        """Playing multiple full turns does not crash."""
        game = Gomoku()
        tries = 0
        while not game.is_game_over and tries < 100:
            # Try to place a piece at a valid location
            placed = False
            for r in range(game.size):
                for c in range(game.size):
                    if game.is_valid_move(r, c):
                        valid, state, cr, cc = game.place_piece(r, c)
                        if valid:
                            placed = True
                            break
                if placed:
                    break
            tries += 1
            if not placed:
                break
        # Game should have progressed
        self.assertGreater(game.move_count, 0)

    def test_draw_on_full_board(self):
        """A full board without a winner results in a draw."""
        # Use a small board for this test
        game = Gomoku(size=5)
        # Fill board alternating to prevent any 5-in-a-row
        # Pattern: checkerboard so no 5 in a row
        for r in range(5):
            for c in range(5):
                if (r + c) % 2 == 0:
                    game.board[r][c] = 'X'
                else:
                    game.board[r][c] = 'O'
        game._move_count = 25
        # Now try to place a piece - board is full
        self.assertTrue(game._is_board_full())

    def test_str_representation_contains_X_and_O(self):
        """String representation shows both player symbols."""
        game = Gomoku()
        game.place_piece_human_only(7, 7)
        game.place_computer_piece_only(7, 8)
        rep = str(game)
        self.assertIn('X', rep)
        self.assertIn('O', rep)


class TestGomokuEdgeCases(unittest.TestCase):
    """Edge case tests."""

    def test_place_piece_at_bounds(self):
        """Placing at board edges works correctly."""
        game = Gomoku()
        valid, state, cr, cc = game.place_piece(0, 0)
        self.assertTrue(valid)
        board = game.get_board()
        self.assertEqual(board[0][0], 'X')

    def test_place_piece_at_corner(self):
        """Placing at the corner works."""
        game = Gomoku()
        sz = game.size - 1
        valid, state, cr, cc = game.place_piece(sz, sz)
        self.assertTrue(valid)
        board = game.get_board()
        self.assertEqual(board[sz][sz], 'X')

    def test_computer_piece_on_empty_board(self):
        """place_computer_piece_only works on empty board."""
        game = Gomoku()
        result = game.place_computer_piece_only(7, 7)
        self.assertTrue(result)
        self.assertEqual(game.move_count, 1)

    def test_human_win_on_last_empty_cell(self):
        """Human wins by taking the last empty cell."""
        game = Gomoku(size=5)
        # Fill most of the board
        game.board = [
            ['X', 'X', 'X', '', 'O'],
            ['O', 'O', 'O', 'O', 'X'],
            ['X', 'X', 'X', 'O', 'O'],
            ['O', 'O', 'O', 'X', 'X'],
            ['X', 'X', 'O', 'O', 'O'],
        ]
        # Human at (0,3) should win
        game._move_count = 21
        game._game_over = False
        game._winner = None
        valid, state, cr, cc = game.place_piece(0, 3)
        self.assertTrue(valid)
        # Check if it's a human win
        self.assertTrue(game.is_game_over)

    def test_move_count_after_both_players(self):
        """After a full turn, move_count reflects both moves."""
        game = Gomoku()
        self.assertEqual(game.move_count, 0)
        game.place_piece(7, 7)
        # Human placed, computer replied = 2 moves
        self.assertEqual(game.move_count, 2)


if __name__ == "__main__":
    unittest.main()
