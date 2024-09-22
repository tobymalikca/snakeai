import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake AI')

# Colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
darkred = pygame.Color(150, 0, 0)
green = pygame.Color(0, 255, 0)
darkgreen = pygame.Color(0, 150, 0)
blue = pygame.Color(0, 0, 255)
# orange = pygame.Color(255, 165 , 0)

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Snake and food settings
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
dead_snake = []
food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
food_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0
framerate = 25
deaths = 0
epilepsy = False # Epilepsy mode was only really used to debug the AI

# This function is called when the snake is about to move into itself
# If for example the snake was moving up, it runs a loop which scans to the left and right
# Once its own body is detected, it turns the opposite way
# This means the snake *usually* picks the side which has more free space
def resolve(direction):
    global framerate, epilepsy
    if epilepsy:
        framerate = 12
    i = 1
    while direction == 'up' or direction == 'down':
        if [(snake_pos[0] + 10*i) % width, snake_pos[1]] in snake_body:
            if [(snake_pos[0] - 10) % width, snake_pos[1]] in snake_body:
                return resolve('left')
            # print("Left")
            return 'LEFT'
        elif [(snake_pos[0] - 10*i) % width, snake_pos[1]] in snake_body:
            if [(snake_pos[0] + 10) % width, snake_pos[1]] in snake_body:
                return resolve('right')
            # print("Right")
            return 'RIGHT'
        i += 1
        if i > int(width/20):
            print("Timed out to left")
            return 'LEFT'

    while direction == 'left' or direction == 'right':
        if [snake_pos[0], (snake_pos[1] + 10*i) % height] in snake_body:
            if [snake_pos[0], (snake_pos[1] + 10) % height] in snake_body:
                if [(snake_pos[0] - 10)  % width, snake_pos[1]] in snake_body and [(snake_pos[0] + 10) % width, snake_pos[1]] in snake_body:
                    # print("Trapped - up")
                    return 'UP'
                else:
                    return resolve('up')
            # print("Up")
            return 'UP'
        elif [snake_pos[0], (snake_pos[1] - 10*i) % height] in snake_body:
            if [snake_pos[0], (snake_pos[1] - 10) % height] in snake_body:
                if [(snake_pos[0] - 10) % width, snake_pos[1]] in snake_body and [(snake_pos[0] + 10) % width, snake_pos[1]] in snake_body:
                    # print("Trapped - down")
                    return 'DOWN'
                else:
                    return resolve('down')
            # print("Down")
            return 'DOWN'
        i += 1
        if i > int(height/20):
            print("Timed out to up")
            return 'UP'

# This function casts a ray from the snake to the food through the borders
# If it reaches the food uninterrupted, the snake takes that path instead
def findShortcut(direction):
    match direction:
        case 'up':
            for i in range(int(height/20)):
                if [snake_pos[0], (snake_pos[1] - 10*(i+1)) % height] in snake_body:
                    return False
                elif [snake_pos[0], (snake_pos[1] - 10*(i+1)) % height] == [snake_pos[0], food_pos[1]]:
                    return True
        case 'down':
            for i in range(int(height/20)):
                if [snake_pos[0], (snake_pos[1] + 10*(i+1)) % height] in snake_body:
                    return False
                elif [snake_pos[0], (snake_pos[1] + 10*(i+1)) % height] == [snake_pos[0], food_pos[1]]:
                    return True
        case 'left':
            for i in range(int(width/20)):
                if [(snake_pos[0] - 10*(i+1)) % width, snake_pos[1]] in snake_body:
                    return False
                elif [(snake_pos[0] - 10*(i+1)) % width, snake_pos[1]] == food_pos:
                    return True
        case 'right':
            for i in range(int(width/20)):
                if [(snake_pos[0] + 10*(i+1)) % width, snake_pos[1]] in snake_body:
                    return False
                elif [(snake_pos[0] + 10*(i+1)) % width, snake_pos[1]] == food_pos:
                    return True
        case _:
            return False
    return False

def AI():
    global change_to, snake_pos, food_pos, snake_body, framerate, epilepsy

    if epilepsy:
        framerate = 25

    # Food is above the snake
    if food_pos[1] < snake_pos[1]:
        # Check if the snake can beeline the food by wrapping around the map
        if snake_pos[1] - food_pos[1] > int(height / 2) and findShortcut('down'):
            change_to = 'DOWN'
        elif [snake_pos[0], (snake_pos[1] - 10) % height] not in snake_body:
            change_to = 'UP'
        else:
            change_to = resolve('up')

    # Food is below the snake
    elif food_pos[1] > snake_pos[1]:
        # Check if the snake can beeline the food by wrapping around the map
        if food_pos[1] - snake_pos[1] > int(height / 2) and findShortcut('up'):
            change_to = 'UP'
        elif [snake_pos[0], (snake_pos[1] + 10) % height] not in snake_body:
            change_to = 'DOWN'
        else:
            change_to = resolve('down')

    # Food is to the left of the snake
    elif food_pos[0] < snake_pos[0]:
        # Check if the snake can beeline the food by wrapping around the map
        if snake_pos[0] - food_pos[0] > int(width / 2) and findShortcut('right'):
            change_to = 'RIGHT'
        elif [((snake_pos[0] - 10) % width), snake_pos[1]] not in snake_body:
            change_to = 'LEFT'
        else:
            change_to = resolve('left')

    # Food is to the right of the snake
    elif food_pos[0] > snake_pos[0]:
        # Check if the snake can beeline the food by wrapping around the map
        if food_pos[0] - snake_pos[0] > int(width / 2) and findShortcut('left'):
            change_to = 'LEFT'
        elif [((snake_pos[0] + 10) % width), snake_pos[1]] not in snake_body:
            change_to = 'RIGHT'
        else:
            change_to = resolve('right')

# Game Over function
def game_over():
    global deaths, snake_pos, dead_snake, snake_body
    # time.sleep(0.2)
    deaths += 1
    i = 1

    # Used to recolour the dead snakes
    dead_snake = snake_body.copy()

    # Respawn the snake somewhere randomly
    # The previous snake body still persists and fades out instead of vanishing instantly
    while True:
        new_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
        if new_pos not in snake_body:
            snake_pos = new_pos
            break
        if i >= 100:
            print("Defaulted game over loop")
            break

# Starting menu function
def main_menu():
    global epilepsy
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to start the game
                    menu = False
                if event.key == pygame.K_1:  # Toggle epilepsy mode
                    epilepsy = not epilepsy

        screen.fill(black)
        font = pygame.font.SysFont('arial', 50)
        title_surface = font.render('Zero Player Snake', True, white)
        title_rect = title_surface.get_rect(center=(width // 2, height // 3))
        screen.blit(title_surface, title_rect)

        font = pygame.font.SysFont('courier new', 30)
        start_surface = font.render('Press Enter to Start', True, green)
        start_rect = start_surface.get_rect(center=(width // 2, height // 2))
        screen.blit(start_surface, start_rect)

        font = pygame.font.SysFont('arial', 20)
        epilepsy_surface = font.render('Press 1 to toggle Epilepsy mode: ' + str(epilepsy), True, white)
        epilepsy_rect = epilepsy_surface.get_rect(center=(width // 2, height // 1.5))
        screen.blit(epilepsy_surface, epilepsy_rect)

        font = pygame.font.SysFont('arial', 15)
        small_text_surface = font.render('(Epilepsy mode ironically disables 10x speed on spacebar)', True, white)
        small_text_rect = small_text_surface.get_rect(center=(width // 2, height // 1.3))
        screen.blit(small_text_surface, small_text_rect)

        pygame.display.update()
        fps_controller.tick(15)

# Main function
def main():
    global change_to, direction, snake_pos, snake_body, food_pos, food_spawn, score, framerate, dead_snake

    main_menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if framerate == 25:
                        framerate = 250
                    else:
                        framerate = 25
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_UP:
            #         change_to = 'UP'
            #     elif event.key == pygame.K_DOWN:
            #         change_to = 'DOWN'
            #     elif event.key == pygame.K_LEFT:
            #         change_to = 'LEFT'
            #     elif event.key == pygame.K_RIGHT:
            #         change_to = 'RIGHT'

        AI()

        # Validate direction
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Update snake position
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos == food_pos:
            score += 10
            food_spawn = False
        else:
            snake_body.pop()
            if dead_snake:
                dead_snake.pop()

        # Spawn in the food
        if not food_spawn:
            i = 1
            # Jumpstart the snake if you want to skip the early game
            if False and len(snake_body) < 100:
                match direction:
                    case 'UP':
                        food_pos = [snake_pos[0], snake_pos[1] - 10]
                    case 'DOWN':
                        food_pos = [snake_pos[0], snake_pos[1] + 10]
                    case 'LEFT':
                        food_pos = [snake_pos[0] - 10, snake_pos[1]]
                    case 'RIGHT':
                        food_pos = [snake_pos[0] + 10, snake_pos[1]]
                if food_pos in snake_body or food_pos[0] <= 20 or food_pos[0] >= width-20 or food_pos[1] < 20 or food_pos[1] >= height-20:
                    food_pos = [random.randrange(2, 21) * 10, random.randrange(2, 21) * 10]
            else:
                while True:
                    i += 1
                    if i > 100:
                        print("Defaulted food spawn")
                        break
                    food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
                    # Not the best solution to reroll the spawn if it's on the level bounds
                    if food_pos[0] <= 0 or food_pos[0] >= width-10 or food_pos[1] <= 0 or food_pos[1] >= height-10:
                        continue
                    elif food_pos not in snake_body:
                        break

        food_spawn = True

        # Background
        screen.fill(black)

        # Draw snake
        for pos in snake_body:
            if epilepsy and framerate == 12:
                if pos in dead_snake:
                    pygame.draw.rect(screen, darkred, pygame.Rect(pos[0], pos[1], 10, 10))
                else:
                    pygame.draw.rect(screen, red, pygame.Rect(pos[0], pos[1], 10, 10))
            else:
                if pos in dead_snake:
                    pygame.draw.rect(screen, darkgreen, pygame.Rect(pos[0], pos[1], 10, 10))
                else:
                    pygame.draw.rect(screen, green, pygame.Rect(pos[0], pos[1], 10, 10))

        # Draw food
        pygame.draw.rect(screen, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        # Draw score/deaths
        font = pygame.font.SysFont('arial', 20)
        if deaths < 1:
            text_surface = font.render(f'Score: {score}', True, blue)
        else:
            text_surface = font.render(f'Score: {score} Deaths: {deaths}', True, blue)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)
        screen.blit(text_surface, text_rect)

        # Wrap around screen
        if snake_pos[0] < 0:
            snake_pos[0] = width - 10
        elif snake_pos[0] >= width:
            snake_pos[0] = 0
        if snake_pos[1] < 0:
            snake_pos[1] = height - 10
        elif snake_pos[1] >= height:
            snake_pos[1] = 0

        # Game Over conditions
        for block in snake_body[1:]:
            if snake_pos == block:
                game_over()

        # Refresh game screen
        pygame.display.update()

        # Frame Per Second /Refresh Rate
        fps_controller.tick(framerate)

if __name__ == "__main__":
    main()