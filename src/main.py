import pygame
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

from models import Board
from view import GameView

FPS = 60 # Pygame refresh rate
SNAKE_SPEED = 5 # Moves per second (Game tick rate)

def main():
    # Initialize Model
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
    board = Board(config_path)

    # Initialize View
    view = GameView(board)
    clock = pygame.time.Clock()
    
    # Game State Variables
    running = True
    game_over = False
    high_score = 0
    round_count = 1
    
    # Custom event for reliable game ticks
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 1000 // SNAKE_SPEED) # Set a timer for the snake movement

    while running:
        # --- Controller: Handle Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    # Normal gameplay controls
                    if event.key == pygame.K_UP:
                        board.snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        board.snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        board.snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        board.snake.set_direction((1, 0))
                else:
                    # Game Over controls
                    if event.key == pygame.K_c:
                        # Continue to next round
                        round_count += 1
                        board = Board(config_path)
                        view.board = board # Update the view to look at the new board
                        game_over = False
                    
                    elif event.key == pygame.K_q:
                        # Quit game
                        running = False

            if event.type == MOVE_EVENT and not game_over:
                # --- Controller: Update Model ---
                
                # Predict the next head position
                dx, dy = board.snake.next_direction
                head_x, head_y = board.snake.body[0]
                new_head = (head_x + dx, head_y + dy)
                
                # Check for collisions (Wall/Obstacle)
                if not board.is_valid_move(new_head):
                    game_over = True
                else:
                    # Move the snake
                    _, success = board.snake.move()
                    if not success:
                        game_over = True
                    else:
                        new_head = board.snake.body[0]

                        # Check for Food
                        if new_head == board.food:
                            board.snake.eat()
                            board.food = board.spawn_food()
                            board.score += 1
                            
        if game_over and board.score > high_score:  
            high_score = board.score
        
        # --- View: Draw State ---
        view.draw_all(game_over, high_score, round_count)
        
        clock.tick(FPS)

    view.cleanup()

if __name__ == '__main__':
    main()