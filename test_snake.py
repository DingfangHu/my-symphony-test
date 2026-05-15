"""Tests for the Snake game."""

import unittest
from snake import SnakeGame, UP, DOWN, LEFT, RIGHT, OPPOSITE


class TestSnakeGame(unittest.TestCase):
    """Unit tests for the SnakeGame class."""

    def test_initial_state(self):
        """Game starts with score 0, not game over, and snake length 3."""
        game = SnakeGame(10, 10)
        self.assertEqual(game.score, 0)
        self.assertFalse(game.game_over)
        self.assertEqual(len(game.snake), 3)

    def test_grid_too_small_raises(self):
        """Grid dimensions below 4x4 raise ValueError."""
        with self.assertRaises(ValueError):
            SnakeGame(3, 10)
        with self.assertRaises(ValueError):
            SnakeGame(10, 3)

    def test_food_spawned_on_init(self):
        """Food is placed on a valid cell after initialization."""
        game = SnakeGame(10, 10)
        self.assertIsNotNone(game.food)
        fx, fy = game.food
        self.assertTrue(0 <= fx < game.grid_width)
        self.assertTrue(0 <= fy < game.grid_height)
        self.assertNotIn(game.food, game.snake)

    def test_set_direction_valid(self):
        """Setting a valid direction changes the snake direction."""
        game = SnakeGame(10, 10)
        game.set_direction(UP)
        self.assertEqual(game.direction, UP)

    def test_set_direction_opposite_ignored(self):
        """Setting opposite direction (reversal) is ignored."""
        game = SnakeGame(10, 10)
        # Snake starts moving RIGHT
        game.set_direction(LEFT)  # opposite of RIGHT
        self.assertEqual(game.direction, RIGHT)

    def test_set_direction_invalid_raises(self):
        """Invalid direction raises ValueError."""
        game = SnakeGame(10, 10)
        with self.assertRaises(ValueError):
            game.set_direction((99, 99))

    def test_tick_moves_snake(self):
        """After one tick, the snake head moves in the current direction."""
        game = SnakeGame(10, 10)
        initial_head = game.snake[0]
        game.tick()
        new_head = game.snake[0]
        # Moving RIGHT: x increases by 1, y unchanged
        self.assertEqual(new_head, (initial_head[0] + 1, initial_head[1]))

    def test_tick_moves_snake_length(self):
        """After a normal tick (no food), snake length stays the same."""
        game = SnakeGame(10, 10)
        initial_len = len(game.snake)
        game.tick()
        self.assertEqual(len(game.snake), initial_len)

    def test_eating_food_grows_snake(self):
        """Eating food increases snake length and increments score."""
        game = SnakeGame(10, 10)
        # Place food directly in front of the snake
        head = game.snake[0]
        game.food = (head[0] + 1, head[1])  # one step right of head
        initial_len = len(game.snake)
        result = game.tick()
        self.assertTrue(result)
        self.assertEqual(len(game.snake), initial_len + 1)
        self.assertEqual(game.score, 1)

    def test_score_increments_on_food(self):
        """Score increments by 1 each time food is eaten."""
        game = SnakeGame(20, 20)
        # Manually place food in front of snake multiple times
        for expected_score in range(1, 5):
            head = game.snake[0]
            game.food = (head[0] + 1, head[1])
            game.tick()
            self.assertEqual(game.score, expected_score)

    def test_wall_collision_ends_game(self):
        """Moving into a wall triggers game over."""
        game = SnakeGame(10, 10)
        # Move snake to the far right edge
        while game.snake[0][0] < game.grid_width - 1:
            game.direction = RIGHT
            game.food = (0, 0)  # food out of the way
            game.tick()
        # Now head is at rightmost column; one more RIGHT hits wall
        game.direction = RIGHT
        game.food = (0, 0)
        result = game.tick()
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_self_collision_ends_game(self):
        """Snake hitting itself triggers game over."""
        game = SnakeGame(10, 10)
        # L-shaped snake: head turns right into own body segment
        game.snake = [(3, 3), (4, 3), (5, 3), (5, 4), (4, 4)]
        game.direction = RIGHT
        game.food = (0, 0)  # food out of the way
        result = game.tick()
        self.assertFalse(result)
        self.assertTrue(game.game_over)

    def test_tick_after_game_over_returns_false(self):
        """Tick returns False when game is already over."""
        game = SnakeGame(10, 10)
        game.game_over = True
        result = game.tick()
        self.assertFalse(result)

    def test_restart_resets_game(self):
        """Restart returns game to initial state."""
        game = SnakeGame(10, 10)
        # Modify the game state
        game.score = 10
        game.snake = [(0, 0), (0, 1)]
        game.game_over = True
        game.restart()
        self.assertEqual(game.score, 0)
        self.assertFalse(game.game_over)
        self.assertEqual(len(game.snake), 3)
        self.assertIsNotNone(game.food)

    def test_direction_up(self):
        """Snake moves up correctly."""
        game = SnakeGame(10, 10)
        game.set_direction(UP)
        game.food = (0, 0)
        game.tick()
        head_before = game.snake[1]  # previous head
        head_after = game.snake[0]
        self.assertEqual(head_after, (head_before[0], head_before[1] - 1))

    def test_direction_down(self):
        """Snake moves down correctly."""
        game = SnakeGame(10, 10)
        game.set_direction(DOWN)
        game.food = (0, 0)
        game.tick()
        head_before = game.snake[1]
        head_after = game.snake[0]
        self.assertEqual(head_after, (head_before[0], head_before[1] + 1))

    def test_direction_left(self):
        """Snake moves left correctly."""
        game = SnakeGame(20, 20)
        # Move snake right first so body isn't immediately behind head
        game.food = (0, 0)
        game.tick()
        # Now turn down and move to create horizontal offset
        game.set_direction(DOWN)
        game.tick()
        # Now turn left for a clean move
        game.set_direction(LEFT)
        game.tick()
        head_before = game.snake[1]
        head_after = game.snake[0]
        self.assertEqual(head_after, (head_before[0] - 1, head_before[1]))

    def test_food_not_on_snake(self):
        """After spawning, food is never on the snake body."""
        for _ in range(50):
            game = SnakeGame(10, 10)
            self.assertIsNotNone(game.food)
            self.assertNotIn(game.food, game.snake)

    def test_opposite_mapping(self):
        """OPPOSITE dictionary correctly maps direction reversals."""
        self.assertEqual(OPPOSITE[UP], DOWN)
        self.assertEqual(OPPOSITE[DOWN], UP)
        self.assertEqual(OPPOSITE[LEFT], RIGHT)
        self.assertEqual(OPPOSITE[RIGHT], LEFT)

    def test_multiple_ticks_without_crash(self):
        """Game runs multiple ticks without crashing."""
        game = SnakeGame(10, 10)
        for _ in range(50):
            if game.game_over:
                break
            game.tick()
        # Should not crash
        self.assertTrue(True)

    def test_immediate_reversal_prevented(self):
        """Cannot reverse direction immediately (e.g., UP after DOWN)."""
        game = SnakeGame(10, 10)
        # Snake starts heading RIGHT
        game.set_direction(UP)
        game.set_direction(DOWN)  # opposite of current UP
        self.assertEqual(game.direction, UP)  # Should still be UP

    def test_game_over_on_wall_top(self):
        """Game over when snake hits the top wall."""
        game = SnakeGame(10, 10)
        game.set_direction(UP)
        game.food = (0, 0)
        # Move to top row
        while game.snake[0][1] > 0:
            game.tick()
            if game.game_over:
                break
        if not game.game_over:
            result = game.tick()
            self.assertFalse(result)
            self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()
