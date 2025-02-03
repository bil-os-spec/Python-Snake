import pygame
import time
import random

pygame.init()

PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

WIDTH = 800
HEIGHT = 600

BLOCK_SIZE = 20
BASE_SPEED = 15

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Purple Snake")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 50)

def draw_snake(snake_list):
    for block in snake_list:
        pygame.draw.rect(window, PURPLE, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def message(msg, color, position):
    text = font.render(msg, True, color)
    window.blit(text, position)

def show_score(score):
    score_text = font.render(f"Score: {score}", True, PURPLE)
    window.blit(score_text, [10, 10])

def welcome_screen():
    window.fill(BLACK)
    message("Welcome to Snake Game", PURPLE, (WIDTH // 6, HEIGHT // 3))
    pygame.display.update()
    time.sleep(2)
    window.fill(BLACK)
    message("GitHub.com/developer2025", PURPLE, (WIDTH // 6, HEIGHT // 3))
    pygame.display.update()
    time.sleep(2)

def game():
    welcome_screen()
    
    game_active = True
    game_over = False
    
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0
    snake_list = []
    snake_length = 1
    speed = BASE_SPEED
    
    food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
    food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
    
    while game_active:
        while game_over:
            window.fill(BLACK)
            message("Game Over! Press Q-Quit or C-Play Again", RED, (WIDTH // 6, HEIGHT // 3))
            show_score(snake_length - 1)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_active = False
                        game_over = False
                    elif event.key == pygame.K_c:
                        return game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -BLOCK_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = BLOCK_SIZE
                    x_change = 0
        
        x += x_change
        y += y_change
        
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_over = True
        
        window.fill(BLACK)
        pygame.draw.rect(window, GREEN, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])
        
        # Update Snake List
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]
        
        # Check for Self Collision
        for block in snake_list[:-1]:
            if block == snake_head:
                game_over = True
        
        draw_snake(snake_list)
        show_score(snake_length - 1)
        pygame.display.update()
        
        # Check Food Collision
        if x == food_x and y == food_y:
            food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            snake_length += 1
        
        clock.tick(speed)
    
    pygame.quit()
    quit()

game()
