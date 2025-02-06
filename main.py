import pygame
import time
import random
import os

pygame.init()

PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

WIDTH = 800
HEIGHT = 600

BLOCK_SIZE = 20
BASE_SPEED = 10

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Purple Snake")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 50)

food_sound = pygame.mixer.Sound("sounds/food.wav")
crash_sound = pygame.mixer.Sound("sounds/crash.wav")
bg_music = pygame.mixer.music.load("music/background.mp3")

def draw_snake(snake_list):
    for block in snake_list:
        pygame.draw.rect(window, PURPLE, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def message(msg, color, position):
    text = font.render(msg, True, color)
    window.blit(text, position)

def show_score(score):
    score_text = font.render(f"Score: {score}", True, PURPLE)
    window.blit(score_text, [10, 10])

def draw_power_up(x, y):
    pygame.draw.circle(window, YELLOW, (x, y), BLOCK_SIZE // 2)

def display_lives(lives):
    lives_text = font.render(f"Lives: {lives}", True, GREEN)
    window.blit(lives_text, [WIDTH - 150, 10])

def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(window, RED, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])

def check_collision(x, y, obstacles):
    for obs in obstacles:
        if x == obs[0] and y == obs[1]:
            return True
    return False

def game_over_screen(score):
    window.fill(BLACK)
    message("Game Over! Press Q-Quit or C-Play Again", RED, (WIDTH // 6, HEIGHT // 3))
    show_score(score)
    pygame.display.update()

def game():
    game_active = True
    game_over = False

    x = random.choice([0, WIDTH // 4, WIDTH // 2, WIDTH - BLOCK_SIZE])
    y = random.choice([0, HEIGHT // 4, HEIGHT // 2, HEIGHT - BLOCK_SIZE])
    x_change = 0
    y_change = 0
    snake_list = []
    snake_length = 1
    speed = BASE_SPEED

    food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
    food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

    obstacles = [[random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                  random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)] for _ in range(5)]
    power_up_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
    power_up_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

    lives = 3

    pygame.mixer.music.play(-1, 0.0)

    while game_active:
        while game_over:
            game_over_screen(snake_length - 1)

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

        for obs in obstacles:
            pygame.draw.rect(window, RED, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])
            if x == obs[0] and y == obs[1]:
                crash_sound.play()
                game_over = True

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for block in snake_list[:-1]:
            if block == snake_head:
                crash_sound.play()
                game_over = True

        if x == power_up_x and y == power_up_y:
            snake_length += 1
            power_up_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            power_up_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

        draw_snake(snake_list)
        draw_obstacles(obstacles)
        show_score(snake_length - 1)
        display_lives(lives)

        if x == food_x and y == food_y:
            food_sound.play()
            food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            snake_length += 1
            speed += 1

        if random.random() < 0.01:
            power_up_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            power_up_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

        draw_power_up(power_up_x, power_up_y)

        pygame.display.update()

        clock.tick(speed)

    pygame.quit()
    quit()

game()
