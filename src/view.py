import pygame
from models import Board, Snake

COLOR_BACKGROUND = (0, 0, 0)
COLOR_HEADER = (40, 40, 40)
COLOR_SNAKE = (0, 255, 0)
COLOR_FOOD = (255, 0, 0)
COLOR_OBSTACLE = (128, 128, 128)
COLOR_WALL = (255, 255, 255)
COLOR_COLLISION = (255, 0, 255)

class GameView:
    """
    Manages the graphical user interface using Pygame.

    This class is responsible for initialising the game window, rendering
    all game elements (snake, food, obstacles, grid) and displaying
    the Game Over Menu.
    """
    def __init__(self, board: Board):
        pygame.init()
        self.board = board
        
        self.header_height = 40
        
        # Dimensions from JSON config
        self.cell_size = board.cell_size
        self.screen_width = board.width * self.cell_size
        self.screen_height = (board.height * self.cell_size) + self.header_height
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Python Snake Game")
        self.font = pygame.font.Font(None, 36)

    def draw_cell(self, x, y, color):
        """Draws a single cell at (x, y) board coordinates."""
        rect = pygame.Rect(
            x * self.cell_size, 
            y * self.cell_size + self.header_height, 
            self.cell_size, 
            self.cell_size
        )
        pygame.draw.rect(self.screen, color, rect)
        
    def draw_all(self, game_over=False, high_score=0, round_num=1, freeze_remaining=None):
        """Draws the entire game state."""
        self.screen.fill(COLOR_BACKGROUND)
        # Header
        header_rect = pygame.Rect(0, 0, self.screen_width, self.header_height)
        pygame.draw.rect(self.screen, COLOR_HEADER, header_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (0, self.header_height), (self.screen_width, self.header_height), 2)
        
        # Score and Round
        score_text = self.font.render(f"Score: {self.board.score}    Round: {round_num}", True, (255, 255, 255))
        text_y = (self.header_height - score_text.get_height()) // 2
        self.screen.blit(score_text, (15, text_y))
        
        # Draw Obstacles
        for obs_x, obs_y in self.board.obstacles:
            self.draw_cell(obs_x, obs_y, COLOR_OBSTACLE)

        # Draw Food
        if self.board.food:
            food_x, food_y = self.board.food
            self.draw_cell(food_x, food_y, COLOR_FOOD)

        # Draw Snake
        for i, (snake_x, snake_y) in enumerate(self.board.snake.body):
            color = COLOR_SNAKE
            if game_over and i == 0:
                # Highlight the head upon collision
                color = COLOR_COLLISION 
            self.draw_cell(snake_x, snake_y, color)

        # Draw Grid Lines
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(self.screen, (30, 30, 30), (x, self.header_height), (x, self.screen_height))
        for y in range(0, self.board.height * self.cell_size + 1, self.cell_size):
            draw_y = y + self.header_height
            pygame.draw.line(self.screen, (30, 30, 30), (0, draw_y), (self.screen_width, draw_y))
        # Game Over Menu
        if game_over:
            # overlay cu fundal transparent
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Display Game Over Text
            text = self.font.render("GAME OVER", True, COLOR_COLLISION)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 60))
            self.screen.blit(text, text_rect)
            
            # Session Statistics 
            stats_text = self.font.render(f"Round: {round_num} | High Score: {high_score}", True, (255, 255, 255))
            stats_rect = stats_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
            self.screen.blit(stats_text, stats_rect)
            
            # Menu Instructions
            options = [
                "[C] - Continue (Next Round)",
                "[U] - Undo",
                "[Q] - Quit Game"
            ]
            
            start_y = self.screen_height // 2 + 20
            for i, line in enumerate(options):
                menu_surf = self.font.render(line, True, (200, 200, 200))
                menu_rect = menu_surf.get_rect(center=(self.screen_width // 2, start_y + i * 30))
                self.screen.blit(menu_surf, menu_rect)
            
        # Freeze countdown
        if freeze_remaining is not None:
            font = pygame.font.Font(None, 100)
            text = font.render(str(freeze_remaining), True, (255, 255, 0))
            
            text_shadow = font.render(str(freeze_remaining), True, (0, 0, 0))
            center_x, center_y = self.screen_width // 2, self.screen_height // 2
            self.screen.blit(text_shadow, (center_x - 2, center_y - 2 + 20))
            self.screen.blit(text, (center_x, center_y + 20))
            
        pygame.display.flip()

    def cleanup(self):
        """Closes Pygame."""
        pygame.quit()