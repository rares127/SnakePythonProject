import pygame
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

from models import Board
from view import GameView

FPS = 60 # Pygame refresh rate
UNDO_FREEZE_DURATION = 3000 # 3 seconds to react 

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'highscore.json')

def load_high_score():
    """Load high score from file."""
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("high_score", 0)
    except (json.JSONDecodeError, ValueError):
        return 0
    
def save_high_score(score):
    """Save high score to file."""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump({"high_score": score}, f)
    except IOError:
        print("Error saving high score.")

def main():
    """
    The main game loop.

    Handles:
    1. Initialization of Model and View.
    2. The Game Loop (Input -> Update -> Render).
    3. Session management (High scores, Round counting).
    4. Special states (Freeze/Undo mechanics).
    """
    
    # Initialize Model
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
    
    try:
        board = Board(config_path)
    except ValueError as e:
        print(f"Error loading configuration: {e}")
        return

    # Initialize View
    view = GameView(board)
    clock = pygame.time.Clock()
    
    # Game State Variables
    running = True
    game_over = False
    high_score = load_high_score()
    round_count = 1
    snake_speed = 5
    unpause_time = 0 # Time marker for freeze state when undoing

    # Separate render (FPS) from gameplay (Tick rate - snake speed) 
    MOVE_EVENT = pygame.USEREVENT + 1 
    pygame.time.set_timer(MOVE_EVENT, 1000 // snake_speed) # Set a timer for the snake movement

    while running:
        current_time = pygame.time.get_ticks()
        
        # Check if we are in frozen state (after undoing)
        is_frozen = current_time < unpause_time
        
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
                    
                    # Speed controls
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        snake_speed = min(snake_speed + 1, 20)
                        pygame.time.set_timer(MOVE_EVENT, 1000 // snake_speed)
                        
                    elif event.key == pygame.K_MINUS:
                        snake_speed = max(snake_speed - 1, 1)
                        pygame.time.set_timer(MOVE_EVENT, 1000 // snake_speed)
                
                else:
                    # Game Over controls
                    if event.key == pygame.K_c:
                        # Continue to next round
                        round_count += 1
                        board = Board(config_path)
                        view.board = board # Update the view to have a new board
                        game_over = False
                        unpause_time = 0
                        snake_speed = 5
                        pygame.time.set_timer(MOVE_EVENT, 1000 // snake_speed)
                    
                    elif event.key == pygame.K_q:
                        # Quit game
                        running = False
                        
                    elif event.key == pygame.K_u:
                        # Undo
                        if board.undo():
                            game_over = False
                            # Freeze the game for 3 seconds to let the player react
                            unpause_time = current_time + UNDO_FREEZE_DURATION
                            snake_speed = 5
                            pygame.time.set_timer(MOVE_EVENT, 1000 // snake_speed)

            if event.type == MOVE_EVENT and not game_over and not is_frozen:
                # we save the state before updating (for undo functionality)
                board.save_state()
                
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
                            board.score += 10
                            
        if game_over and board.score > high_score:  
            high_score = board.score
            save_high_score(high_score)
        
        # Calculate countdown 
        freeze_remaining = None
        if is_frozen and not game_over:
            freeze_remaining = (unpause_time - current_time) // 1000 + 1
        
        # --- View: Draw State ---
        view.draw_all(game_over, high_score, round_count, freeze_remaining)
        
        clock.tick(FPS)

    view.cleanup()

if __name__ == '__main__':
    main()