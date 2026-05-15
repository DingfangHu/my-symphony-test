"""Classic Snake game implementation using Pygame."""

import random
import pygame


# Direction constants as (dx, dy) vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# All valid directions
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Opposites mapping to prevent reversing into yourself
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class SnakeGame:
    """Classic Snake game logic.

    The snake moves on a grid, grows when eating food, and the game ends
    if the snake hits a wall or itself.
    """

    def __init__(self, grid_width=20, grid_height=20):
        """Initialize a new Snake game.

        Args:
            grid_width: Number of columns in the play grid.
            grid_height: Number of rows in the play grid.

        Raises:
            ValueError: If grid dimensions are too small.
        """
        if grid_width < 4 or grid_height < 4:
            raise ValueError("Grid dimensions must be at least 4x4.")
        self.grid_width = grid_width
        self.grid_height = grid_height
        self._reset()

    def _reset(self):
        """Reset the snake and food to starting positions."""
        cx = self.grid_width // 2
        cy = self.grid_height // 2
        # Snake starts horizontally, length 3: head, body, tail
        self.snake = [(cx + 2, cy), (cx + 1, cy), (cx, cy)]
        self.direction = RIGHT
        self._spawn_food()
        self.score = 0
        self.game_over = False

    def _spawn_food(self):
        """Place food at a random empty cell."""
        snake_set = set(self.snake)
        candidates = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in snake_set
        ]
        if not candidates:
            # Board is full — snake wins (rare corner case)
            self.food = None
            return
        self.food = random.choice(candidates)

    def set_direction(self, direction):
        """Set the snake direction. Reversals are ignored.

        Args:
            direction: One of (UP, DOWN, LEFT, RIGHT).

        Raises:
            ValueError: If direction is not valid.
        """
        if direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction}")
        # Prevent reversing into yourself
        if direction != OPPOSITE[self.direction]:
            self.direction = direction

    def tick(self):
        """Advance the game by one frame.

        Returns:
            True if the tick was successful (no collision), False if game over.
        """
        if self.game_over:
            return False

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Wall collision
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self.game_over = True
            return False

        # Self-collision (check against body, excluding the tail if not growing)
        if new_head in self.snake[:-1]:
            self.game_over = True
            return False

        # Move: insert new head
        self.snake.insert(0, new_head)

        # Check food
        if self.food is not None and new_head == self.food:
            self.score += 1
            self._spawn_food()
            # Do not remove tail — snake grows
        else:
            self.snake.pop()  # Remove tail to keep length

        return True

    def restart(self):
        """Restart the game from initial state."""
        self._reset()


def main():
    """Run the Snake game with Pygame rendering.

    Controls: Arrow keys to change direction.
    Close the window or press ESC to quit.
    Press SPACE to restart after game over.
    """
    pygame.init()

    CELL_SIZE = 25
    GRID_WIDTH = 20
    GRID_HEIGHT = 20
    FPS = 10

    WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
    WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

    # Colors
    BG_COLOR = (20, 20, 30)
    SNAKE_COLOR = (50, 200, 50)
    SNAKE_HEAD_COLOR = (80, 240, 80)
    FOOD_COLOR = (220, 50, 50)
    SCORE_COLOR = (200, 200, 200)
    GAME_OVER_COLOR = (255, 100, 100)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    game = SnakeGame(GRID_WIDTH, GRID_HEIGHT)

    running = True
    while running:
        clock.tick(FPS)

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.game_over:
                    if event.key == pygame.K_SPACE:
                        game.restart()
                else:
                    if event.key == pygame.K_UP:
                        game.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        game.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        game.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        game.set_direction(RIGHT)

        # --- Game logic ---
        if not game.game_over:
            game.tick()

        # --- Rendering ---
        screen.fill(BG_COLOR)

        # Draw grid lines
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (30, 30, 40), rect, 1)

        # Draw food
        if game.food is not None:
            fx, fy = game.food
            food_rect = (fx * CELL_SIZE + 2, fy * CELL_SIZE + 2,
                         CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(screen, FOOD_COLOR, food_rect, border_radius=5)

        # Draw snake
        for i, (sx, sy) in enumerate(game.snake):
            seg_rect = (sx * CELL_SIZE + 2, sy * CELL_SIZE + 2,
                        CELL_SIZE - 4, CELL_SIZE - 4)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            pygame.draw.rect(screen, color, seg_rect, border_radius=4)

        # Draw score
        score_surf = font.render(f"Score: {game.score}", True, SCORE_COLOR)
        screen.blit(score_surf, (10, 10))

        # Draw game over overlay
        if game.game_over:
            go_surf = font.render("GAME OVER - Press SPACE to restart",
                                  True, GAME_OVER_COLOR)
            go_rect = go_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(go_surf, go_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
