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

snake_skins = [PURPLE, BLUE, GREEN, RED]
backgrounds = [BLACK, (50, 50, 50), (0, 0, 255)]

def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def message(msg, color, position):
    text = font.render(msg, True, color)
    window.blit(text, position)

def show_score(score):
    score_text = font.render(f"Score: {score}", True, PURPLE)
    window.blit(score_text, [10, 10])

def countdown():
    for i in range(3, 0, -1):
        window.fill(BLACK)
        message(f"Game Over! Restarting in {i}...", WHITE, (WIDTH // 4, HEIGHT // 3))
        pygame.display.update()
        time.sleep(1)

def save_score_to_log(score):
    with open("scores.log", "a") as f:
        f.write(f"{score}\n")

def draw_snake(snake_list, skin_color):
    for block in snake_list:
        pygame.draw.rect(window, skin_color, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def game():
    game_active = True
    game_over = False
    paused = False
    speed = BASE_SPEED
    snake_skin = random.choice(snake_skins)
    background = random.choice(backgrounds)
    x = random.choice([0, WIDTH // 4, WIDTH // 2, WIDTH - BLOCK_SIZE])
    y = random.choice([0, HEIGHT // 4, HEIGHT // 2, HEIGHT - BLOCK_SIZE])
    x_change = 0
    y_change = 0
    snake_list = []
    snake_length = 1

    food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
    food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

    obstacles = [[random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                  random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)] for _ in range(5)]

    powerups = []
    powerup_timer = 0
    move_obstacles = True

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
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    if paused:
                        game_active = False
                    else:
                        paused = True
                elif event.key == pygame.K_t:
                    x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
                    y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

        if paused:
            window.fill(BLACK)
            message("Paused - Press P to Resume or ESC to Exit", WHITE, (WIDTH // 4, HEIGHT // 3))
            pygame.display.update()
            continue

        x += x_change
        y += y_change

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            crash_sound.play()
            game_over = True

        window.fill(background)
        pygame.draw.rect(window, GREEN, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])

        for obs in obstacles:
            pygame.draw.rect(window, RED, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])
            if x == obs[0] and y == obs[1]:
                crash_sound.play()
                game_over = True

        if move_obstacles:
            for obs in obstacles:
                obs[0] += random.choice([-1, 1]) * BLOCK_SIZE
                obs[1] += random.choice([-1, 1]) * BLOCK_SIZE

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for block in snake_list[:-1]:
            if block == snake_head:
                crash_sound.play()
                game_over = True

        draw_snake(snake_list, snake_skin)
        show_score(snake_length - 1)
        pygame.display.update()

        if x == food_x and y == food_y:
            food_sound.play()
            food_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            food_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            snake_length += 1
            speed += 1

        if random.random() < 0.01:
            powerup_x = random.randrange(0, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
            powerup_y = random.randrange(0, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            powerups.append([powerup_x, powerup_y])

        for powerup in powerups:
            pygame.draw.rect(window, YELLOW, [powerup[0], powerup[1], BLOCK_SIZE, BLOCK_SIZE])
            if x == powerup[0] and y == powerup[1]:
                powerups.remove(powerup)
                speed += 2

        save_score_to_log(snake_length - 1)

        if snake_length - 1 > load_highscore():
            save_highscore(snake_length - 1)

        clock.tick(speed)

    countdown()
    pygame.quit()
    quit()

game()
