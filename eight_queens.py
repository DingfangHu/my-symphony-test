"""Eight-Queens Puzzle solver using backtracking.

Finds all valid placements of eight queens on an 8x8 chessboard such that
no two queens threaten each other (no shared row, column, or diagonal).
"""

from __future__ import annotations


class EightQueens:
    """Solver for the classic Eight-Queens Puzzle.

    Uses a backtracking algorithm to enumerate all 92 distinct solutions
    for placing 8 queens on an 8x8 board with no mutual attacks.
    """

    def __init__(self, board_size: int = 8):
        """Initialize the solver for a given board size.

        Args:
            board_size: Dimension of the NxN board (default 8).
        """
        if board_size < 4 and board_size != 1:
            raise ValueError(
                f"No solutions exist for board size {board_size}. "
                f"Use size 1 or size >= 4."
            )
        self.size = board_size
        self._solutions: list[list[int]] = []

    def solve(self) -> list[list[int]]:
        """Find all valid queen placements.

        Returns:
            A list of solutions, where each solution is a list of column
            positions (one per row, 0-indexed). For example, [0, 4, 7, 5,
            2, 6, 1, 3] means queens at (row 0, col 0), (row 1, col 4),
            ..., (row 7, col 3).
        """
        self._solutions = []
        self._backtrack(row=0, cols=set(), diag1=set(), diag2=set(), placement=[])
        return self._solutions

    def _backtrack(
        self,
        row: int,
        cols: set[int],
        diag1: set[int],
        diag2: set[int],
        placement: list[int],
    ) -> None:
        """Recursive backtracking search for valid placements.

        Args:
            row: Current row being processed (0-indexed).
            cols: Set of occupied column indices.
            diag1: Set of occupied main-diagonal indices (row - col).
            diag2: Set of occupied anti-diagonal indices (row + col).
            placement: Partial solution being built (column per row).
        """
        if row == self.size:
            self._solutions.append(placement.copy())
            return

        for col in range(self.size):
            d1 = row - col
            d2 = row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            placement.append(col)
            self._backtrack(row + 1, cols, diag1, diag2, placement)
            placement.pop()
            diag2.discard(d2)
            diag1.discard(d1)
            cols.discard(col)

    def print_solution(self, solution: list[int]) -> None:
        """Print a single solution as a readable chessboard.

        Args:
            solution: List of column positions per row (0-indexed).
        """
        for col in solution:
            line = ["."] * self.size
            line[col] = "Q"
            print(" ".join(line))
        print()

    def print_all(self, limit: int | None = None) -> None:
        """Print all solutions (or up to limit).

        Args:
            limit: Maximum number of solutions to print. None means all.
        """
        if not self._solutions:
            self.solve()
        count = min(len(self._solutions), limit) if limit else len(self._solutions)
        for i in range(count):
            print(f"Solution {i + 1}/{len(self._solutions)}:")
            self.print_solution(self._solutions[i])


if __name__ == "__main__":
    solver = EightQueens()
    solutions = solver.solve()
    print(f"Found {len(solutions)} solutions for {solver.size}x{solver.size} board.")
    print()
    solver.print_all(limit=3)
    if len(solutions) > 3:
        print(f"... and {len(solutions) - 3} more.")
