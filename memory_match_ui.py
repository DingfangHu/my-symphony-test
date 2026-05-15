"""Tkinter GUI for the Memory Match card game.

Wraps the MemoryMatchGame logic in a graphical interface,
separating UI rendering from game logic. All game rules
are handled by memory_match.MemoryMatchGame.

Usage:
    python3 memory_match_ui.py
"""

import tkinter as tk
from memory_match import MemoryMatchGame


class MemoryMatchUI:
    """Tkinter-based graphical interface for the Memory Match game.

    Provides a clickable card grid, move counter, status display,
    and new-game button. Delegates all game logic to MemoryMatchGame.

    Attributes:
        game: The underlying MemoryMatchGame instance.
        grid_size: Board dimension (rows/columns).
    """

    # Display constants
    FACE_DOWN_SYMBOL = "?"
    FLIP_BACK_DELAY_MS = 800

    # Color scheme
    BG_COLOR = "#1a1a2e"
    CARD_FACE_DOWN_COLOR = "#16213e"
    CARD_FACE_UP_COLOR = "#0f3460"
    CARD_MATCHED_COLOR = "#533483"
    TEXT_COLOR = "#e94560"
    MATCHED_TEXT_COLOR = "#a0ffa0"
    BUTTON_FONT = ("Helvetica", 24, "bold")
    LABEL_FONT = ("Helvetica", 16)
    WIN_FONT = ("Helvetica", 20, "bold")
    BTN_ACTIVE_BG = "#e94560"
    BTN_ACTIVE_FG = "#ffffff"

    def __init__(self, grid_size=4):
        """Initialize the UI wrapper without creating Tk widgets.

        Args:
            grid_size: Board size for MemoryMatchGame (must be >= 2 and even).

        Raises:
            ValueError: If grid_size is invalid.
        """
        self.game = MemoryMatchGame(grid_size=grid_size)
        self.grid_size = grid_size
        self._buttons = None
        self._move_label = None
        self._status_label = None
        self._root = None
        self._flip_back_job = None
        self._frame = None

    # ------------------------------------------------------------------
    # UI state helpers (testable without Tk)
    # ------------------------------------------------------------------

    def get_button_text(self, row, col):
        """Get the text to display on the card button at (row, col).

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            The card value string if face up or matched, otherwise
            the face-down symbol. Returns None if out of bounds.
        """
        if self.game.is_matched(row, col):
            return str(self.game.get_card_value(row, col))
        if self.game.is_face_up(row, col):
            return str(self.game.get_card_value(row, col))
        if self.game.get_card_value(row, col) is not None:
            return self.FACE_DOWN_SYMBOL
        return None

    def get_button_bg(self, row, col):
        """Get the background color for the button at (row, col).

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            Color hex string based on card state, or None if out of bounds.
        """
        if self.game.is_matched(row, col):
            return self.CARD_MATCHED_COLOR
        if self.game.is_face_up(row, col):
            return self.CARD_FACE_UP_COLOR
        if self.game.get_card_value(row, col) is not None:
            return self.CARD_FACE_DOWN_COLOR
        return None

    def get_button_fg(self, row, col):
        """Get the foreground (text) color for the button at (row, col).

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            Color hex string, or None if out of bounds.
        """
        if self.game.is_matched(row, col):
            return self.MATCHED_TEXT_COLOR
        if self.game.get_card_value(row, col) is not None:
            return self.TEXT_COLOR
        return None

    def get_button_state(self, row, col):
        """Get the Tk button state for the card at (row, col).

        Returns 'disabled' for matched or face-up cards, 'normal' otherwise.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            'normal', 'disabled', or None if out of bounds.
        """
        if self.game.is_matched(row, col):
            return 'disabled'
        if self.game.is_face_up(row, col):
            return 'disabled'
        if self.game.get_card_value(row, col) is not None:
            return 'normal'
        return None

    def get_status_text(self):
        """Get the current status text for the UI.

        Returns:
            Win message if won, otherwise a string with the move count.
        """
        if self.game.has_won():
            return self.game.get_win_message() or "You Win!"
        return f"Moves: {self.game.moves}"

    def get_matched_count_text(self):
        """Get a string showing matched pairs progress.

        Returns:
            e.g. 'Pairs: 3 / 8' for a 4x4 board.
        """
        total = (self.grid_size * self.grid_size) // 2
        return f"Pairs: {self.game.matched_pairs} / {total}"

    def is_waiting(self):
        """Return True if the game is in the waiting state (non-matching
        cards are face up, awaiting flip-back).
        """
        return self.game.waiting

    # ------------------------------------------------------------------
    # Click handling (testable logic)
    # ------------------------------------------------------------------

    def handle_click(self, row, col):
        """Handle a card click at (row, col).

        Delegates to MemoryMatchGame.flip_card and returns a
        structured result dict.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            dict with keys:
                success: bool
                reason: str or None
                match_result: 'match', 'no_match', 'pending', or None
                waiting: bool
                is_won: bool
        """
        result = self.game.flip_card(row, col)
        return {
            'success': result['success'],
            'reason': result['reason'],
            'match_result': result['match_result'],
            'waiting': result['waiting'],
            'is_won': self.game.has_won(),
        }

    def handle_flip_back(self):
        """Trigger flip_back for non-matching cards.

        Delegates to MemoryMatchGame.flip_back.

        Returns:
            True if cards were flipped back, False otherwise.
        """
        return self.game.flip_back()

    def reset(self):
        """Reset the game to its initial state with new board layout."""
        self.game = MemoryMatchGame(grid_size=self.grid_size)

    # ------------------------------------------------------------------
    # Tkinter rendering (requires Tk root)
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the full Tkinter interface inside the root window."""
        self._root.title("Memory Match")
        self._root.configure(bg=self.BG_COLOR)
        self._root.resizable(False, False)

        # Top frame for info labels
        info_frame = tk.Frame(self._root, bg=self.BG_COLOR)
        info_frame.pack(pady=(15, 5))

        self._status_label = tk.Label(
            info_frame, text=self.get_status_text(),
            font=self.LABEL_FONT, fg=self.TEXT_COLOR, bg=self.BG_COLOR,
        )
        self._status_label.pack(side=tk.LEFT, padx=20)

        self._move_label = tk.Label(
            info_frame, text=self.get_matched_count_text(),
            font=self.LABEL_FONT, fg=self.TEXT_COLOR, bg=self.BG_COLOR,
        )
        self._move_label.pack(side=tk.LEFT, padx=20)

        # Card grid frame
        self._frame = tk.Frame(self._root, bg=self.BG_COLOR)
        self._frame.pack(pady=10, padx=10)

        # Create the button grid
        self._buttons = []
        for r in range(self.grid_size):
            row_buttons = []
            for c in range(self.grid_size):
                btn = tk.Button(
                    self._frame,
                    text=self.get_button_text(r, c),
                    font=self.BUTTON_FONT,
                    width=4, height=2,
                    bg=self.get_button_bg(r, c),
                    fg=self.get_button_fg(r, c),
                    activebackground=self.BTN_ACTIVE_BG,
                    activeforeground=self.BTN_ACTIVE_FG,
                    relief=tk.RAISED,
                    command=lambda row=r, col=c: self._on_card_click(row, col),
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
            self._buttons.append(row_buttons)

        # Bottom frame for New Game button
        bottom_frame = tk.Frame(self._root, bg=self.BG_COLOR)
        bottom_frame.pack(pady=(5, 15))

        new_game_btn = tk.Button(
            bottom_frame,
            text="New Game",
            font=self.LABEL_FONT,
            bg=self.CARD_MATCHED_COLOR,
            fg=self.MATCHED_TEXT_COLOR,
            activebackground=self.BTN_ACTIVE_BG,
            activeforeground=self.BTN_ACTIVE_FG,
            command=self._on_new_game,
        )
        new_game_btn.pack()

    def _on_card_click(self, row, col):
        """Internal handler: called when a card button is clicked."""
        click_result = self.handle_click(row, col)
        if not click_result['success']:
            return

        self._refresh_all_buttons()

        if click_result['match_result'] == 'no_match' and click_result['waiting']:
            # Schedule flip-back after delay
            self._flip_back_job = self._root.after(
                self.FLIP_BACK_DELAY_MS, self._on_flip_back,
            )
        elif click_result['is_won']:
            self._update_labels()

    def _on_flip_back(self):
        """Internal handler: flip back non-matching cards and refresh."""
        self.handle_flip_back()
        self._flip_back_job = None
        self._refresh_all_buttons()
        self._update_labels()

    def _on_new_game(self):
        """Internal handler: reset and rebuild the UI."""
        self.reset()
        self._frame.destroy()
        self._buttons = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI refresh helpers
    # ------------------------------------------------------------------

    def _refresh_button(self, row, col):
        """Refresh a single button's appearance from game state."""
        if self._buttons is None:
            return
        btn = self._buttons[row][col]
        btn.configure(
            text=self.get_button_text(row, col),
            bg=self.get_button_bg(row, col),
            fg=self.get_button_fg(row, col),
            state=self.get_button_state(row, col),
        )

    def _refresh_all_buttons(self):
        """Refresh all buttons to match current game state."""
        if self._buttons is None:
            return
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self._refresh_button(r, c)

    def _update_labels(self):
        """Update the status and move labels."""
        if self._status_label is not None:
            self._status_label.configure(text=self.get_status_text())
        if self._move_label is not None:
            self._move_label.configure(text=self.get_matched_count_text())

    # ------------------------------------------------------------------
    # Public launch method
    # ------------------------------------------------------------------

    def run(self):
        """Launch the Tkinter main loop. Blocks until the window is closed."""
        self._root = tk.Tk()
        self._build_ui()
        self._root.mainloop()
        self._root = None


def main():
    """Entry point: create and run the Memory Match UI."""
    app = MemoryMatchUI(grid_size=4)
    app.run()


if __name__ == "__main__":
    main()
