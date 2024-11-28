import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Helicopter Mini Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Player settings
player_size = int(50 * 2)  # Increased size of the helicopter
player_speed = 10

# Enemy settings
enemy_speed = 10
enemy_list = []

# Parachute settings
parachute_speed = 2
parachute_list = []

# Fuel settings
MAX_FUEL = 20 * 30  # 20 seconds * 30 FPS
fuel = MAX_FUEL
FUEL_WIDTH = 200
FUEL_HEIGHT = 20
REFUEL_RATE = 5  # Points per second

# Helipad settings
HELIPAD_WIDTH = 100
HELIPAD_HEIGHT = int(HELIPAD_WIDTH * (456/769))  # Maintain aspect ratio
HELIPAD_POS = [50, SCREEN_HEIGHT - HELIPAD_HEIGHT - 50]  # Bottom left with some padding

# Clock
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont("monospace", 35)
small_font = pygame.font.SysFont("monospace", 20)

# Border settings
BORDER_THICKNESS = 4

# Load helicopter image
helicopter_image = pygame.image.load('helicopter.png')
helicopter_image = pygame.transform.scale(helicopter_image, (player_size, player_size))

# Load and scale background image
background_image = pygame.image.load('city.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load enemy plane image
plane_image = pygame.image.load('plane.png')
plane_size = int(50 * 2)
plane_image = pygame.transform.scale(plane_image, (plane_size, plane_size))

# Load parachute image
parachute_size = int(30 * 2)
parachute_image = pygame.image.load('parachute.png')
parachute_image = pygame.transform.scale(parachute_image, (parachute_size, parachute_size))

# Load helipad image
helipad_image = pygame.image.load('helipad.png')
helipad_image = pygame.transform.scale(helipad_image, (HELIPAD_WIDTH, HELIPAD_HEIGHT))

# Functions
def draw_helipad():
    screen.blit(helipad_image, (HELIPAD_POS[0], HELIPAD_POS[1]))
    text = small_font.render("REFUEL", True, BLACK)
    text_rect = text.get_rect(center=(HELIPAD_POS[0] + HELIPAD_WIDTH//2, HELIPAD_POS[1] + HELIPAD_HEIGHT + 15))
    screen.blit(text, text_rect)

def check_refuel_zone(player_pos):
    # Get the center point of the helicopter
    player_center_x = player_pos[0] + player_size // 2
    player_center_y = player_pos[1] + player_size // 2
    
    # Check if the center point is within the helipad boundaries
    return (HELIPAD_POS[0] < player_center_x < HELIPAD_POS[0] + HELIPAD_WIDTH and 
            HELIPAD_POS[1] < player_center_y < HELIPAD_POS[1] + HELIPAD_HEIGHT)

def drop_enemies(enemy_list, parachute_list):
    delay = random.random()
    if len(enemy_list) < 10 and delay < 0.1:
        x_pos = SCREEN_WIDTH
        y_pos = random.randint(0, SCREEN_HEIGHT - int(50 * 2))  # Assuming max enemy size is 50
        enemy_list.append({'pos': [x_pos, y_pos], 'parachute_dropped': False})

def draw_enemies(enemy_list, parachute_list):
    for enemy in enemy_list:
        screen.blit(plane_image, (enemy['pos'][0], enemy['pos'][1]))
        # Randomly decide to drop a parachute alongside the plane if it's in the left half of the screen
        if enemy['pos'][0] < SCREEN_WIDTH // 2 and random.random() < 0.01 and not enemy['parachute_dropped']:  # 30% chance to drop a parachute
            parachute_list.append({'pos': [enemy['pos'][0], enemy['pos'][1]]})
            enemy['parachute_dropped'] = True

def draw_parachutes(parachute_list):
    for parachute in parachute_list:
        screen.blit(parachute_image, (parachute['pos'][0], parachute['pos'][1]))

def update_enemy_positions(enemy_list, score):
    for idx, enemy in enumerate(enemy_list):
        if enemy['pos'][0] >= 0:
            enemy['pos'][0] -= enemy_speed
        else:
            enemy_list.pop(idx)
    return score

def update_parachute_positions(parachute_list, player_pos, score):
    for idx, parachute in enumerate(parachute_list):
        if parachute['pos'][0] >= 0 and parachute['pos'][1] < SCREEN_HEIGHT:
            parachute['pos'][0] -= parachute_speed
            parachute['pos'][1] += parachute_speed
            if detect_collision(player_pos, parachute['pos'], int(30 * 2)):  # Assuming parachute size is 30
                score += 1  # Arbitrary score increment for collecting a parachute
                parachute_list.pop(idx)
        else:
            parachute_list.pop(idx)
    return score

def collision_check(enemy_list, player_pos):
    if check_refuel_zone(player_pos):  # No collisions while in refuel zone
        return False
    for enemy in enemy_list:
        if detect_collision(player_pos, enemy['pos'], int(50 * 1.2)):  # Reduced collision box to 1.2x plane size
            return True
    return False

def detect_collision(player_pos, enemy_pos, enemy_size):
    # Add some padding to make collision detection more forgiving
    padding = 20  # Increased horizontal padding to reduce collision box width
    vertical_padding = 25  # Increased vertical padding to reduce collision box height
    p_x = player_pos[0] + padding
    p_y = player_pos[1] + vertical_padding
    p_width = player_size - (2 * padding)
    p_height = player_size - (2 * vertical_padding)  # Reduced height of collision box

    e_x = enemy_pos[0] + padding
    e_y = enemy_pos[1] + vertical_padding
    e_width = enemy_size - (2 * padding)
    e_height = enemy_size - (2 * vertical_padding)  # Reduced height of collision box

    # Check if the rectangles overlap using smaller collision boxes
    if (p_x < e_x + e_width and
        p_x + p_width > e_x and
        p_y < e_y + e_height and
        p_y + p_height > e_y):
        return True
    return False

def draw_fuel_gauge(fuel):
    # Draw fuel gauge background
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - FUEL_WIDTH//2, 10, FUEL_WIDTH, FUEL_HEIGHT), 2)
    # Draw fuel level
    fuel_level = (fuel / MAX_FUEL) * FUEL_WIDTH
    fuel_percentage = (fuel / MAX_FUEL) * 100
    
    # Choose color based on fuel percentage
    if fuel_percentage > 50:
        color = GREEN
    elif fuel_percentage > 25:
        color = YELLOW
    else:
        color = RED
        
    pygame.draw.rect(screen, color, (SCREEN_WIDTH//2 - FUEL_WIDTH//2, 10, fuel_level, FUEL_HEIGHT))
    # Draw fuel text
    fuel_text = font.render("FUEL", True, BLACK)
    screen.blit(fuel_text, (SCREEN_WIDTH//2 - FUEL_WIDTH//2 - 80, 5))

# Game loop
lives = 5
score = 0

background_x = 0

while lives > 0:
    player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
    game_over = False
    fuel = MAX_FUEL
    paused = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lives = 0
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        # Create semi-transparent overlay
                        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                        overlay.fill((128, 128, 128))
                        overlay.set_alpha(128)
                        screen.blit(overlay, (0,0))
                        # Draw pause text
                        pause_text = font.render("PAUSED", True, WHITE)
                        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                        screen.blit(pause_text, text_rect)
                        pygame.display.update()

        if not paused:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP] and player_pos[1] > 0:
                player_pos[1] -= player_speed
            if keys[pygame.K_DOWN] and player_pos[1] < SCREEN_HEIGHT - player_size:
                player_pos[1] += player_speed
            if keys[pygame.K_LEFT] and player_pos[0] > 0:
                player_pos[0] -= player_speed
            if keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - player_size:
                player_pos[0] += player_speed

            # Update fuel
            if check_refuel_zone(player_pos):
                if fuel < MAX_FUEL:
                    fuel = min(MAX_FUEL, fuel + REFUEL_RATE)
            else:
                fuel -= 1
                
            if fuel <= 0:
                lives -= 1
                if lives > 0:
                    # Create semi-transparent overlay
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.fill((128, 128, 128))
                    overlay.set_alpha(128)
                    screen.blit(overlay, (0,0))
                    # Draw text
                    text = font.render("Out of Fuel!", True, WHITE)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    screen.blit(text, text_rect)
                    pygame.display.update()
                    time.sleep(2)
                    enemy_list.clear()
                    parachute_list.clear()
                game_over = True

            # Draw the moving background with parallax effect
            background_x -= 5
            if background_x <= -SCREEN_WIDTH:
                background_x = 0
            screen.blit(background_image, (background_x, 0))
            screen.blit(background_image, (background_x + SCREEN_WIDTH, 0))

            draw_enemies(enemy_list, parachute_list)
            draw_parachutes(parachute_list)
            draw_helipad()
            screen.blit(helicopter_image, (player_pos[0], player_pos[1]))

            drop_enemies(enemy_list, parachute_list)
            score = update_enemy_positions(enemy_list, score)
            score = update_parachute_positions(parachute_list, player_pos, score)

            if collision_check(enemy_list, player_pos):
                lives -= 1
                if lives > 0:
                    # Create semi-transparent overlay
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.fill((128, 128, 128))
                    overlay.set_alpha(128)
                    screen.blit(overlay, (0,0))
                    # Draw text
                    text = font.render("One life lost!", True, WHITE)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    screen.blit(text, text_rect)
                    pygame.display.update()
                    time.sleep(2)
                    enemy_list.clear()
                    parachute_list.clear()
                game_over = True

            score_text = font.render("Score: {0}".format(score), True, BLACK)
            screen.blit(score_text, (10, 10))

            lives_text = font.render("Lives: {0}".format(lives), True, BLACK)
            screen.blit(lives_text, (SCREEN_WIDTH - 200, 10))  # Adjusted position to move it left

            # Draw fuel gauge
            draw_fuel_gauge(fuel)

            clock.tick(30)

            pygame.display.update()

# Create semi-transparent overlay
overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
overlay.fill((128, 128, 128))
overlay.set_alpha(128)
screen.blit(overlay, (0,0))
# Draw game over text
text = font.render("Game Over", True, WHITE)
text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
screen.blit(text, text_rect)
pygame.display.update()
time.sleep(2)

pygame.quit()
