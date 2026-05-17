"""Tkinter GUI for the Eight-Queens Puzzle solver.

Wraps the EightQueens solver in a graphical interface,
separating UI rendering from puzzle logic. All solving
is handled by eight_queens.EightQueens.

Usage:
    python3 eight_queens_ui.py
"""

import tkinter as tk

from eight_queens import EightQueens


class EightQueensUI:
    """Tkinter-based graphical interface for the Eight-Queens Puzzle.

    Displays a chessboard with queen placements and navigation controls
    to browse through all solutions. Delegates solving to EightQueens.

    Attributes:
        solver: The underlying EightQueens solver instance.
        board_size: Board dimension (rows/columns).
        solutions: List of all valid solutions.
    """

    # Display constants
    QUEEN_SYMBOL = "\u2655"
    EMPTY_SYMBOL = ""

    # Color scheme (light square / dark square pattern)
    LIGHT_SQUARE = "#f0d9b5"
    DARK_SQUARE = "#b58863"
    QUEEN_COLOR = "#1a1a2e"
    BG_COLOR = "#2d2d2d"
    LABEL_FG = "#ffffff"
    BUTTON_BG = "#4a4a4a"
    BUTTON_FG = "#ffffff"
    BUTTON_ACTIVE_BG = "#e94560"
    BUTTON_ACTIVE_FG = "#ffffff"
    LABEL_FONT = ("Helvetica", 16)
    HEADER_FONT = ("Helvetica", 20, "bold")
    NAV_FONT = ("Helvetica", 14, "bold")

    def __init__(self, board_size: int = 8):
        """Initialize the UI wrapper without creating Tk widgets.

        Args:
            board_size: Board size for EightQueens solver (default 8).

        Raises:
            ValueError: If board_size is invalid (no solutions exist).
        """
        self.solver = EightQueens(board_size=board_size)
        self.board_size = board_size
        self.solutions: "list[list[int]]" = []
        self._current_index: int = -1
        self._buttons: "list[list]" = []
        self._info_label = None
        self._root = None
        self._frame = None

    # ------------------------------------------------------------------
    # Navigation helpers (testable without Tk)
    # ------------------------------------------------------------------

    @property
    def current_index(self) -> int:
        """Return the 1-based index of the currently displayed solution.

        Returns 0 if no solution has been loaded.
        """
        return self._current_index + 1 if self._current_index >= 0 else 0

    @property
    def solution_count(self) -> int:
        """Return the total number of solutions."""
        return len(self.solutions)

    def _ensure_solved(self) -> None:
        """Solve if solutions haven't been computed yet."""
        if not self.solutions:
            self.solutions = self.solver.solve()

    def has_solutions(self) -> bool:
        """Return True if the solver has found solutions."""
        self._ensure_solved()
        return len(self.solutions) > 0

    def load_solution(self, index: int) -> bool:
        """Load a solution by 1-based index.

        Args:
            index: 1-based solution index.

        Returns:
            True if the solution was loaded, False if index is out of range.
        """
        self._ensure_solved()
        if not self.solutions:
            return False
        if index < 1 or index > len(self.solutions):
            return False
        self._current_index = index - 1
        return True

    def first_solution(self) -> bool:
        """Navigate to the first solution.

        Returns True on success.
        """
        return self.load_solution(1)

    def last_solution(self) -> bool:
        """Navigate to the last solution.

        Returns True on success.
        """
        self._ensure_solved()
        return self.load_solution(len(self.solutions))

    def next_solution(self) -> bool:
        """Navigate to the next solution.

        Returns True on success, False if already at the last solution.
        """
        self._ensure_solved()
        if not self.solutions:
            return False
        if self._current_index + 1 >= len(self.solutions):
            return False
        self._current_index += 1
        return True

    def prev_solution(self) -> bool:
        """Navigate to the previous solution.

        Returns True on success, False if already at the first solution.
        """
        self._ensure_solved()
        if not self.solutions:
            return False
        if self._current_index <= 0:
            return False
        self._current_index -= 1
        return True

    def get_current_solution(self):
        """Return the current solution (list of column positions), or None."""
        self._ensure_solved()
        if self._current_index < 0 or self._current_index >= len(self.solutions):
            return None
        return list(self.solutions[self._current_index])

    def get_cell_symbol(self, row: int, col: int) -> str:
        """Get the display symbol for cell (row, col).

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            The queen symbol if a queen is at this cell, otherwise empty.
        """
        solution = self.get_current_solution()
        if solution is None:
            return self.EMPTY_SYMBOL
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return self.EMPTY_SYMBOL
        return self.QUEEN_SYMBOL if solution[row] == col else self.EMPTY_SYMBOL

    def get_cell_bg(self, row: int, col: int) -> str:
        """Get the background color for cell (row, col).

        Returns light or dark square color.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            Hex color string.
        """
        return self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE

    def get_info_text(self) -> str:
        """Get the current status text for the UI.

        Returns a string showing the current solution number / total.
        """
        if not self.solutions:
            return "Solving..."
        if self._current_index < 0:
            return f"{len(self.solutions)} solutions found"
        return f"Solution {self._current_index + 1} / {len(self.solutions)}"

    def reset(self) -> None:
        """Reset UI state and re-solve."""
        self.solver = EightQueens(board_size=self.board_size)
        self.solutions = []
        self._current_index = -1

    # ------------------------------------------------------------------
    # Tkinter rendering
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the full Tkinter interface inside the root window."""
        if self._root is None:
            return
        self._root.title("Eight Queens Puzzle")
        self._root.configure(bg=self.BG_COLOR)
        self._root.resizable(False, False)

        # Header
        header = tk.Label(
            self._root,
            text=f"{self.board_size}-Queens Puzzle",
            font=self.HEADER_FONT,
            fg=self.LABEL_FG,
            bg=self.BG_COLOR,
        )
        header.pack(pady=(15, 5))

        # Info label
        self._info_label = tk.Label(
            self._root,
            text=self.get_info_text(),
            font=self.LABEL_FONT,
            fg=self.LABEL_FG,
            bg=self.BG_COLOR,
        )
        self._info_label.pack(pady=(0, 10))

        # Chessboard frame
        self._frame = tk.Frame(self._root, bg=self.BG_COLOR)
        self._frame.pack(pady=5, padx=20)

        # Build the board grid
        self._buttons.clear()
        for r in range(self.board_size):
            row_buttons = []
            for c in range(self.board_size):
                btn = tk.Button(
                    self._frame,
                    text=self.get_cell_symbol(r, c),
                    font=("Helvetica", 20),
                    width=3,
                    height=1,
                    bg=self.get_cell_bg(r, c),
                    fg=self.QUEEN_COLOR,
                    activebackground=self.get_cell_bg(r, c),
                    relief=tk.FLAT,
                    state=tk.DISABLED,
                    disabledforeground=self.QUEEN_COLOR,
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                row_buttons.append(btn)
            self._buttons.append(row_buttons)

        # Navigation frame
        nav_frame = tk.Frame(self._root, bg=self.BG_COLOR)
        nav_frame.pack(pady=(10, 5))

        buttons = [
            ("|< First", lambda: self._on_navigate(self.first_solution)),
            ("< Prev", lambda: self._on_navigate(self.prev_solution)),
            ("Next >", lambda: self._on_navigate(self.next_solution)),
            ("Last >|", lambda: self._on_navigate(self.last_solution)),
        ]
        for text, cmd in buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=self.NAV_FONT,
                bg=self.BUTTON_BG,
                fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG,
                activeforeground=self.BUTTON_ACTIVE_FG,
                command=cmd,
                width=8,
            ).pack(side=tk.LEFT, padx=4)

    def _on_navigate(self, nav_func) -> None:
        """Internal handler: navigate to a solution and refresh the board.

        Args:
            nav_func: Navigation function to call (returns bool).
        """
        if nav_func():
            self._refresh_board()
            self._update_info()

    def _refresh_cell(self, row: int, col: int) -> None:
        """Refresh a single cell's appearance from current solution."""
        if not self._buttons or row >= len(self._buttons):
            return
        btn = self._buttons[row][col]
        if btn is not None:
            btn.configure(text=self.get_cell_symbol(row, col))

    def _refresh_board(self) -> None:
        """Refresh all board cells to match the current solution."""
        for r in range(self.board_size):
            for c in range(self.board_size):
                self._refresh_cell(r, c)

    def _update_info(self) -> None:
        """Update the info label."""
        if self._info_label is not None:
            self._info_label.configure(text=self.get_info_text())

    # ------------------------------------------------------------------
    # Public launch method
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Launch the Tkinter main loop. Blocks until the window is closed."""
        self._ensure_solved()
        if self.solutions:
            self.load_solution(1)
        self._root = tk.Tk()
        self._build_ui()
        self._root.mainloop()
        self._root = None


def main() -> None:
    """Entry point: create and run the Eight Queens UI."""
    app = EightQueensUI(board_size=8)
    app.run()


if __name__ == "__main__":
    main()
