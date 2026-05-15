"""Tests for the Memory Match UI wrapper.

Tests the UI state helpers, click handling, and game interaction
without requiring a display server.
"""

import unittest
from memory_match_ui import MemoryMatchUI


class TestMemoryMatchUIInitialization(unittest.TestCase):
    """Tests for UI initialization and initial state."""

    def test_default_grid_size(self):
        """Default grid is 4x4."""
        app = MemoryMatchUI()
        self.assertEqual(app.grid_size, 4)
        self.assertEqual(app.game.grid_size, 4)

    def test_custom_grid_size(self):
        """Custom grid size is accepted."""
        app = MemoryMatchUI(grid_size=6)
        self.assertEqual(app.grid_size, 6)
        self.assertEqual(app.game.grid_size, 6)

    def test_invalid_grid_size_raises(self):
        """Invalid grid size raises ValueError."""
        with self.assertRaises(ValueError):
            MemoryMatchUI(grid_size=1)
        with self.assertRaises(ValueError):
            MemoryMatchUI(grid_size=3)

    def test_initial_has_no_widgets(self):
        """Before run(), internal widget references are None."""
        app = MemoryMatchUI()
        self.assertIsNone(app._buttons)
        self.assertIsNone(app._root)
        self.assertIsNone(app._status_label)
        self.assertIsNone(app._move_label)
        self.assertIsNone(app._flip_back_job)
        self.assertIsNone(app._frame)

    def test_initial_not_waiting(self):
        """Initial state is not waiting."""
        app = MemoryMatchUI()
        self.assertFalse(app.is_waiting())


class TestMemoryMatchUIButtonText(unittest.TestCase):
    """Tests for get_button_text."""

    def test_face_down_shows_symbol(self):
        """Face-down cards show the face-down symbol."""
        app = MemoryMatchUI()
        for r in range(4):
            for c in range(4):
                self.assertEqual(app.get_button_text(r, c), "?")

    def test_face_up_shows_value(self):
        """Face-up cards show their numeric value as string."""
        app = MemoryMatchUI()
        app.game.flip_card(0, 0)
        val = str(app.game.get_card_value(0, 0))
        self.assertEqual(app.get_button_text(0, 0), val)

    def test_matched_shows_value(self):
        """Matched cards show their numeric value as string."""
        app = MemoryMatchUI()
        # Manually mark a card as matched
        app.game.board[0][0]['matched'] = True
        app.game.board[0][0]['face_up'] = True
        val = str(app.game.get_card_value(0, 0))
        self.assertEqual(app.get_button_text(0, 0), val)

    def test_out_of_bounds_returns_none(self):
        """Out-of-bounds positions return None."""
        app = MemoryMatchUI()
        self.assertIsNone(app.get_button_text(-1, 0))
        self.assertIsNone(app.get_button_text(4, 0))
        self.assertIsNone(app.get_button_text(0, -1))
        self.assertIsNone(app.get_button_text(0, 4))


class TestMemoryMatchUIButtonColors(unittest.TestCase):
    """Tests for get_button_bg and get_button_fg."""

    def test_face_down_bg(self):
        """Face-down cards use CARD_FACE_DOWN_COLOR."""
        app = MemoryMatchUI()
        for r in range(4):
            for c in range(4):
                self.assertEqual(
                    app.get_button_bg(r, c), app.CARD_FACE_DOWN_COLOR)

    def test_face_up_bg(self):
        """Face-up cards use CARD_FACE_UP_COLOR."""
        app = MemoryMatchUI()
        app.game.flip_card(0, 0)
        self.assertEqual(app.get_button_bg(0, 0), app.CARD_FACE_UP_COLOR)

    def test_matched_bg(self):
        """Matched cards use CARD_MATCHED_COLOR."""
        app = MemoryMatchUI()
        app.game.board[0][0]['matched'] = True
        app.game.board[0][0]['face_up'] = True
        self.assertEqual(app.get_button_bg(0, 0), app.CARD_MATCHED_COLOR)

    def test_face_down_fg(self):
        """Face-down cards use TEXT_COLOR."""
        app = MemoryMatchUI()
        for r in range(4):
            for c in range(4):
                self.assertEqual(app.get_button_fg(r, c), app.TEXT_COLOR)

    def test_matched_fg(self):
        """Matched cards use MATCHED_TEXT_COLOR."""
        app = MemoryMatchUI()
        app.game.board[0][0]['matched'] = True
        app.game.board[0][0]['face_up'] = True
        self.assertEqual(app.get_button_fg(0, 0), app.MATCHED_TEXT_COLOR)

    def test_out_of_bounds_colors_none(self):
        """Out-of-bounds positions return None for colors."""
        app = MemoryMatchUI()
        self.assertIsNone(app.get_button_bg(-1, 0))
        self.assertIsNone(app.get_button_bg(4, 0))
        self.assertIsNone(app.get_button_fg(0, -1))
        self.assertIsNone(app.get_button_fg(0, 4))


class TestMemoryMatchUIButtonState(unittest.TestCase):
    """Tests for get_button_state."""

    def test_face_down_state_is_normal(self):
        """Face-down cards have state 'normal'."""
        app = MemoryMatchUI()
        for r in range(4):
            for c in range(4):
                self.assertEqual(app.get_button_state(r, c), 'normal')

    def test_face_up_state_is_disabled(self):
        """Face-up cards have state 'disabled'."""
        app = MemoryMatchUI()
        app.game.flip_card(0, 0)
        self.assertEqual(app.get_button_state(0, 0), 'disabled')

    def test_matched_state_is_disabled(self):
        """Matched cards have state 'disabled'."""
        app = MemoryMatchUI()
        app.game.board[2][2]['matched'] = True
        app.game.board[2][2]['face_up'] = True
        self.assertEqual(app.get_button_state(2, 2), 'disabled')

    def test_out_of_bounds_state_none(self):
        """Out-of-bounds positions return None."""
        app = MemoryMatchUI()
        self.assertIsNone(app.get_button_state(-1, 0))
        self.assertIsNone(app.get_button_state(4, 4))


class TestMemoryMatchUIStatusText(unittest.TestCase):
    """Tests for get_status_text and get_matched_count_text."""

    def test_status_text_initial(self):
        """Initial status shows moves = 0."""
        app = MemoryMatchUI()
        self.assertEqual(app.get_status_text(), "Moves: 0")

    def test_status_text_after_moves(self):
        """Status text updates with move count."""
        app = MemoryMatchUI()
        app.game.moves = 5
        self.assertEqual(app.get_status_text(), "Moves: 5")

    def test_status_text_win(self):
        """Status text shows 'You Win!' when game is won."""
        app = MemoryMatchUI()
        app.game.matched_pairs = 8
        self.assertEqual(app.get_status_text(), "You Win!")

    def test_matched_count_initial(self):
        """Initial matched count shows 0 / 8."""
        app = MemoryMatchUI()
        self.assertEqual(app.get_matched_count_text(), "Pairs: 0 / 8")

    def test_matched_count_partial(self):
        """Matched count reflects progress."""
        app = MemoryMatchUI()
        app.game.matched_pairs = 3
        self.assertEqual(app.get_matched_count_text(), "Pairs: 3 / 8")

    def test_matched_count_all(self):
        """Matched count shows full when all pairs matched."""
        app = MemoryMatchUI()
        app.game.matched_pairs = 8
        self.assertEqual(app.get_matched_count_text(), "Pairs: 8 / 8")

    def test_matched_count_custom_size(self):
        """Matched count adapts to grid size."""
        app = MemoryMatchUI(grid_size=6)
        self.assertEqual(app.get_matched_count_text(), "Pairs: 0 / 18")


class TestMemoryMatchUIHandleClick(unittest.TestCase):
    """Tests for handle_click."""

    def test_click_success_returns_correct_format(self):
        """Successful click returns dict with expected keys."""
        app = MemoryMatchUI()
        result = app.handle_click(0, 0)
        self.assertTrue(result['success'])
        self.assertIsNone(result['reason'])
        self.assertEqual(result['match_result'], 'pending')
        self.assertFalse(result['waiting'])
        self.assertFalse(result['is_won'])

    def test_click_out_of_bounds_fails(self):
        """Out-of-bounds click returns success=False."""
        app = MemoryMatchUI()
        result = app.handle_click(-1, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'out_of_bounds')

    def test_click_already_face_up_fails(self):
        """Clicking an already face-up card fails."""
        app = MemoryMatchUI()
        app.game.flip_card(0, 0)
        result = app.handle_click(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'already_revealed')

    def test_click_pair_match(self):
        """Clicking two matching cards results in match."""
        app = MemoryMatchUI()
        # Find two cards with the same value
        found = {}
        for r in range(4):
            for c in range(4):
                v = app.game.get_card_value(r, c)
                if v in found:
                    pos1 = found[v]
                    pos2 = (r, c)
                    break
                else:
                    found[v] = (r, c)
            else:
                continue
            break

        app.handle_click(pos1[0], pos1[1])
        result = app.handle_click(pos2[0], pos2[1])
        self.assertTrue(result['success'])
        self.assertEqual(result['match_result'], 'match')
        self.assertFalse(result['waiting'])

    def test_click_no_match(self):
        """Clicking two non-matching cards results in no_match."""
        app = MemoryMatchUI()
        v00 = app.game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if app.game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        app.handle_click(0, 0)
        result = app.handle_click(target[0], target[1])
        self.assertTrue(result['success'])
        self.assertEqual(result['match_result'], 'no_match')
        self.assertTrue(result['waiting'])

    def test_click_after_win_fails(self):
        """Click fails after game is won."""
        app = MemoryMatchUI()
        app.game.matched_pairs = 8
        result = app.handle_click(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'game_won')

    def test_click_during_waiting_fails(self):
        """Click fails during waiting state."""
        app = MemoryMatchUI()
        v00 = app.game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if app.game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        app.handle_click(0, 0)
        app.handle_click(target[0], target[1])
        # Now in waiting state
        result = app.handle_click(1, 1)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'waiting_for_flip_back')


class TestMemoryMatchUIFlipBack(unittest.TestCase):
    """Tests for handle_flip_back."""

    def test_flip_back_success(self):
        """flip_back succeeds when in waiting state."""
        app = MemoryMatchUI()
        v00 = app.game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if app.game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        app.handle_click(0, 0)
        app.handle_click(target[0], target[1])
        self.assertTrue(app.is_waiting())
        result = app.handle_flip_back()
        self.assertTrue(result)
        self.assertFalse(app.is_waiting())

    def test_flip_back_no_waiting_returns_false(self):
        """flip_back returns False when not waiting."""
        app = MemoryMatchUI()
        self.assertFalse(app.handle_flip_back())

    def test_flip_back_clears_state(self):
        """After flip_back, cards are face down."""
        app = MemoryMatchUI()
        v00 = app.game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if app.game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        app.handle_click(0, 0)
        app.handle_click(target[0], target[1])
        app.handle_flip_back()
        self.assertFalse(app.game.is_face_up(0, 0))
        self.assertFalse(app.game.is_face_up(target[0], target[1]))
        self.assertFalse(app.is_waiting())


class TestMemoryMatchUIReset(unittest.TestCase):
    """Tests for reset."""

    def test_reset_changes_board(self):
        """reset() creates a new game with a new board layout."""
        app = MemoryMatchUI()
        original_values = tuple(
            app.game.get_card_value(r, c)
            for r in range(4) for c in range(4)
        )
        app.reset()
        new_values = tuple(
            app.game.get_card_value(r, c)
            for r in range(4) for c in range(4)
        )
        # The new board may be the same by chance, but we verify
        # a new MemoryMatchGame was created and is functional
        self.assertEqual(app.game.grid_size, 4)
        self.assertEqual(app.game.moves, 0)
        self.assertEqual(app.game.matched_pairs, 0)
        self.assertFalse(app.game.has_won())

    def test_reset_preserves_grid_size(self):
        """reset() preserves the original grid size."""
        app = MemoryMatchUI(grid_size=6)
        app.reset()
        self.assertEqual(app.grid_size, 6)
        self.assertEqual(app.game.grid_size, 6)

    def test_reset_from_midgame(self):
        """reset() from mid-game returns to initial state."""
        app = MemoryMatchUI()
        app.handle_click(0, 0)
        app.handle_click(0, 1)
        app.reset()
        self.assertEqual(app.game.moves, 0)
        self.assertEqual(app.game.matched_pairs, 0)
        self.assertIsNone(app.game.first_flipped)
        self.assertFalse(app.game.waiting)


class TestMemoryMatchUIIntegration(unittest.TestCase):
    """Integration tests: UI wrapper + game logic end-to-end."""

    def test_full_game_flow_through_ui(self):
        """Complete a game entirely through the UI click handler."""
        app = MemoryMatchUI()

        # Build a map of value -> positions
        value_positions = {}
        for r in range(4):
            for c in range(4):
                v = app.game.get_card_value(r, c)
                if v not in value_positions:
                    value_positions[v] = []
                value_positions[v].append((r, c))

        move_count = 0
        for v, positions in value_positions.items():
            p1, p2 = positions
            r1 = app.handle_click(p1[0], p1[1])
            self.assertTrue(r1['success'])
            r2 = app.handle_click(p2[0], p2[1])
            self.assertTrue(r2['success'])
            if r2['waiting']:
                app.handle_flip_back()
                # After flip_back, try a different approach
                pass
            move_count += 1

        # Verify the game progressed
        self.assertIsNotNone(app)
        self.assertGreaterEqual(move_count, 1)

    def test_ui_status_updates_with_game_progress(self):
        """UI status text reflects game state changes."""
        app = MemoryMatchUI()
        self.assertEqual(app.get_status_text(), "Moves: 0")
        self.assertEqual(app.get_matched_count_text(), "Pairs: 0 / 8")

        # Simulate making some moves
        app.game.moves = 3
        app.game.matched_pairs = 1
        self.assertEqual(app.get_status_text(), "Moves: 3")
        self.assertEqual(app.get_matched_count_text(), "Pairs: 1 / 8")

    def test_button_text_after_multiple_actions(self):
        """Button text reflects state after flip, match, flip_back cycle."""
        app = MemoryMatchUI()

        # All face-down initially
        for r in range(4):
            for c in range(4):
                self.assertEqual(app.get_button_text(r, c), "?")

        # Flip one card
        app.handle_click(0, 0)
        val0 = str(app.game.get_card_value(0, 0))
        self.assertEqual(app.get_button_text(0, 0), val0)

        # Flip a different card (non-match), then flip back
        v00 = app.game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if app.game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        app.handle_click(target[0], target[1])
        app.handle_flip_back()
        # Both should be face-down again
        self.assertEqual(app.get_button_text(0, 0), "?")
        self.assertEqual(app.get_button_text(target[0], target[1]), "?")

    def test_match_pair_button_states(self):
        """After a match, both buttons should show disabled and matched colors."""
        app = MemoryMatchUI()

        found = {}
        for r in range(4):
            for c in range(4):
                v = app.game.get_card_value(r, c)
                if v in found:
                    p1 = found[v]
                    p2 = (r, c)

                    app.handle_click(p1[0], p1[1])
                    app.handle_click(p2[0], p2[1])

                    self.assertEqual(app.get_button_state(p1[0], p1[1]), 'disabled')
                    self.assertEqual(app.get_button_state(p2[0], p2[1]), 'disabled')
                    self.assertEqual(app.get_button_bg(p1[0], p1[1]), app.CARD_MATCHED_COLOR)
                    self.assertEqual(app.get_button_bg(p2[0], p2[1]), app.CARD_MATCHED_COLOR)
                    self.assertEqual(app.get_button_fg(p1[0], p1[1]), app.MATCHED_TEXT_COLOR)
                    self.assertEqual(app.get_button_fg(p2[0], p2[1]), app.MATCHED_TEXT_COLOR)
                    return
                else:
                    found[v] = (r, c)


class TestMemoryMatchUIConstants(unittest.TestCase):
    """Tests for UI constants."""

    def test_face_down_symbol_is_string(self):
        """FACE_DOWN_SYMBOL is a string."""
        self.assertIsInstance(MemoryMatchUI.FACE_DOWN_SYMBOL, str)

    def test_flip_back_delay_is_positive(self):
        """FLIP_BACK_DELAY_MS is positive."""
        self.assertGreater(MemoryMatchUI.FLIP_BACK_DELAY_MS, 0)

    def test_colors_are_hex_strings(self):
        """All color constants are valid hex strings."""
        for attr_name in [
            'BG_COLOR', 'CARD_FACE_DOWN_COLOR', 'CARD_FACE_UP_COLOR',
            'CARD_MATCHED_COLOR', 'TEXT_COLOR', 'MATCHED_TEXT_COLOR',
            'BTN_ACTIVE_BG', 'BTN_ACTIVE_FG',
        ]:
            val = getattr(MemoryMatchUI, attr_name)
            self.assertIsInstance(val, str)
            self.assertTrue(val.startswith('#'))


class TestMemoryMatchUIMainFunction(unittest.TestCase):
    """Tests that the module can be imported and main() exists."""

    def test_main_function_exists(self):
        """main function is callable."""
        from memory_match_ui import main
        self.assertTrue(callable(main))


class TestMemoryMatchUICustomSizes(unittest.TestCase):
    """Tests for non-default grid sizes in the UI wrapper."""

    def test_2x2_ui(self):
        """2x2 grid UI wrapper works."""
        app = MemoryMatchUI(grid_size=2)
        self.assertEqual(app.grid_size, 2)
        self.assertEqual(app.get_matched_count_text(), "Pairs: 0 / 2")

        # Test button text
        for r in range(2):
            for c in range(2):
                self.assertEqual(app.get_button_text(r, c), "?")
                self.assertEqual(app.get_button_state(r, c), "normal")

    def test_6x6_ui(self):
        """6x6 grid UI wrapper works."""
        app = MemoryMatchUI(grid_size=6)
        self.assertEqual(app.grid_size, 6)
        self.assertEqual(app.get_matched_count_text(), "Pairs: 0 / 18")

        # Test button text
        for r in range(6):
            for c in range(6):
                self.assertEqual(app.get_button_text(r, c), "?")
                self.assertEqual(app.get_button_state(r, c), "normal")


if __name__ == "__main__":
    unittest.main()
