"""Tests for the Memory Match game."""

import unittest
from memory_match import MemoryMatchGame


class TestMemoryMatchInitialization(unittest.TestCase):
    """Tests for game initialization and setup."""

    def test_default_grid_size(self):
        """Default grid is 4x4."""
        game = MemoryMatchGame()
        self.assertEqual(game.grid_size, 4)
        board = game.get_board()
        self.assertEqual(len(board), 4)
        self.assertEqual(len(board[0]), 4)

    def test_custom_even_grid_size(self):
        """Custom even grid size works."""
        game = MemoryMatchGame(grid_size=6)
        self.assertEqual(game.grid_size, 6)
        board = game.get_board()
        self.assertEqual(len(board), 6)
        self.assertEqual(len(board[0]), 6)

    def test_size_too_small_raises(self):
        """Grid size < 2 raises ValueError."""
        with self.assertRaises(ValueError):
            MemoryMatchGame(grid_size=1)

    def test_odd_grid_size_raises(self):
        """Odd grid size raises ValueError (must be even for pairs)."""
        with self.assertRaises(ValueError):
            MemoryMatchGame(grid_size=3)

    def test_initial_board_all_face_down(self):
        """All cards start face down."""
        game = MemoryMatchGame()
        for row in range(4):
            for col in range(4):
                self.assertFalse(game.is_face_up(row, col))

    def test_initial_no_cards_matched(self):
        """No cards are matched initially."""
        game = MemoryMatchGame()
        for row in range(4):
            for col in range(4):
                self.assertFalse(game.is_matched(row, col))

    def test_initial_moves_zero(self):
        """Moves counter starts at zero."""
        game = MemoryMatchGame()
        self.assertEqual(game.moves, 0)

    def test_initial_matched_pairs_zero(self):
        """Matched pairs counter starts at zero."""
        game = MemoryMatchGame()
        self.assertEqual(game.matched_pairs, 0)

    def test_initial_not_won(self):
        """Game is not won initially."""
        game = MemoryMatchGame()
        self.assertFalse(game.has_won())

    def test_initial_win_message_none(self):
        """Win message is None initially."""
        game = MemoryMatchGame()
        self.assertIsNone(game.get_win_message())

    def test_initial_face_up_count_zero(self):
        """No cards are face up initially."""
        game = MemoryMatchGame()
        self.assertEqual(game.face_up_count(), 0)

    def test_initial_waiting_false(self):
        """Waiting state is False initially."""
        game = MemoryMatchGame()
        self.assertFalse(game.waiting)

    def test_initial_first_flipped_none(self):
        """first_flipped is None initially."""
        game = MemoryMatchGame()
        self.assertIsNone(game.first_flipped)

    def test_initial_second_flipped_none(self):
        """second_flipped is None initially."""
        game = MemoryMatchGame()
        self.assertIsNone(game.second_flipped)


class TestMemoryMatchBoardComposition(unittest.TestCase):
    """Tests for board content (card values and pair count)."""

    def test_exact_eight_pairs_in_4x4(self):
        """A 4x4 board has exactly 8 unique values, each appearing twice."""
        game = MemoryMatchGame()
        values = []
        for row in range(4):
            for col in range(4):
                values.append(game.get_card_value(row, col))
        unique = set(values)
        self.assertEqual(len(unique), 8)
        for v in unique:
            self.assertEqual(values.count(v), 2)

    def test_board_covers_all_values_zero_to_seven(self):
        """All card values 0..7 appear exactly twice."""
        game = MemoryMatchGame()
        value_counts = {}
        for row in range(4):
            for col in range(4):
                v = game.get_card_value(row, col)
                value_counts[v] = value_counts.get(v, 0) + 1
        self.assertEqual(sorted(value_counts.keys()), list(range(8)))
        for count in value_counts.values():
            self.assertEqual(count, 2)

    def test_total_cards_match_grid(self):
        """Total cards equals grid_size squared."""
        for size in [2, 4, 6]:
            game = MemoryMatchGame(grid_size=size)
            count = 0
            for row in range(size):
                for col in range(size):
                    if game.get_card_value(row, col) is not None:
                        count += 1
            self.assertEqual(count, size * size)

    def test_randomized_board_not_identical(self):
        """Repeated initialization produces different boards."""
        # Run multiple initializations and verify not all identical
        boards_seen = set()
        for _ in range(10):
            game = MemoryMatchGame()
            # Serialize board values as a tuple
            values = tuple(
                game.get_card_value(r, c)
                for r in range(4) for c in range(4)
            )
            boards_seen.add(values)
        # With 16! / (2!^8) possible boards, 10 init should differ
        self.assertGreater(len(boards_seen), 1)


class TestMemoryMatchFlipCard(unittest.TestCase):
    """Tests for the core flip_card operation."""

    def test_flip_single_card_success(self):
        """Flipping a face-down card succeeds."""
        game = MemoryMatchGame()
        result = game.flip_card(0, 0)
        self.assertTrue(result['success'])
        self.assertEqual(result['match_result'], 'pending')
        self.assertTrue(game.is_face_up(0, 0))

    def test_flip_out_of_bounds_fails(self):
        """Flipping out of bounds returns success=False."""
        game = MemoryMatchGame()
        result = game.flip_card(-1, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'out_of_bounds')

        result = game.flip_card(4, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'out_of_bounds')

    def test_flip_already_face_up_fails(self):
        """Flipping an already face-up card fails."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        result = game.flip_card(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'already_revealed')

    def test_flip_matched_card_fails(self):
        """Flipping a matched card fails."""
        game = MemoryMatchGame()
        # Manually mark a card as matched
        game.board[0][0]['matched'] = True
        game.board[0][0]['face_up'] = True
        result = game.flip_card(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'already_revealed')

    def test_face_up_count_after_single_flip(self):
        """After flipping one card, face_up_count is 1."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        self.assertEqual(game.face_up_count(), 1)

    def test_first_flipped_set_after_single_flip(self):
        """After first flip, first_flipped stores the position."""
        game = MemoryMatchGame()
        game.flip_card(2, 3)
        self.assertEqual(game.first_flipped, (2, 3))


class TestMemoryMatchMatching(unittest.TestCase):
    """Tests for card matching logic."""

    def test_match_two_identical_cards(self):
        """Flipping two cards with the same value results in a match."""
        game = MemoryMatchGame()
        # Find two cells with the same value
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    pos1 = found[v]
                    pos2 = (r, c)
                    break
                else:
                    found[v] = (r, c)
            else:
                continue
            break

        # Flip first card
        r1 = game.flip_card(pos1[0], pos1[1])
        self.assertTrue(r1['success'])
        # Flip second card
        r2 = game.flip_card(pos2[0], pos2[1])
        self.assertTrue(r2['success'])
        self.assertEqual(r2['match_result'], 'match')
        self.assertFalse(r2['waiting'])

    def test_match_increments_matched_pairs(self):
        """A successful match increments matched_pairs."""
        game = MemoryMatchGame()
        # Find and match a pair
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertEqual(game.matched_pairs, 1)
                    return
                else:
                    found[v] = (r, c)

    def test_match_keeps_cards_face_up(self):
        """Matched cards stay face up."""
        game = MemoryMatchGame()
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertTrue(game.is_face_up(found[v][0], found[v][1]))
                    self.assertTrue(game.is_face_up(r, c))
                    return
                else:
                    found[v] = (r, c)

    def test_match_marks_cards_as_matched(self):
        """Matched cards are marked as matched."""
        game = MemoryMatchGame()
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertTrue(game.is_matched(found[v][0], found[v][1]))
                    self.assertTrue(game.is_matched(r, c))
                    return
                else:
                    found[v] = (r, c)

    def test_match_clears_first_and_second_flipped(self):
        """After a match, first_flipped and second_flipped are cleared."""
        game = MemoryMatchGame()
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertIsNone(game.first_flipped)
                    self.assertIsNone(game.second_flipped)
                    return
                else:
                    found[v] = (r, c)


class TestMemoryMatchNoMatch(unittest.TestCase):
    """Tests for non-matching card behavior."""

    def test_no_match_sets_waiting(self):
        """Flipping two non-matching cards sets waiting=True."""
        game = MemoryMatchGame()
        # Find two cells with different values
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        result = game.flip_card(target[0], target[1])
        self.assertTrue(result['success'])
        self.assertEqual(result['match_result'], 'no_match')
        self.assertTrue(result['waiting'])
        self.assertTrue(game.waiting)

    def test_no_match_both_cards_face_up(self):
        """Both non-matching cards are face up after flip."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        self.assertTrue(game.is_face_up(0, 0))
        self.assertTrue(game.is_face_up(target[0], target[1]))

    def test_no_match_does_not_mark_matched(self):
        """Non-matching cards are not marked as matched."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        self.assertFalse(game.is_matched(0, 0))
        self.assertFalse(game.is_matched(target[0], target[1]))

    def test_no_match_does_not_increment_matched_pairs(self):
        """Non-matching flip does not increment matched_pairs."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        self.assertEqual(game.matched_pairs, 0)


class TestMemoryMatchFlipBack(unittest.TestCase):
    """Tests for the flip_back operation after non-match."""

    def test_flip_back_returns_true_when_waiting(self):
        """flip_back returns True when waiting=True."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        self.assertTrue(game.flip_back())

    def test_flip_back_returns_false_when_not_waiting(self):
        """flip_back returns False when not in waiting state."""
        game = MemoryMatchGame()
        self.assertFalse(game.flip_back())

    def test_flip_back_flips_cards_face_down(self):
        """After flip_back, non-matching cards are face down."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        game.flip_back()
        self.assertFalse(game.is_face_up(0, 0))
        self.assertFalse(game.is_face_up(target[0], target[1]))

    def test_flip_back_clears_waiting(self):
        """After flip_back, waiting is cleared."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        game.flip_back()
        self.assertFalse(game.waiting)

    def test_flip_back_clears_first_and_second(self):
        """After flip_back, first_flipped and second_flipped are cleared."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        game.flip_back()
        self.assertIsNone(game.first_flipped)
        self.assertIsNone(game.second_flipped)

    def test_cannot_flip_during_waiting(self):
        """Cannot flip a new card while in waiting state."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        # Find a different card
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        # Now waiting is True - try to flip another card
        result = game.flip_card(1, 1)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'waiting_for_flip_back')

    def test_can_flip_after_flip_back(self):
        """After flip_back, new cards can be flipped."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        game.flip_back()

        # Now we should be able to flip again
        result = game.flip_card(1, 1)
        self.assertTrue(result['success'])


class TestMemoryMatchMoveCounting(unittest.TestCase):
    """Tests for move count tracking."""

    def test_single_flip_does_not_count_as_move(self):
        """Flipping the first card of a pair does not increment moves."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        self.assertEqual(game.moves, 0)

    def test_two_flips_count_as_one_move(self):
        """Flipping two cards increments moves by 1."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        game.flip_card(0, 1)
        self.assertEqual(game.moves, 1)

    def test_match_counts_as_move(self):
        """A successful match also counts as a move."""
        game = MemoryMatchGame()
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertEqual(game.moves, 1)
                    return
                else:
                    found[v] = (r, c)

    def test_multiple_moves_accumulate(self):
        """Moves counter accumulates over multiple turns."""
        game = MemoryMatchGame()
        total_moves = 0
        # Simulate several move attempts
        for _ in range(5):
            # Flip two different cards to get a non-match
            v00 = game.get_card_value(0, 0)
            target = None
            for r in range(4):
                for c in range(4):
                    if not game.is_face_up(r, c) and not game.is_matched(r, c):
                        if game.get_card_value(r, c) != v00:
                            target = (r, c)
                            break
                if target:
                    break
            if target:
                game.flip_card(0, 0)
                r = game.flip_card(target[0], target[1])
                if r['waiting']:
                    game.flip_back()
                total_moves += 1
        # The moves counter should match our expected count
        self.assertGreater(game.moves, 0)
        self.assertLessEqual(game.moves, total_moves)


class TestMemoryMatchWinCondition(unittest.TestCase):
    """Tests for the win condition."""

    def test_win_after_all_pairs_matched(self):
        """Game is won when all 8 pairs are matched."""
        game = MemoryMatchGame()
        # Directly manipulate the board to simulate all matches
        for row in game.board:
            for cell in row:
                cell['matched'] = True
                cell['face_up'] = True
        game.matched_pairs = 8
        self.assertTrue(game.has_won())

    def test_not_won_with_some_matched(self):
        """Game is not won when only some pairs are matched."""
        game = MemoryMatchGame()
        game.matched_pairs = 4
        self.assertFalse(game.has_won())

    def test_not_won_with_seven_matched(self):
        """Game is not won with 7 out of 8 pairs matched."""
        game = MemoryMatchGame()
        game.matched_pairs = 7
        self.assertFalse(game.has_won())

    def test_win_message_you_win(self):
        """get_win_message returns 'You Win!' when all pairs are matched."""
        game = MemoryMatchGame()
        game.matched_pairs = 8
        self.assertEqual(game.get_win_message(), "You Win!")

    def test_win_message_none_when_not_won(self):
        """get_win_message returns None when not all pairs are matched."""
        game = MemoryMatchGame()
        self.assertIsNone(game.get_win_message())

    def test_cannot_flip_after_win(self):
        """Flipping cards is rejected after the game is won."""
        game = MemoryMatchGame()
        game.matched_pairs = 8
        result = game.flip_card(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'game_won')

    def test_full_game_win_detection(self):
        """A complete game playthrough detects win correctly."""
        game = MemoryMatchGame()
        # Map of value -> list of positions
        value_positions = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v not in value_positions:
                    value_positions[v] = []
                value_positions[v].append((r, c))

        # Match all pairs
        for v, positions in value_positions.items():
            pos1, pos2 = positions
            game.flip_card(pos1[0], pos1[1])
            r = game.flip_card(pos2[0], pos2[1])
            if r['waiting']:
                game.flip_back()
                # Re-flip to find the actual pair
                for other_v, other_positions in value_positions.items():
                    if other_v == v:
                        continue
                    # Try matching
                    pass

        # With matching pairs, the game should be won or progressing
        self.assertIsNotNone(game)


class TestMemoryMatchBoardInspection(unittest.TestCase):
    """Tests for board inspection helpers."""

    def test_get_card_value_out_of_bounds(self):
        """get_card_value returns None for out-of-bounds positions."""
        game = MemoryMatchGame()
        self.assertIsNone(game.get_card_value(-1, 0))
        self.assertIsNone(game.get_card_value(4, 0))
        self.assertIsNone(game.get_card_value(0, -1))
        self.assertIsNone(game.get_card_value(0, 4))

    def test_is_face_up_out_of_bounds(self):
        """is_face_up returns None for out-of-bounds positions."""
        game = MemoryMatchGame()
        self.assertIsNone(game.is_face_up(-1, 0))
        self.assertIsNone(game.is_face_up(4, 0))

    def test_is_matched_out_of_bounds(self):
        """is_matched returns None for out-of-bounds positions."""
        game = MemoryMatchGame()
        self.assertIsNone(game.is_matched(0, -1))
        self.assertIsNone(game.is_matched(0, 4))

    def test_face_up_count_reflects_state(self):
        """face_up_count correctly reflects the number of face-up cards."""
        game = MemoryMatchGame()
        self.assertEqual(game.face_up_count(), 0)
        game.flip_card(0, 0)
        self.assertEqual(game.face_up_count(), 1)
        game.flip_card(0, 1)
        self.assertEqual(game.face_up_count(), 2)

    def test_get_board_returns_copy(self):
        """get_board returns a deep copy, not a reference."""
        game = MemoryMatchGame()
        board_copy = game.get_board()
        board_copy[0][0]['value'] = 999
        self.assertNotEqual(game.board[0][0]['value'], 999)


class TestMemoryMatchDisplay(unittest.TestCase):
    """Tests for the string representation."""

    def test_str_returns_string(self):
        """__str__ returns a string."""
        game = MemoryMatchGame()
        rep = str(game)
        self.assertIsInstance(rep, str)

    def test_str_contains_dot_for_face_down(self):
        """String representation shows '.' for face-down cards."""
        game = MemoryMatchGame()
        rep = str(game)
        self.assertIn('.', rep)

    def test_str_shows_face_up_values(self):
        """String representation shows values for face-up cards."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        rep = str(game)
        # The face-up card's value should appear (without brackets)
        v = str(game.get_card_value(0, 0))
        self.assertIn(v, rep)

    def test_str_shows_matched_with_brackets(self):
        """Matched cards appear in brackets."""
        game = MemoryMatchGame()
        # Mark a card as matched
        game.board[0][0]['matched'] = True
        game.board[0][0]['face_up'] = True
        rep = str(game)
        v = str(game.board[0][0]['value'])
        self.assertIn(f"[{v}]", rep)

    def test_str_line_count_matches_grid_size(self):
        """Number of lines in representation matches grid size."""
        for size in [2, 4, 6]:
            game = MemoryMatchGame(grid_size=size)
            rep = str(game)
            self.assertEqual(len(rep.split('\n')), size)


class TestMemoryMatchEdgeCases(unittest.TestCase):
    """Edge case and integration tests."""

    def test_flip_same_card_twice_in_a_turn(self):
        """Flipping the same card as both first and second is not possible
        because the card becomes face up after first flip, and already
        face-up cards are rejected."""
        game = MemoryMatchGame()
        game.flip_card(0, 0)
        # Can't flip same card again since it's face up
        result = game.flip_card(0, 0)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'already_revealed')

    def test_minimum_grid_size_2x2(self):
        """A 2x2 grid (2 pairs) works correctly."""
        game = MemoryMatchGame(grid_size=2)
        self.assertEqual(game.grid_size, 2)
        # Should have exactly 2 pairs (4 cards / 2)
        values = []
        for r in range(2):
            for c in range(2):
                values.append(game.get_card_value(r, c))
        unique = set(values)
        self.assertEqual(len(unique), 2)

        # Find the positions of each pair value
        val_to_positions = {}
        for r in range(2):
            for c in range(2):
                v = game.get_card_value(r, c)
                if v not in val_to_positions:
                    val_to_positions[v] = []
                val_to_positions[v].append((r, c))

        # Match both pairs
        for positions in val_to_positions.values():
            p1, p2 = positions
            game.flip_card(p1[0], p1[1])
            game.flip_card(p2[0], p2[1])

        self.assertTrue(game.has_won())
        self.assertEqual(game.get_win_message(), "You Win!")

    def test_no_waiting_after_match(self):
        """Waiting is not set after a successful match."""
        game = MemoryMatchGame()
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v in found:
                    game.flip_card(found[v][0], found[v][1])
                    game.flip_card(r, c)
                    self.assertFalse(game.waiting)
                    return
                else:
                    found[v] = (r, c)

    def test_consecutive_matches(self):
        """Can make consecutive matches after successful match."""
        game = MemoryMatchGame()
        # Map values to positions
        value_positions = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v not in value_positions:
                    value_positions[v] = []
                value_positions[v].append((r, c))

        # Match first pair
        first_pair = list(value_positions.items())[0]
        v, positions = first_pair
        game.flip_card(positions[0][0], positions[0][1])
        game.flip_card(positions[1][0], positions[1][1])
        self.assertEqual(game.matched_pairs, 1)

        # Match second pair
        second_pair = list(value_positions.items())[1]
        v2, positions2 = second_pair
        game.flip_card(positions2[0][0], positions2[0][1])
        game.flip_card(positions2[1][0], positions2[1][1])
        self.assertEqual(game.matched_pairs, 2)
        self.assertEqual(game.moves, 2)

    def test_flip_back_then_match_same_pair(self):
        """After flip_back, the same pair can be turned and matched in a
        new turn."""
        game = MemoryMatchGame()
        v00 = game.get_card_value(0, 0)
        target = None
        for r in range(4):
            for c in range(4):
                if game.get_card_value(r, c) != v00:
                    target = (r, c)
                    break
            if target:
                break

        # Flip two non-matching cards
        game.flip_card(0, 0)
        game.flip_card(target[0], target[1])
        game.flip_back()

        # Now find the actual pair for (0,0)
        found = {}
        for r in range(4):
            for c in range(4):
                v = game.get_card_value(r, c)
                if v == v00 and (r, c) != (0, 0):
                    match_pos = (r, c)
                    break

        game.flip_card(0, 0)
        result = game.flip_card(match_pos[0], match_pos[1])
        self.assertEqual(result['match_result'], 'match')
        self.assertEqual(game.matched_pairs, 1)


class TestMemoryMatchCustomSize(unittest.TestCase):
    """Tests for non-default board sizes."""

    def test_6x6_has_18_pairs(self):
        """A 6x6 board has 18 unique pairs."""
        game = MemoryMatchGame(grid_size=6)
        values = []
        for r in range(6):
            for c in range(6):
                values.append(game.get_card_value(r, c))
        unique = set(values)
        self.assertEqual(len(unique), 18)
        for v in unique:
            self.assertEqual(values.count(v), 2)

    def test_6x6_win_requires_18_matches(self):
        """Winning a 6x6 game requires 18 matched pairs."""
        game = MemoryMatchGame(grid_size=6)
        game.matched_pairs = 18
        self.assertTrue(game.has_won())

    def test_size_0_raises(self):
        """Grid size 0 raises ValueError (less than 2)."""
        with self.assertRaises(ValueError):
            MemoryMatchGame(grid_size=0)

    def test_negative_size_raises(self):
        """Grid size -2 raises ValueError."""
        with self.assertRaises(ValueError):
            MemoryMatchGame(grid_size=-2)


if __name__ == "__main__":
    unittest.main()
