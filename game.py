import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLOCK_SIZE, BLACK, WHITE, GRAY, SIDEBAR_BG, FALL_SPEED, GRID_W, GRID_H
from tetromino import Tetromino

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Тетрис")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.game_over = False        
        self.font = pygame.font.Font(None, 36) 
        self.big_font = pygame.font.Font(None, 72)

        self.grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]

        self.next_shape_type = random.choice(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])
        
        self.last_move_time = 0
        self.move_delay = 100
        
        self.spawn_new_figure()
        
        self.FALL_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.FALL_EVENT, FALL_SPEED)

    def spawn_new_figure(self):
        self.figure = Tetromino(GRID_W // 2 - 1, 0, self.next_shape_type)        
        self.next_shape_type = random.choice(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])
        
        if self.figure.check_collision(0, 0, self.grid):
            self.game_over = True
            print("GAME OVER! Ваш счет:", self.score)

    def freeze_figure(self):
        for block_x, block_y in self.figure.shape:
            grid_x = self.figure.x + block_x
            grid_y = self.figure.y + block_y
            if 0 <= grid_y < GRID_H and 0 <= grid_x < GRID_W:
                self.grid[grid_y][grid_x] = self.figure.color

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_H - 1
        
        while y >= 0:
            if None not in self.grid[y]:
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_W)])
                lines_cleared += 1
            else:
                y -= 1
                
        if lines_cleared > 0:
            points = [0, 100, 300, 500, 800]
            self.score += points[lines_cleared]
            print(f"Линий очищено: {lines_cleared}. Счет: {self.score}")

    def run(self):
        while self.running:
            if self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                
                self.screen.fill(BLACK)
                game_over_text = self.big_font.render("GAME OVER", True, WHITE)
                score_text = self.font.render(f"Score: {self.score}", True, WHITE)
                
                go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
                sc_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
                
                self.screen.blit(game_over_text, go_rect)
                self.screen.blit(score_text, sc_rect)
                
                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        new_shape = self.figure.get_rotated_shape()
                        old_shape = self.figure.shape
                        self.figure.shape = new_shape
                        
                        if not self.figure.check_collision(0, 0, self.grid):
                            pass
                        else:
                            kicked = False
                            
                            for kick_x in [-1, 1, -2, 2]:
                                if not self.figure.check_collision(kick_x, 0, self.grid):
                                    self.figure.x += kick_x
                                    kicked = True
                                    break
                            
                            if not kicked:
                                self.figure.shape = old_shape
                    
                    elif event.key == pygame.K_SPACE:
                        while not self.figure.check_collision(0, 1, self.grid):
                            self.figure.move_down()
                        self.freeze_figure()
                        self.clear_lines()
                        self.spawn_new_figure()

                elif event.type == self.FALL_EVENT:
                    if not self.figure.check_collision(0, 1, self.grid):
                        self.figure.move_down()
                    else:
                        self.freeze_figure()
                        self.clear_lines()
                        self.spawn_new_figure()

            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            
            if current_time - self.last_move_time > self.move_delay:
                moved = False
                
                if keys[pygame.K_LEFT]:
                    if not self.figure.check_collision(-1, 0, self.grid):
                        self.figure.move_left()
                        moved = True
                
                if keys[pygame.K_RIGHT]:
                    if not self.figure.check_collision(1, 0, self.grid):
                        self.figure.move_right()
                        moved = True
                        
                if keys[pygame.K_DOWN]:
                    if not self.figure.check_collision(0, 1, self.grid):
                        self.figure.move_down()
                        moved = True
                
                if moved:
                    self.last_move_time = current_time

            self.screen.fill(BLACK)
            
            pygame.draw.rect(self.screen, SIDEBAR_BG, (300, 0, 150, SCREEN_HEIGHT))
            
            for y in range(GRID_H):
                for x in range(GRID_W):
                    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

            for y in range(GRID_H):
                for x in range(GRID_W):
                    if self.grid[y][x] is not None:
                        pixel_x = x * BLOCK_SIZE
                        pixel_y = y * BLOCK_SIZE
                        rect = pygame.Rect(pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.screen, self.grid[y][x], rect)
                        pygame.draw.rect(self.screen, BLACK, rect, 2)

            self.figure.draw(self.screen)
            
            next_text = self.font.render("NEXT", True, WHITE)
            self.screen.blit(next_text, (330, 30))
            
            next_piece_preview = Tetromino(0, 0, self.next_shape_type)
            next_piece_preview.draw_next(self.screen, 330, 80)
            
            score_label = self.font.render("SCORE", True, WHITE)
            self.screen.blit(score_label, (330, 200))
            
            score_value = self.font.render(str(self.score), True, WHITE)
            self.screen.blit(score_value, (330, 240))
            
            small_font = pygame.font.Font(None, 24)
            controls = [
                "Arrows: Move",
                "Up: Rotate",
                "Down: Soft Drop",
                "Space: Hard Drop"
            ]
            for i, text in enumerate(controls):
                ctrl_text = small_font.render(text, True, GRAY)
                self.screen.blit(ctrl_text, (315, 350 + i * 25))
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
