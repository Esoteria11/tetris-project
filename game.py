import pygame
import random
import os
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLOCK_SIZE, 
    BLACK, WHITE, GRAY, RED, SIDEBAR_BG, GHOST, GOLD,
    FALL_SPEED, GRID_W, GRID_H,
    VICTORY_SCORE, CAT_IMAGE_SIZE, SIDEBAR_X, SIDEBAR_WIDTH,
    SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y, OVERLAY_ALPHA, IS_FULLSCREEN
)
from tetromino import Tetromino

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.lifetime = random.randint(30, 60)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        alpha = min(255, self.lifetime * 5)
        color = tuple(min(c, 255) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class Game:    
    def __init__(self):
        pygame.init()

        self.is_fullscreen = IS_FULLSCREEN
        flags = pygame.SCALED
        if self.is_fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()      
        self.running = True
        self.score = 0
        self.game_over = False
        self.is_paused = False
        self.victory = False
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.next_shape_type = random.choice(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])
        self.last_move_time = 0
        self.move_delay = 100
        self.victory_cats = self.load_cat_images('victory')
        self.gameover_cats = self.load_cat_images('gameover')
        self.current_cat = None
        self.particles = []
        self.clearing_lines = []
        
        self.spawn_new_figure()
        
        self.FALL_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.FALL_EVENT, FALL_SPEED)

    def load_cat_images(self, cat_type):
        cats = []
        images_dir = os.path.join('assets', 'images')
        
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if cat_type in filename.lower() and filename.lower().endswith(('.jpg', '.png')):
                    try:
                        img_path = os.path.join(images_dir, filename)
                        img = pygame.image.load(img_path)
                        img = pygame.transform.scale(img, CAT_IMAGE_SIZE)
                        cats.append(img)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        if not cats:
            placeholder = pygame.Surface(CAT_IMAGE_SIZE)
            placeholder.fill(GRAY)
            cats.append(placeholder)
        
        return cats

    def spawn_new_figure(self):
        self.figure = Tetromino(GRID_W // 2 - 1, 0, self.next_shape_type)
        self.next_shape_type = random.choice(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])
        
        if self.figure.check_collision(0, 0, self.grid):
            self.game_over = True
            if self.score >= VICTORY_SCORE:
                self.victory = True
                self.current_cat = random.choice(self.victory_cats)
                print(f"VICTORY! Score: {self.score}")
            else:
                self.current_cat = random.choice(self.gameover_cats)
                print(f"GAME OVER! Score: {self.score}")

    def freeze_figure(self):
        for block_x, block_y in self.figure.shape:
            grid_x = self.figure.x + block_x
            grid_y = self.figure.y + block_y
            if 0 <= grid_y < GRID_H and 0 <= grid_x < GRID_W:
                self.grid[grid_y][grid_x] = self.figure.color

    def clear_lines(self):
        lines_to_clear = []

        for y in range(GRID_H):
            if None not in self.grid[y]:
                lines_to_clear.append(y)

        if lines_to_clear:
            for y in lines_to_clear:
                for x in range(GRID_W):
                    color = self.grid[y][x]
                    particle_x = x * BLOCK_SIZE + BLOCK_SIZE // 2
                    particle_y = y * BLOCK_SIZE + BLOCK_SIZE // 2
                    for _ in range(random.randint(5, 10)):
                        self.particles.append(Particle(particle_x, particle_y, color))
            
            for y in sorted(lines_to_clear, reverse=True):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_W)])

            lines_cleared = len(lines_to_clear)
            points = [0, 100, 300, 500, 800]
            self.score += points[lines_cleared]

    def draw_end_screen(self, title, title_color):
        self.screen.fill(BLACK)
        
        if self.current_cat:
            cat_rect = self.current_cat.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(self.current_cat, cat_rect)
        
        title_text = self.big_font.render(title, True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(score_text, score_rect)
        
        hint_text = self.small_font.render("Press ESC to exit", True, GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(hint_text, hint_rect)

    def run(self):
        while self.running:
            if self.victory:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            self.is_fullscreen = not self.is_fullscreen
                            flags = pygame.SCALED
                            if self.is_fullscreen:
                                flags |= pygame.FULLSCREEN
                            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
                            continue
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                
                self.draw_end_screen("VICTORY!", GOLD)
                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            if self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                
                self.draw_end_screen("GAME OVER!", RED)
                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.is_fullscreen = not self.is_fullscreen
                        flags = pygame.SCALED
                        if self.is_fullscreen:
                            flags |= pygame.FULLSCREEN
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
                        continue
                    
                    if event.key == pygame.K_ESCAPE:
                        self.is_paused = not self.is_paused

                    if not self.is_paused:
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
                    if not self.is_paused:
                        if not self.figure.check_collision(0, 1, self.grid):
                            self.figure.move_down()
                        else:
                            self.freeze_figure()
                            self.clear_lines()
                            self.spawn_new_figure()

            if not self.is_paused:
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
            
            pygame.draw.rect(self.screen, SIDEBAR_BG, (SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
            
            for y in range(GRID_H):
                for x in range(GRID_W):
                    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

            for y in range(GRID_H):
                for x in range(GRID_W):
                    if self.grid[y][x] is not None:
                        pixel_x = x * BLOCK_SIZE
                        pixel_y = y * BLOCK_SIZE
                        color = self.grid[y][x]
                        
                        for i in range(BLOCK_SIZE):
                            darken = (i / BLOCK_SIZE) * 0.2
                            r = int(color[0] * (1 - darken))
                            g = int(color[1] * (1 - darken))
                            b = int(color[2] * (1 - darken))
                            pygame.draw.line(self.screen, (r, g, b),
                                           (pixel_x, pixel_y + i),
                                           (pixel_x + BLOCK_SIZE - 1, pixel_y + i))
                        
                        border_color = tuple(min(c + 100, 255) for c in color)
                        pygame.draw.rect(self.screen, border_color,
                                       (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE), 2)
                        
                        highlight_color = tuple(min(c + 140, 255) for c in color)
                        pygame.draw.line(self.screen, highlight_color,
                                       (pixel_x + 3, pixel_y + 3),
                                       (pixel_x + BLOCK_SIZE - 4, pixel_y + 3), 2)
                        pygame.draw.line(self.screen, highlight_color,
                                       (pixel_x + 3, pixel_y + 3),
                                       (pixel_x + 3, pixel_y + BLOCK_SIZE - 4), 2)

            drop_distance = 0
            while not self.figure.check_collision(0, drop_distance + 1, self.grid):
                drop_distance += 1
            ghost_y = self.figure.y + drop_distance
            self.figure.draw_prediction(self.screen, ghost_y, GHOST)

            self.figure.draw(self.screen)
            
            next_text = self.font.render("NEXT", True, WHITE)
            self.screen.blit(next_text, (SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y))
            
            next_piece_preview = Tetromino(0, 0, self.next_shape_type)
            next_piece_preview.draw_next(self.screen, SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y + 50)
            
            score_label = self.font.render("SCORE", True, WHITE)
            self.screen.blit(score_label, (SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y + 170))
            
            score_value = self.font.render(str(self.score), True, WHITE)
            self.screen.blit(score_value, (SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y + 210))
            
            progress = min(self.score / VICTORY_SCORE * 100, 100)
            progress_text = self.font.render(f"{int(progress)}% to Victory", True, WHITE)
            self.screen.blit(progress_text, (SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y + 260))
            
            controls = [
                "Controls:",
                "Left/Right: Move",
                "Up: Rotate",
                "Down: Soft Drop",
                "Space: Hard Drop",
                "ESC: Pause",
                "F11: Fullscreen"
            ]
            for i, text in enumerate(controls):
                ctrl_text = self.small_font.render(text, True, GRAY)
                self.screen.blit(ctrl_text, (SIDEBAR_TEXT_X, SIDEBAR_TEXT_START_Y + 320 + i * 28))
            
            if self.is_paused:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, OVERLAY_ALPHA))
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.big_font.render("PAUSED", True, WHITE)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)

            for particle in self.particles[:]:
                particle.update()
                particle.draw(self.screen)
                if particle.lifetime <= 0:
                    self.particles.remove(particle)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
