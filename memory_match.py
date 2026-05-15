"""Memory matching card game implementation.

A 4x4 grid of face-down cards (8 unique pairs). Cards flip on click.
If two cards match, they stay face up; otherwise, they flip back
after a short delay. Tracks the number of moves and declares a win
when all pairs are found.
"""

import random


class MemoryMatchGame:
    """Memory matching card game logic.

    Manages a grid of face-down cards, handles card flipping,
    match detection, move counting, and win detection.

    Attributes:
        grid_size: Number of rows/columns in the square grid.
        moves: Number of move attempts made so far.
        matched_pairs: Number of pairs successfully matched.
        waiting: True when two non-matching cards are face up
                 and awaiting flip-back.
    """

    def __init__(self, grid_size=4):
        """Initialize a new memory match game.

        Args:
            grid_size: The size of the square grid (must be >= 2 and even).

        Raises:
            ValueError: If grid_size is less than 2 or not even.
        """
        if grid_size < 2:
            raise ValueError("Grid size must be at least 2.")
        if grid_size % 2 != 0:
            raise ValueError("Grid size must be even to form pairs.")
        self.grid_size = grid_size
        self._reset()

    def _reset(self):
        """Reset the game to its initial state.

        Creates a shuffled board, resets all counters, and clears
        any pending flip state.
        """
        total_cards = self.grid_size * self.grid_size
        num_pairs = total_cards // 2
        # Create card values: 0..num_pairs-1, each appearing twice
        card_values = list(range(num_pairs)) * 2
        random.shuffle(card_values)

        self.board = []
        idx = 0
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                row.append({
                    'value': card_values[idx],
                    'face_up': False,
                    'matched': False,
                })
                idx += 1
            self.board.append(row)

        self.moves = 0
        self.first_flipped = None   # (row, col) of first card
        self.second_flipped = None  # (row, col) of second card
        self.matched_pairs = 0
        self.waiting = False        # True during the flip-back delay

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_board(self):
        """Return a deep copy of the board state.

        Returns:
            A 2D list of dicts, each containing 'value', 'face_up',
            and 'matched' keys.
        """
        return [
            [{k: v for k, v in cell.items()} for cell in row]
            for row in self.board
        ]

    def flip_card(self, row, col):
        """Attempt to flip a card at the given position.

        A card can be flipped only when it is face-down, not yet
        matched, and the game is not in a waiting state (two
        non-matching cards currently face up).

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            dict with keys:
                success: bool -- whether the flip was accepted.
                reason: str or None -- failure reason if success is False.
                match_result: 'match', 'no_match', 'pending', or None.
                waiting: bool -- True if a flip-back delay is now active.
        """
        # Bounds check
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return {
                'success': False,
                'reason': 'out_of_bounds',
                'match_result': None,
                'waiting': self.waiting,
            }

        card = self.board[row][col]

        # Card already revealed or matched
        if card['face_up'] or card['matched']:
            return {
                'success': False,
                'reason': 'already_revealed',
                'match_result': None,
                'waiting': self.waiting,
            }

        # Game is in waiting state (two non-matching cards are face up)
        if self.waiting:
            return {
                'success': False,
                'reason': 'waiting_for_flip_back',
                'match_result': None,
                'waiting': True,
            }

        # Game already won
        if self.has_won():
            return {
                'success': False,
                'reason': 'game_won',
                'match_result': None,
                'waiting': False,
            }

        # Flip the card face up
        card['face_up'] = True

        if self.first_flipped is None:
            # This is the first card of the current move
            self.first_flipped = (row, col)
            return {
                'success': True,
                'reason': None,
                'match_result': 'pending',
                'waiting': False,
            }

        # This is the second card of the current move
        self.second_flipped = (row, col)
        self.moves += 1

        r1, c1 = self.first_flipped
        val1 = self.board[r1][c1]['value']
        val2 = self.board[row][col]['value']

        if val1 == val2:
            # Cards match — keep them face up and mark as matched
            self.board[r1][c1]['matched'] = True
            self.board[row][col]['matched'] = True
            self.matched_pairs += 1
            self.first_flipped = None
            self.second_flipped = None
            return {
                'success': True,
                'reason': None,
                'match_result': 'match',
                'waiting': False,
            }

        # Cards do not match — will flip back after delay
        self.waiting = True
        return {
            'success': True,
            'reason': None,
            'match_result': 'no_match',
            'waiting': True,
        }

    def flip_back(self):
        """Flip back the two non-matching cards after the delay.

        Should be called by the UI/game loop after showing the
        non-matching cards for a short duration.

        Returns:
            True if a flip-back was performed, False if there was
            nothing to flip back.
        """
        if not self.waiting:
            return False

        r1, c1 = self.first_flipped
        r2, c2 = self.second_flipped
        self.board[r1][c1]['face_up'] = False
        self.board[r2][c2]['face_up'] = False
        self.first_flipped = None
        self.second_flipped = None
        self.waiting = False
        return True

    def has_won(self):
        """Return True if all pairs have been matched.

        Returns:
            True when the number of matched pairs equals the total
            number of pairs on the board.
        """
        total_pairs = (self.grid_size * self.grid_size) // 2
        return self.matched_pairs >= total_pairs

    def get_win_message(self):
        """Return the win message if the game is won, otherwise None.

        Returns:
            'You Win!' if all pairs are matched, None otherwise.
        """
        if self.has_won():
            return "You Win!"
        return None

    # ------------------------------------------------------------------
    # Inspection helpers (useful for testing and UI)
    # ------------------------------------------------------------------

    def get_card_value(self, row, col):
        """Get the card value at a position.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            The card's numeric value, or None if out of bounds.
        """
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return None
        return self.board[row][col]['value']

    def is_face_up(self, row, col):
        """Check whether a card is currently face up.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            True if the card is face up, False if not, None if out of bounds.
        """
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return None
        return self.board[row][col]['face_up']

    def is_matched(self, row, col):
        """Check whether a card has been successfully matched.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            True if matched, False if not, None if out of bounds.
        """
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return None
        return self.board[row][col]['matched']

    def face_up_count(self):
        """Return the number of cards currently face up."""
        count = 0
        for row in self.board:
            for cell in row:
                if cell['face_up']:
                    count += 1
        return count

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self):
        """Return a string representation of the board.

        Face-up cards show their value, face-down show '.',
        matched cards are enclosed in brackets.
        """
        lines = []
        for row in self.board:
            row_str = []
            for cell in row:
                if cell['matched']:
                    row_str.append(f"[{cell['value']}]")
                elif cell['face_up']:
                    row_str.append(f" {cell['value']} ")
                else:
                    row_str.append(" . ")
            lines.append(''.join(row_str))
        return '\n'.join(lines)
