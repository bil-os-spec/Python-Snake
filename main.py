import pygame
import sys
import time
import random
import os
from pygame.locals import *

pygame.init()

COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 165, 0),
    "CYAN": (0, 255, 255),
    "GRAY": (128, 128, 128)
}

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BLOCK_SIZE = 24
BASE_SPEED = 15
MAX_SPEED = 30
MIN_SPEED = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Snake Game")
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

class Snake:
    def __init__(self):
        self.reset()
        self.skin_index = 0
        self.skins = [COLORS["PURPLE"], COLORS["CYAN"], COLORS["ORANGE"], COLORS["GREEN"]]
        
    def reset(self):
        self.body = [[SCREEN_WIDTH//2, SCREEN_HEIGHT//2]]
        self.direction = "RIGHT"
        self.length = 1
        self.speed = BASE_SPEED
        self.invincible = False
        self.shield = False
        self.powerups = {}
        
    def move(self):
        head = self.body[0].copy()
        
        if self.direction == "RIGHT":
            head[0] += BLOCK_SIZE
        elif self.direction == "LEFT":
            head[0] -= BLOCK_SIZE
        elif self.direction == "UP":
            head[1] -= BLOCK_SIZE
        elif self.direction == "DOWN":
            head[1] += BLOCK_SIZE
            
        self.body.insert(0, head)
        if len(self.body) > self.length:
            self.body.pop()
            
    def grow(self):
        self.length += 1
        self.speed = min(self.speed + 0.5, MAX_SPEED)
        
    def shrink(self):
        self.length = max(1, self.length - 1)
        self.speed = max(self.speed - 1, MIN_SPEED)
        
    def draw(self):
        for index, block in enumerate(self.body):
            color = self.skins[self.skin_index]
            if index == 0:
                pygame.draw.rect(screen, COLORS["YELLOW"], (block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(screen, color, (block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

class Food:
    def __init__(self):
        self.types = {
            "normal": (COLORS["GREEN"], 1),
            "speed": (COLORS["CYAN"], 2),
            "slow": (COLORS["BLUE"], -1),
            "bonus": (COLORS["ORANGE"], 3)
        }
        self.respawn()
        
    def respawn(self):
        self.type = random.choice(list(self.types.keys()))
        self.color, self.value = self.types[self.type]
        self.pos = [
            random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
            random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
        ]
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], BLOCK_SIZE, BLOCK_SIZE))

class Obstacle:
    def __init__(self):
        self.positions = []
        self.moving = True
        self.directions = {}
        self.generate()
        
    def generate(self):
        for _ in range(10):
            pos = [
                random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            ]
            self.positions.append(pos)
            self.directions[tuple(pos)] = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            
    def move(self):
        if self.moving:
            for index, pos in enumerate(self.positions):
                direction = self.directions[tuple(pos)]
                new_pos = pos.copy()
                
                if direction == "UP":
                    new_pos[1] -= BLOCK_SIZE
                elif direction == "DOWN":
                    new_pos[1] += BLOCK_SIZE
                elif direction == "LEFT":
                    new_pos[0] -= BLOCK_SIZE
                elif direction == "RIGHT":
                    new_pos[0] += BLOCK_SIZE
                    
                if new_pos[0] < 0 or new_pos[0] >= SCREEN_WIDTH:
                    self.directions[tuple(pos)] = "LEFT" if direction == "RIGHT" else "RIGHT"
                elif new_pos[1] < 0 or new_pos[1] >= SCREEN_HEIGHT:
                    self.directions[tuple(pos)] = "UP" if direction == "DOWN" else "DOWN"
                else:
                    self.positions[index] = new_pos
                    del self.directions[tuple(pos)]
                    self.directions[tuple(new_pos)] = direction
                    
    def draw(self):
        for pos in self.positions:
            pygame.draw.rect(screen, COLORS["RED"], (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.obstacle = Obstacle()
        self.score = 0
        self.high_score = self.load_highscore()
        self.paused = False
        self.game_over = False
        self.effects = []
        self.backgrounds = [COLORS["BLACK"], (30, 30, 30), (50, 50, 100)]
        self.current_bg = 0
        self.powerup_duration = 5000
        
    def load_highscore(self):
        try:
            with open("highscore.dat", "r") as f:
                return int(f.read())
        except:
            return 0
            
    def save_highscore(self):
        with open("highscore.dat", "w") as f:
            f.write(str(max(self.score, self.high_score)))
            
    def check_collision(self):
        head = self.snake.body[0]
        
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT:
            if not self.snake.invincible:
                return True
            else:
                self.snake.body[0] = [
                    (head[0] + SCREEN_WIDTH) % SCREEN_WIDTH,
                    (head[1] + SCREEN_HEIGHT) % SCREEN_HEIGHT
                ]
                
        for block in self.snake.body[1:]:
            if head == block and not self.snake.shield:
                return True
                
        for obs in self.obstacle.positions:
            if head == obs and not self.snake.invincible:
                return True
                
        return False
        
    def handle_powerups(self):
        current_time = pygame.time.get_ticks()
        expired = []
        
        for powerup, end_time in self.snake.powerups.items():
            if current_time >= end_time:
                expired.append(powerup)
                
        for powerup in expired:
            del self.snake.powerups[powerup]
            if powerup == "invincible":
                self.snake.invincible = False
            elif powerup == "shield":
                self.snake.shield = False
                
    def add_effect(self, effect):
        self.effects.append(effect)
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.save_highscore()
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if self.game_over:
                    if event.key == K_r:
                        self.reset()
                    elif event.key == K_q:
                        self.save_highscore()
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == K_p:
                        self.paused = not self.paused
                    elif event.key == K_ESCAPE:
                        self.paused = True
                    elif not self.paused:
                        if event.key in [K_RIGHT, K_d] and self.snake.direction != "LEFT":
                            self.snake.direction = "RIGHT"
                        elif event.key in [K_LEFT, K_a] and self.snake.direction != "RIGHT":
                            self.snake.direction = "LEFT"
                        elif event.key in [K_UP, K_w] and self.snake.direction != "DOWN":
                            self.snake.direction = "UP"
                        elif event.key in [K_DOWN, K_s] and self.snake.direction != "UP":
                            self.snake.direction = "DOWN"
                        elif event.key == K_SPACE:
                            self.snake.skin_index = (self.snake.skin_index + 1) % len(self.snake.skins)
                        elif event.key == K_b:
                            self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
                            
    def reset(self):
        self.snake.reset()
        self.food.respawn()
        self.obstacle = Obstacle()
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def run(self):
        while True:
            self.handle_input()
            
            if self.game_over or self.paused:
                continue
                
            self.snake.move()
            
            if self.check_collision():
                self.game_over = True
                self.save_highscore()
                continue
                
            if self.snake.body[0] == self.food.pos:
                self.score += self.food.value
                self.snake.grow()
                self.food.respawn()
                self.add_effect("grow")
                
                if self.food.type == "speed":
                    self.snake.speed = min(self.snake.speed + 2, MAX_SPEED)
                elif self.food.type == "slow":
                    self.snake.speed = max(self.snake.speed - 2, MIN_SPEED)
                elif self.food.type == "bonus":
                    self.score += 5
                    
                if random.random() < 0.1:
                    self.snake.powerups["invincible"] = pygame.time.get_ticks() + self.powerup_duration
                    self.snake.invincible = True
                    
            self.handle_powerups()
            self.obstacle.move()
            
            screen.fill(self.backgrounds[self.current_bg])
            self.snake.draw()
            self.food.draw()
            self.obstacle.draw()
            
            score_text = font_small.render(f"Score: {self.score} | High Score: {self.high_score}", True, COLORS["WHITE"])
            screen.blit(score_text, (10, 10))
            
            if self.snake.invincible:
                timer = (self.snake.powerups["invincible"] - pygame.time.get_ticks()) // 1000
                inv_text = font_small.render(f"Invincible: {timer}s", True, COLORS["YELLOW"])
                screen.blit(inv_text, (10, 50))
                
            if self.game_over:
                self.show_game_over()
                
            if self.paused:
                self.show_pause_menu()
                
            pygame.display.update()
            clock.tick(self.snake.speed)
            
    def show_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font_large.render("Game Over", True, COLORS["RED"])
        score_text = font_medium.render(f"Final Score: {self.score}", True, COLORS["WHITE"])
        restart_text = font_small.render("Press R to Restart or Q to Quit", True, COLORS["WHITE"])
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT*2//3))
        
    def show_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        pause_text = font_large.render("Paused", True, COLORS["WHITE"])
        resume_text = font_medium.render("Press P to Resume", True, COLORS["WHITE"])
        quit_text = font_medium.render("Press Q to Quit", True, COLORS["WHITE"])
        
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT*2//3))

if __name__ == "__main__":
    game = Game()
    game.run()
