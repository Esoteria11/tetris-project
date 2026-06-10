import pygame
from settings import BLOCK_SIZE, GRID_W, GRID_H, RED, CYAN, YELLOW, PURPLE, GREEN, BLUE, ORANGE, BLACK

class Tetromino:
    def __init__(self, x, y, shape_type):
        self.x = x
        self.y = y
        self.shape_type = shape_type
        
        self.shapes = {
            'I': {
                'color': CYAN,
                'blocks': [(0, 1), (1, 1), (2, 1), (3, 1)]
            },
            'O': {
                'color': YELLOW,
                'blocks': [(0, 0), (1, 0), (0, 1), (1, 1)]
            },
            'T': {
                'color': PURPLE,
                'blocks': [(0, 0), (1, 0), (2, 0), (1, 1)]
            },
            'S': {
                'color': GREEN,
                'blocks': [(1, 0), (2, 0), (0, 1), (1, 1)]
            },
            'Z': {
                'color': RED,
                'blocks': [(0, 0), (1, 0), (1, 1), (2, 1)]
            },
            'J': {
                'color': BLUE,
                'blocks': [(0, 0), (0, 1), (1, 1), (2, 1)]
            },
            'L': {
                'color': ORANGE,
                'blocks': [(2, 0), (0, 1), (1, 1), (2, 1)]
            }
        }
        
        self.color = self.shapes[shape_type]['color']
        self.shape = self.shapes[shape_type]['blocks']

    def draw(self, screen):
        for block_x, block_y in self.shape:
            pixel_x = (self.x + block_x) * BLOCK_SIZE
            pixel_y = (self.y + block_y) * BLOCK_SIZE
            rect = pygame.Rect(pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def check_collision(self, dx, dy, grid):
        for block_x, block_y in self.shape:
            future_x = self.x + block_x + dx
            future_y = self.y + block_y + dy
            
            if future_x < 0 or future_x >= GRID_W or future_y >= GRID_H:
                return True
            
            if future_y >= 0: 
                if grid[future_y][future_x] is not None:
                    return True
                    
        return False
    
    def get_rotated_shape(self):
        rotated = [(y, -x) for x, y in self.shape]
        
        min_x = min(block[0] for block in rotated)
        min_y = min(block[1] for block in rotated)
        
        normalized = [(x - min_x, y - min_y) for x, y in rotated]
        
        return normalized

    def draw_next(self, screen, offset_x, offset_y):
        for block_x, block_y in self.shape:
            pixel_x = offset_x + block_x * BLOCK_SIZE
            pixel_y = offset_y + block_y * BLOCK_SIZE
            rect = pygame.Rect(pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

    def draw_prediction(self, screen, ghost_y, color):
        for block_x, block_y in self.shape:
            pixel_x = (self.x + block_x) * BLOCK_SIZE
            pixel_y = (ghost_y + block_y) * BLOCK_SIZE
            rect = pygame.Rect(pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)

            pygame.draw.rect(screen, color, rect, 2)
