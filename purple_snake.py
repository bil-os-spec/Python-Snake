import pygame
import time
import random

pygame.init()

purple = (128, 0, 128)
white = (255, 255, 255)
black = (0, 0, 0)

width = 800
height = 600

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Purple Snake")

clock = pygame.time.Clock()

block_size = 20
speed = 15

font = pygame.font.SysFont(None, 50)

def draw_snake(block_size, snake_list):
    for block in snake_list:
        pygame.draw.rect(window, purple, [block[0], block[1], block_size, block_size])

def message(msg, color):
    text = font.render(msg, True, color)
    window.blit(text, [width / 6, height / 3])

def game():
    game_active = True
    game_over = False

    x = width / 2
    y = height / 2

    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
    food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0

    while game_active:
        while game_over:
            window.fill(white)
            message("You lost! Press Q to quit or C to play again", purple)
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
                if event.key == pygame.K_LEFT:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = block_size
                    x_change = 0

        if x >= width or x < 0 or y >= height or y < 0:
            game_over = True

        x += x_change
        y += y_change
        window.fill(black)
        pygame.draw.rect(window, purple, [food_x, food_y, block_size, block_size])
        snake_head = []
        snake_head.append(x)
        snake_head.append(y)
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for block in snake_list[:-1]:
            if block == snake_head:
                game_over = True

        draw_snake(block_size, snake_list)
        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
            food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0
            snake_length += 1

        clock.tick(speed)

    pygame.quit()
    quit()

game()
