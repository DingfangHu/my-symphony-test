"""Tests for the EightQueensUI Tkinter wrapper.

Tests the UI logic layer (navigation, cell rendering, info text)
without requiring a display or Tk main loop.
"""

import unittest

from eight_queens_ui import EightQueensUI


class TestEightQueensUI(unittest.TestCase):
    """Test the EightQueensUI logic helpers (no Tk required)."""

    def setUp(self):
        """Create a fresh UI instance for each test."""
        self.ui = EightQueensUI(board_size=8)

    # ---- Initialization ----

    def test_init_default_board_size(self):
        """Board size defaults to 8."""
        self.assertEqual(self.ui.board_size, 8)
        self.assertEqual(self.ui.solution_count, 0)
        self.assertEqual(self.ui.current_index, 0)

    def test_init_4x4_board(self):
        """4x4 board should initialize without error."""
        ui = EightQueensUI(board_size=4)
        self.assertEqual(ui.board_size, 4)

    def test_init_invalid_size_raises(self):
        """Board sizes 2 and 3 should raise ValueError."""
        for size in (2, 3):
            with self.assertRaises(ValueError):
                EightQueensUI(board_size=size)

    def test_init_size_1(self):
        """Board size 1 should be valid (1 solution)."""
        ui = EightQueensUI(board_size=1)
        self.assertEqual(ui.board_size, 1)

    # ---- Solving ----

    def test_has_solutions_8x8(self):
        """8x8 board should have solutions (92 distinct)."""
        self.assertTrue(self.ui.has_solutions())
        self.assertEqual(self.ui.solution_count, 92)

    def test_has_solutions_4x4(self):
        """4x4 board should have solutions (2 distinct)."""
        ui = EightQueensUI(board_size=4)
        self.assertTrue(ui.has_solutions())
        self.assertEqual(ui.solution_count, 2)

    def test_has_solutions_1x1(self):
        """1x1 board should have exactly 1 solution."""
        ui = EightQueensUI(board_size=1)
        self.assertTrue(ui.has_solutions())
        self.assertEqual(ui.solution_count, 1)

    # ---- Navigation ----

    def test_load_solution_valid(self):
        """Loading a valid index should succeed."""
        self.assertTrue(self.ui.load_solution(1))
        self.assertEqual(self.ui.current_index, 1)

    def test_load_solution_invalid_negative(self):
        """Loading index 0 should fail."""
        self.assertTrue(self.ui.has_solutions())
        self.assertFalse(self.ui.load_solution(0))

    def test_load_solution_invalid_too_high(self):
        """Loading index beyond count should fail."""
        self.assertTrue(self.ui.has_solutions())
        self.assertFalse(self.ui.load_solution(1000))

    def test_first_solution(self):
        """first_solution should navigate to solution 1."""
        self.assertTrue(self.ui.has_solutions())
        self.assertTrue(self.ui.first_solution())
        self.assertEqual(self.ui.current_index, 1)

    def test_last_solution(self):
        """last_solution should navigate to the final solution."""
        self.assertTrue(self.ui.has_solutions())
        self.assertTrue(self.ui.last_solution())
        self.assertEqual(self.ui.current_index, 92)

    def test_next_solution(self):
        """next_solution should advance one step."""
        self.assertTrue(self.ui.has_solutions())
        self.ui.load_solution(50)
        self.assertTrue(self.ui.next_solution())
        self.assertEqual(self.ui.current_index, 51)

    def test_next_solution_at_end(self):
        """next_solution at the last solution should return False."""
        self.assertTrue(self.ui.has_solutions())
        self.ui.last_solution()
        self.assertFalse(self.ui.next_solution())
        self.assertEqual(self.ui.current_index, 92)  # unchanged

    def test_prev_solution(self):
        """prev_solution should go back one step."""
        self.assertTrue(self.ui.has_solutions())
        self.ui.load_solution(50)
        self.assertTrue(self.ui.prev_solution())
        self.assertEqual(self.ui.current_index, 49)

    def test_prev_solution_at_start(self):
        """prev_solution at first solution should return False."""
        self.assertTrue(self.ui.has_solutions())
        self.ui.first_solution()
        self.assertFalse(self.ui.prev_solution())
        self.assertEqual(self.ui.current_index, 1)  # unchanged

    def test_load_solution_before_solve_lazy_inits(self):
        """Loading before explicit solve should trigger lazy init."""
        self.assertTrue(self.ui.load_solution(1))
        self.assertEqual(self.ui.solution_count, 92)

    # ---- Current solution access ----

    def test_get_current_solution_before_load(self):
        """Before loading any solution, get_current_solution returns None."""
        self.assertIsNone(self.ui.get_current_solution())

    def test_get_current_solution_after_load(self):
        """After loading, get_current_solution returns a valid list."""
        self.ui.load_solution(1)
        sol = self.ui.get_current_solution()
        self.assertIsNotNone(sol)
        self.assertEqual(len(sol), 8)
        # Each column should be unique (valid placement)
        self.assertEqual(len(set(sol)), 8)

    def test_get_current_solution_matches_backend(self):
        """UI solution should match what the backend produces."""
        self.ui.solver.solve()
        backend_solutions = self.ui.solver._solutions
        self.ui.load_solution(1)
        self.assertEqual(self.ui.get_current_solution(), backend_solutions[0])
        self.ui.load_solution(92)
        self.assertEqual(self.ui.get_current_solution(), backend_solutions[91])

    # ---- Cell rendering ----

    def test_get_cell_symbol_before_load_returns_empty(self):
        """Before loading a solution, all cells should be empty."""
        for r in range(8):
            for c in range(8):
                self.assertEqual(self.ui.get_cell_symbol(r, c), self.ui.EMPTY_SYMBOL)

    def test_get_cell_symbol_with_queen(self):
        """Cells with queens should show the queen symbol."""
        self.ui.load_solution(1)
        sol = self.ui.get_current_solution()
        self.assertIsNotNone(sol)
        queen_count = 0
        for r in range(8):
            for c in range(8):
                if self.ui.get_cell_symbol(r, c) == self.ui.QUEEN_SYMBOL:
                    queen_count += 1
                    self.assertEqual(sol[r], c)
        self.assertEqual(queen_count, 8)

    def test_get_cell_symbol_out_of_bounds(self):
        """Out-of-bounds cells should return empty symbol."""
        self.ui.load_solution(1)
        self.assertEqual(self.ui.get_cell_symbol(-1, 0), self.ui.EMPTY_SYMBOL)
        self.assertEqual(self.ui.get_cell_symbol(0, -1), self.ui.EMPTY_SYMBOL)
        self.assertEqual(self.ui.get_cell_symbol(8, 0), self.ui.EMPTY_SYMBOL)
        self.assertEqual(self.ui.get_cell_symbol(0, 8), self.ui.EMPTY_SYMBOL)

    def test_get_cell_bg_alternates(self):
        """Cell backgrounds should alternate like a chessboard."""
        bg00 = self.ui.get_cell_bg(0, 0)
        bg01 = self.ui.get_cell_bg(0, 1)
        bg10 = self.ui.get_cell_bg(1, 0)
        self.assertNotEqual(bg00, bg01)
        self.assertNotEqual(bg00, bg10)
        self.assertEqual(bg00, self.ui.get_cell_bg(1, 1))

    def test_get_cell_bg_is_consistent(self):
        """Same parity cells should have same background."""
        for r in range(8):
            for c in range(8):
                expected = self.ui.LIGHT_SQUARE if (r + c) % 2 == 0 else self.ui.DARK_SQUARE
                self.assertEqual(self.ui.get_cell_bg(r, c), expected)

    # ---- Info text ----

    def test_get_info_text_after_navigate(self):
        """Info text should reflect current solution index."""
        self.ui.has_solutions()
        self.ui.load_solution(42)
        text = self.ui.get_info_text()
        self.assertIn("42", text)
        self.assertIn("92", text)

    def test_get_info_text_before_load(self):
        """Info text before loading should show total count."""
        self.ui.has_solutions()
        text = self.ui.get_info_text()
        self.assertIn("92", text)
        self.assertIn("solutions found", text)

    def test_get_info_text_before_solve(self):
        """Info text before solving should show 'Solving...'."""
        text = self.ui.get_info_text()
        self.assertEqual(text, "Solving...")

    # ---- Reset ----

    def test_reset_clears_solutions(self):
        """Reset should clear solutions and current index."""
        self.ui.load_solution(1)
        self.ui.reset()
        self.assertEqual(self.ui.solution_count, 0)
        self.assertEqual(self.ui.current_index, 0)

    def test_reset_then_solve_again(self):
        """After reset, solutions can be recomputed."""
        self.ui.load_solution(1)
        self.ui.reset()
        self.assertTrue(self.ui.has_solutions())
        self.assertEqual(self.ui.solution_count, 92)

    # ---- Solution uniqueness ----

    def test_each_solution_has_no_conflicts(self):
        """Every solution should have no row, column, or diagonal conflicts."""
        self.ui.has_solutions()
        for i in range(1, 93):
            self.ui.load_solution(i)
            sol = self.ui.get_current_solution()
            self.assertIsNotNone(sol)
            # Check no two queens share the same column
            self.assertEqual(len(set(sol)), self.ui.board_size)
            # Check no two queens share the same diagonal
            for r1 in range(8):
                for r2 in range(r1 + 1, 8):
                    c1, c2 = sol[r1], sol[r2]
                    self.assertNotEqual(r1 - c1, r2 - c2)  # main diagonal
                    self.assertNotEqual(r1 + c1, r2 + c2)  # anti diagonal

    def test_all_solutions_are_distinct(self):
        """All 92 solutions should be distinct from each other."""
        self.ui.has_solutions()
        seen = set()
        for i in range(1, 93):
            self.ui.load_solution(i)
            sol = self.ui.get_current_solution()
            self.assertIsNotNone(sol)
            seen.add(tuple(sol))
        self.assertEqual(len(seen), 92)


if __name__ == "__main__":
    unittest.main()
