"""Tests for eight_queens.py - verifies correctness of the N-Queens solver."""
import unittest

# Import the module under test — compile-time check plus runtime import
import eight_queens
from eight_queens import solve_n_queens, format_solution


def _is_valid_solution(solution, n):
    """Return True if the solution has no two queens attacking each other.

    A solution is a list where solution[row] = col.
    No two queens may share the same column or diagonal.
    (Rows are guaranteed distinct by construction.)
    """
    for i in range(n):
        for j in range(i + 1, n):
            if solution[i] == solution[j]:
                return False  # same column
            if abs(solution[i] - solution[j]) == abs(i - j):
                return False  # same diagonal
    return True


class TestEightQueens(unittest.TestCase):

    def test_solution_count(self):
        """The 8-queens problem has exactly 92 distinct solutions."""
        solutions = solve_n_queens(8)
        self.assertEqual(len(solutions), 92,
                         f"Expected 92 solutions, got {len(solutions)}")

    def test_all_solutions_valid(self):
        """Every returned solution must be valid (no two queens attack)."""
        solutions = solve_n_queens(8)
        for i, sol in enumerate(solutions):
            self.assertTrue(_is_valid_solution(sol, 8),
                            f"Solution {i} is invalid: {sol}")

    def test_all_solutions_unique(self):
        """All 92 solutions should be distinct."""
        solutions = solve_n_queens(8)
        unique = {tuple(sol) for sol in solutions}
        self.assertEqual(len(unique), 92,
                         "Solutions contain duplicates")

    def test_small_boards(self):
        """Known solution counts for n=1..7."""
        expected = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40}
        for n, count in expected.items():
            with self.subTest(n=n):
                solutions = solve_n_queens(n)
                self.assertEqual(len(solutions), count,
                                 f"n={n}: expected {count}, got {len(solutions)}")
                for sol in solutions:
                    self.assertTrue(_is_valid_solution(sol, n),
                                    f"Invalid solution for n={n}: {sol}")

    def test_format_solution(self):
        """format_solution should produce a board with n lines of n characters."""
        solution = [0, 4, 7, 5, 2, 6, 1, 3]  # A known valid 8-queens solution
        board_str = format_solution(solution)
        lines = board_str.strip().split('\n')
        self.assertEqual(len(lines), 8)
        for line in lines:
            tokens = line.split()
            self.assertEqual(len(tokens), 8)
            self.assertEqual(tokens.count('Q'), 1)
            self.assertEqual(tokens.count('.'), 7)


if __name__ == '__main__':
    unittest.main()
