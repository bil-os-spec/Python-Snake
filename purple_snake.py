import pygame
import time
import random

pygame.init()

purple = (128, 0, 128)
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)


width = 800
height = 600

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Purple Snake")

clock = pygame.time.Clock()

block_size = 20
speed = 15

font = pygame.font.SysFont(None, 50)

GAME_MODES = {
    "classic": "Classic Mode",
    "infinite": "Infinite Mode",
    "timed": "Timed Mode",
    "missions": "Missions Mode"
}

current_mode = "classic"

# Speed boosters and brakes
speed_booster = {"x": -1, "y": -1, "active": False, "timer": 0}
brake = {"x": -1, "y": -1, "active": False, "timer": 0}

# Destructible walls
destructible_walls = [
    {"x": 200, "y": 200, "hits": 3},
    {"x": 400, "y": 400, "hits": 3}
]

# Special attacks
special_attack = {"active": False, "timer": 0}

def draw_snake(block_size, snake_list):
    for block in snake_list:
        pygame.draw.rect(window, purple, [block[0], block[1], block_size, block_size])

def message(msg, color):
    text = font.render(msg, True, color)
    window.blit(text, [width / 6, height / 3])

def show_score(score):
    score_text = font.render(f"Score: {score}", True, purple)
    window.blit(score_text, [10, 10])

def welcome_screen():
    window.fill(black)
    message("Welcome to Snake Game", purple)
    pygame.display.update()
    time.sleep(2)
    window.fill(black)
    message("GitHub.com/developer2025", purple)
    pygame.display.update()
    time.sleep(2)

def spawn_speed_booster():
    speed_booster["x"] = round(random.randrange(0, width - block_size) / 20.0) * 20.0
    speed_booster["y"] = round(random.randrange(0, height - block_size) / 20.0) * 20.0
    speed_booster["active"] = True
    speed_booster["timer"] = time.time() + 5  # Lasts for 5 seconds

def spawn_brake():
    brake["x"] = round(random.randrange(0, width - block_size) / 20.0) * 20.0
    brake["y"] = round(random.randrange(0, height - block_size) / 20.0) * 20.0
    brake["active"] = True
    brake["timer"] = time.time() + 5  # Lasts for 5 seconds

def draw_destructible_walls():
    for wall in destructible_walls:
        if wall["hits"] > 0:
            pygame.draw.rect(window, red, [wall["x"], wall["y"], block_size, block_size])

def check_wall_collision(x, y):
    for wall in destructible_walls:
        if wall["hits"] > 0 and x == wall["x"] and y == wall["y"]:
            wall["hits"] -= 1
            return True
    return False

def activate_special_attack():
    special_attack["active"] = True
    special_attack["timer"] = time.time() + 10  # Lasts for 10 seconds

def game():
    welcome_screen()
    game_active = True
    game_over = False

    x = width / 2
    y = height / 2

    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
    food_y = round(random.randrange(0, height - block_size) / 20.
    food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0

    while game_active:
        while game_over:
            window.fill(black)
            message("Game Over! Press Q-Quit or C-Play Again", red)
            show_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_active = False
                        game_over = False
                    if event.key == pygame.K_c:
                        game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = block_size
                    x_change = 0
                elif event.key == pygame.K_SPACE and not special_attack["active"]:
                    activate_special_attack()

        # Check if snake hits the boundaries
        if x >= width or x < 0 or y >= height or y < 0:
            game_over = True

        x += x_change
        y += y_change

        window.fill(black)

        # Draw food
        pygame.draw.rect(window, green, [food_x, food_y, block_size, block_size])

        # Draw speed booster
        if speed_booster["active"] and time.time() < speed_booster["timer"]:
            pygame.draw.rect(window, blue, [speed_booster["x"], speed_booster["y"], block_size, block_size])
        else:
            speed_booster["active"] = False

        # Draw brake
        if brake["active"] and time.time() < brake["timer"]:
            pygame.draw.rect(window, red, [brake["x"], brake["y"], block_size, block_size])
        else:
            brake["active"] = False

        # Draw destructible walls
        draw_destructible_walls()

        # Check for collisions with walls
        if check_wall_collision(x, y):
            game_over = True

        # Check for collisions with speed booster
        if speed_booster["active"] and x == speed_booster["x"] and y == speed_booster["y"]:
            speed_booster["active"] = False
            speed = 30  # Increase speed

        # Check for collisions with brake
        if brake["active"] and x == brake["x"] and y == brake["y"]:
            brake["active"] = False
            speed = 5  # Decrease speed

        # Check for collisions with food
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
            food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0
            snake_length += 1
            if random.randint(0, 1) == 0:
                spawn_speed_booster()
            else:
                spawn_brake()

        # Update snake's body
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check for self-collision
        for block in snake_list[:-1]:
            if block == snake_head:
                game_over = True

        # Draw snake
        draw_snake(block_size, snake_list)

        # Show score
        show_score(snake_length - 1)

        # Update display
        pygame.display.update()

        # Set game speed
        clock.tick(speed)

    pygame.quit()
    quit()

# Start the game
game()
