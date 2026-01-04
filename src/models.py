import json
import random

class Board:
    """
    game state and logic.

    This class manages the game grid, loading configuration from JSON,
    tracking the positions of the snake, food, obstacles, and
    enforcing game rules like collision detection.
    """
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self._validate_config()
        
        self.width = self.config['board_size']['width']
        self.height = self.config['board_size']['height']
        self.cell_size = self.config['cell_size']
        self.obstacles = list(map(tuple, self.config['initial_obstacles']))
        
        self.snake = Snake(self.config['initial_snake_position'])
        
        if set(self.snake.body) & set(self.obstacles):
            raise ValueError("Config Error: Initial snake position collides with obstacles.")
        
        self.food = self.spawn_food()
        self.score = 0
        
    def _validate_config(self):
        """Validates the loaded configuration."""
        w = self.config['board_size']['width']
        h = self.config['board_size']['height']
        size = self.config['cell_size']
        start_x, start_y = self.config['initial_snake_position']
        
        if w <= 0 or h <= 0 or size <= 0:
            raise ValueError("Config Error: Board dimensions and cell size must be positive integers.") 
        
        if not (0 <= start_x < w and 0 <= start_y < h):
            raise ValueError("Config Error: Initial snake position is outside the board boundaries.")
        
        for obs in self.config['initial_obstacles']:
            ox, oy = obs
            if not (0 <= ox < w and 0 <= oy < h):
                raise ValueError(f"Config Error: Obstacle at position ({ox}, {oy}) is outside the board boundaries.")
        
    def get_occupied_cells(self):
        """Returns all positions currently occupied by the snake or obstacles."""
        return set(self.snake.body) | set(self.obstacles)

    def spawn_food(self):
        """Places food in a random and unoccupied cell."""
        occupied = self.get_occupied_cells()
        
        # List of all valid cells (x, y) coordinates
        available_cells = [
            (x, y) for x in range(self.width) for y in range(self.height)
            if (x, y) not in occupied
        ]

        if not available_cells:
            return None 

        return random.choice(available_cells)

    def is_valid_move(self, new_head):
        """Checks for collisions with walls, itself, or obstacles."""
        x, y = new_head
        
        # Wall collision
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            
        # Obstacle collision
        if new_head in self.obstacles:
            return False
        
        return True

class Snake:
    """
    Snake itself.

    This class maintains the snake's body coordinates, handles movement
    mechanics, manages direction changes, and controls growth when food is eaten.
    """
    def __init__(self, initial_pos):
        # Body is a list of (x, y) tuples, where index 0 is the head
        self.body = [tuple(initial_pos)]
        # Default direction: Right (1, 0)
        self.direction = (1, 0)
        self.next_direction = (1, 0) # Allows buffered input
        self.grow = False # determine if the snake should grow on next move

    def set_direction(self, new_dir):
        """Sets the next direction of the snake, preventing 180-degree turns."""
        dx, dy = self.direction
        ndx, ndy = new_dir
        
        # Check if the new direction is the opposite of the current one
        if (dx + ndx, dy + ndy) != (0, 0):
            self.next_direction = new_dir

    def move(self):
        """Updates the snake's position based on its direction."""
        self.direction = self.next_direction
        dx, dy = self.direction
        head_x, head_y = self.body[0]
        
        new_head = (head_x + dx, head_y + dy)
        
        # If we are growing, the tail stays, so we can hit it
        if self.grow:
            check_body = self.body
        # If we are NOT growing, the tail will move away, so we can't hit it
        else:
            check_body = self.body[:-1]
        
        if new_head in check_body:
             return new_head, False # Collision detected

        self.body.insert(0, new_head)
        
        if self.grow:
            self.grow = False
        else:
            # Remove the tail if not growing
            self.body.pop()
            
        return new_head, True 

    def eat(self):
        self.grow = True