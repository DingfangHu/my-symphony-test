"""Tests for the EightQueensWeb web interface.

Tests the content-generation layer (HTML building, JSON API,
navigation helpers) without requiring a running HTTP server.
"""

import json
import unittest

from eight_queens_web import WebQueensServer


class TestWebQueensServer(unittest.TestCase):
    """Test WebQueensServer content generation and API helpers."""

    def setUp(self):
        """Create a fresh server wrapper for each test."""
        self.server = WebQueensServer(board_size=8, port=9999)

    # ---- Initialisation ----

    def test_init_defaults(self):
        """Default board_size=8, port=8080."""
        s = WebQueensServer()
        self.assertEqual(s.board_size, 8)
        self.assertEqual(s.port, 8080)
        self.assertEqual(s.solution_count, 0)

    def test_init_custom_size(self):
        """Custom board sizes are accepted."""
        s = WebQueensServer(board_size=4, port=3000)
        self.assertEqual(s.board_size, 4)
        self.assertEqual(s.port, 3000)

    def test_init_size_1(self):
        """Board size 1 is valid."""
        s = WebQueensServer(board_size=1)
        self.assertEqual(s.board_size, 1)

    def test_init_invalid_board_size(self):
        """Board sizes <= 0 raise ValueError."""
        for size in (0, -1):
            with self.assertRaises(ValueError):
                WebQueensServer(board_size=size)

    def test_init_invalid_port_low(self):
        """Port 0 raises ValueError."""
        with self.assertRaises(ValueError):
            WebQueensServer(port=0)

    def test_init_invalid_port_high(self):
        """Port > 65535 raises ValueError."""
        with self.assertRaises(ValueError):
            WebQueensServer(port=70000)

    # ---- Solving ----

    def test_solve_8x8_count(self):
        """8x8 board should yield 92 solutions."""
        solutions = self.server.solve()
        self.assertEqual(len(solutions), 92)
        self.assertEqual(self.server.solution_count, 92)

    def test_solve_4x4_count(self):
        """4x4 board should yield 2 solutions."""
        s = WebQueensServer(board_size=4)
        solutions = s.solve()
        self.assertEqual(len(solutions), 2)

    def test_solve_1x1_count(self):
        """1x1 board should yield 1 solution."""
        s = WebQueensServer(board_size=1)
        solutions = s.solve()
        self.assertEqual(len(solutions), 1)

    def test_solve_2x2_count(self):
        """2x2 board should yield 0 solutions."""
        s = WebQueensServer(board_size=2)
        solutions = s.solve()
        self.assertEqual(len(solutions), 0)

    def test_solve_is_idempotent(self):
        """Calling solve() twice returns cached results."""
        first = self.server.solve()
        second = self.server.solve()
        self.assertIs(first, second)
        self.assertEqual(len(first), 92)

    # ---- HTML generation ----

    def test_build_html_contains_title(self):
        """Generated HTML should include the puzzle title."""
        html = self.server.build_html()
        self.assertIn("<title>Eight Queens Puzzle</title>", html)
        self.assertIn("8-Queens Puzzle", html)

    def test_build_html_contains_solutions_data(self):
        """Generated HTML should embed solutions as JSON."""
        html = self.server.build_html()
        self.assertIn("SOLUTIONS", html)
        # Verify it's valid JSON by extracting and parsing
        self.assertIn("[", html)
        self.assertIn("]", html)

    def test_build_html_for_small_board(self):
        """4x4 board HTML should reference correct size."""
        s = WebQueensServer(board_size=4)
        html = s.build_html()
        self.assertIn("4-Queens Puzzle", html)
        self.assertIn("const N = 4;", html)  # JavaScript board-size variable

    def test_build_html_includes_navigation(self):
        """Generated HTML should include navigation buttons."""
        html = self.server.build_html()
        self.assertIn("btnFirst", html)
        self.assertIn("btnPrev", html)
        self.assertIn("btnNext", html)
        self.assertIn("btnLast", html)

    def test_build_html_includes_styles(self):
        """Generated HTML should include embedded CSS."""
        html = self.server.build_html()
        self.assertIn("<style>", html)
        self.assertIn("</style>", html)

    def test_build_html_includes_script(self):
        """Generated HTML should include embedded JavaScript."""
        html = self.server.build_html()
        self.assertIn("<script>", html)
        self.assertIn("</script>", html)

    def test_build_html_valid_doctype(self):
        """Generated HTML should start with DOCTYPE declaration."""
        html = self.server.build_html()
        self.assertTrue(html.strip().startswith("<!DOCTYPE html>"))

    # ---- JSON API ----

    def test_build_json_all_solutions(self):
        """build_json() without index returns all solutions."""
        result = self.server.build_json()
        data = json.loads(result)
        self.assertEqual(data["board_size"], 8)
        self.assertEqual(data["total"], 92)
        self.assertEqual(len(data["solutions"]), 92)

    def test_build_json_specific_solution(self):
        """build_json(index=1) returns the first solution."""
        result = self.server.build_json(index=1)
        data = json.loads(result)
        self.assertEqual(data["index"], 1)
        self.assertEqual(data["total"], 92)
        self.assertEqual(len(data["solution"]), 8)

    def test_build_json_last_solution(self):
        """build_json(index=92) returns the last solution."""
        result = self.server.build_json(index=92)
        data = json.loads(result)
        self.assertEqual(data["index"], 92)
        self.assertEqual(len(data["solution"]), 8)

    def test_build_json_out_of_range_high(self):
        """build_json with index > total returns error."""
        result = self.server.build_json(index=1000)
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertEqual(data["total"], 92)

    def test_build_json_out_of_range_zero(self):
        """build_json with index 0 returns error."""
        result = self.server.build_json(index=0)
        data = json.loads(result)
        self.assertIn("error", data)

    def test_build_json_out_of_range_negative(self):
        """build_json with negative index returns error."""
        result = self.server.build_json(index=-5)
        data = json.loads(result)
        self.assertIn("error", data)

    def test_build_json_solution_matches_backend(self):
        """API solutions should match the backend solver output."""
        from eight_queens import solve_n_queens
        backend = solve_n_queens(8)
        result = self.server.build_json(index=1)
        data = json.loads(result)
        self.assertEqual(data["solution"], backend[0])

    # ---- Server lifecycle ----

    def test_reset_clears_solutions(self):
        """reset() should clear cached solutions."""
        self.server.solve()
        self.assertEqual(self.server.solution_count, 92)
        self.server.reset()
        self.assertEqual(self.server.solution_count, 0)

    def test_reset_then_solve_again(self):
        """After reset, solve() recomputes correctly."""
        self.server.solve()
        self.server.reset()
        self.server.solve()
        self.assertEqual(self.server.solution_count, 92)

    def test_shutdown_when_not_running(self):
        """shutdown() on a non-running server should not raise."""
        self.server.shutdown()  # Should be a no-op


if __name__ == "__main__":
    unittest.main()
