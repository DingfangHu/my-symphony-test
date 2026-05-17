"""Solve the Eight-Queens problem using backtracking.

Place 8 queens on an 8x8 chessboard so that no two queens attack each other.
Two queens attack if they share the same row, column, or diagonal.

Returns all 92 distinct solutions. Each solution is represented as a list
of 8 column indices: board[row] = column.
"""


def solve_n_queens(n=8):
    """Return all distinct solutions to the N-Queens problem.

    Uses backtracking. board[i] stores the column position of the queen
    placed in row i.

    Args:
        n: Board size (default 8 for the classic Eight-Queens problem).

    Returns:
        A list of solutions, each being a list of n column indices.
    """
    solutions = []
    board = [-1] * n

    def is_safe(row, col):
        """Check if placing a queen at (row, col) is safe."""
        for prev_row in range(row):
            if board[prev_row] == col:
                return False
            if abs(board[prev_row] - col) == abs(prev_row - row):
                return False
        return True

    def backtrack(row):
        """Recursively place queens row by row."""
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1

    backtrack(0)
    return solutions


def format_solution(solution):
    """Format a solution as a printable board string.

    Args:
        solution: A list of column indices (board[row] = col).

    Returns:
        Multi-line string representing the board with 'Q' for a queen
        and '.' for an empty square.
    """
    n = len(solution)
    lines = []
    for row in range(n):
        line = ['.'] * n
        line[solution[row]] = 'Q'
        lines.append(' '.join(line))
    return '\n'.join(lines)


if __name__ == '__main__':
    solutions = solve_n_queens(8)
    print(f"Found {len(solutions)} solutions to the Eight-Queens problem.")
    print("\nFirst solution:")
    print(format_solution(solutions[0]))
    print("\nLast solution:")
    print(format_solution(solutions[-1]))
