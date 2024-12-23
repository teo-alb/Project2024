import pygame
import csv

# Pygame setup
pygame.init()

# Game settings

SCREEN_INFO = pygame.display.Info()
SCREEN_WIDTH = SCREEN_INFO.current_w
SCREEN_HEIGHT = SCREEN_INFO.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FRAMERATE = 60
font = pygame.font.SysFont('Arial', 20)
WHITE = (255, 255, 255)

# Level Data
ROWS = 16
COLUMNS = 16
TILE_SIZE = SCREEN_HEIGHT // 16

# Initialize game objects
enemy_group = pygame.sprite.Group()  # No enemies as per your request
bullet_group = pygame.sprite.Group()

# Create a simple level with just obstacles (level tiles)
world_data = []
with open('multiplayer_level.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        world_data.append([int(tile) for tile in row])

world = World()

# Player 1 and Player 2
player1 = Soldier('Blue', 200, 200, 3, 5, 20, 7)
player2 = Soldier('Red', 400, 200, 3, 5, 20, 7)

# Health bar (only for Player 1 for this case)
health_bar = HealthBar(10, 10, player1.health, player1.health)

# Key states for player 1 and player 2
moving_left1 = moving_right1 = False
moving_up1 = moving_down1 = False
shoot1 = False

moving_left2 = moving_right2 = False
moving_up2 = moving_down2 = False
shoot2 = False

# Create level world
world.process_data(world_data)

# Game loop
running = True
while running:
    clock.tick(FRAMERATE)
    screen.fill((0, 0, 0))  # Clear screen

    # Draw the background and level (only obstacles)
    world.draw()

    # Draw player health (for player 1 only in this case)
    health_bar.draw(player1.health)

    # Draw ammo for Player 1 and Player 2 (they have unlimited ammo)
    draw_text('AMMO: ', font, WHITE, 10, 35)
    for x in range(1):  # Infinite ammo, display a single bullet image just for reference
        screen.blit(bullet_img, (90 + (x * 10), 40))

    draw_text('AMMO: ', font, WHITE, 10, 70)
    for x in range(1):  # Infinite ammo for Player 2 as well
        screen.blit(bullet_img, (90 + (x * 10), 80))

    # Update and draw Player 1 and Player 2
    player1.update()
    player1.draw()
    player2.update()
    player2.draw()

    # Update and draw bullets
    bullet_group.update()
    bullet_group.draw(screen)

    # Check for collisions (bullets with players and level tiles)
    for bullet in bullet_group:
        if bullet.rect.colliderect(player1.rect):
            player1.health -= bullet.damage  # Deduct health for player 1
            bullet.kill()  # Destroy bullet after collision
        if bullet.rect.colliderect(player2.rect):
            player2.health -= bullet.damage  # Deduct health for player 2
            bullet.kill()  # Destroy bullet after collision

        for tile in world.obstacle_list:  # Check for bullet collision with level tiles
            if bullet.rect.colliderect(tile[1]):
                bullet.kill()  # Destroy bullet when colliding with a tile

    # Check for player collisions with level tiles (walls)
    for tile in world.obstacle_list:
        if player1.rect.colliderect(tile[1]):
            # Handle collision for player 1 (stop movement if colliding with walls)
            pass
        if player2.rect.colliderect(tile[1]):
            # Handle collision for player 2 (stop movement if colliding with walls)
            pass

    # Player input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Player 1 controls (WASD, Space for shoot)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left1 = True
            if event.key == pygame.K_d:
                moving_right1 = True
            if event.key == pygame.K_w:
                moving_up1 = True
            if event.key == pygame.K_s:
                moving_down1 = True
            if event.key == pygame.K_SPACE:
                shoot1 = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left1 = False
            if event.key == pygame.K_d:
                moving_right1 = False
            if event.key == pygame.K_w:
                moving_up1 = False
            if event.key == pygame.K_s:
                moving_down1 = False
            if event.key == pygame.K_SPACE:
                shoot1 = False

        # Player 2 controls (Arrow keys, P for shoot)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left2 = True
            if event.key == pygame.K_RIGHT:
                moving_right2 = True
            if event.key == pygame.K_UP:
                moving_up2 = True
            if event.key == pygame.K_DOWN:
                moving_down2 = True
            if event.key == pygame.K_p:
                shoot2 = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left2 = False
            if event.key == pygame.K_RIGHT:
                moving_right2 = False
            if event.key == pygame.K_UP:
                moving_up2 = False
            if event.key == pygame.K_DOWN:
                moving_down2 = False
            if event.key == pygame.K_p:
                shoot2 = False

    # Update player movements
    if player1.alive:
        player1.update_action(1 if moving_left1 or moving_right1 else 0)
        screen_scroll = player1.move(moving_left1, moving_right1)
    if player2.alive:
        player2.update_action(1 if moving_left2 or moving_right2 else 0)
        screen_scroll = player2.move(moving_left2, moving_right2)

    # Handle shooting for both players
    if shoot1 and player1.alive:
        player1.shoot()
    if shoot2 and player2.alive:
        player2.shoot()

    pygame.display.update()

pygame.quit()
