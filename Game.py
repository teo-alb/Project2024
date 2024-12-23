import pygame # Importing the pygame module
from pygame import mixer
import os
import sysconfig
import random
import csv
import math
import Button

mixer.init()
pygame.init() # Initialize pygame

SCREEN_INFO = pygame.display.Info()
SCREEN_WIDTH = SCREEN_INFO.current_w
SCREEN_HEIGHT = SCREEN_INFO.current_h
SCALING = 2.5 # Used for images
SCALING = 4 # Used for images

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption('3B-SHOOTER')

# Game variables
paused = False

# Framerate
clock = pygame.time.Clock()
FRAMERATE = 60

# Game variables
GRAVITY = 0.5
SCROLL_THRESH = 200
TILE_SIZE = SCREEN_HEIGHT // 16
ROWS = 16
COLUMNS = 150
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# Player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


#Music and sounds
pygame.mixer.music.load('Audios/Cat-Burglars.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 6000)
jump_fx = pygame.mixer.Sound('Audios/audio_jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('Audios/audio_shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('Audios/audio_grenade.wav')
grenade_fx.set_volume(0.5)


# Load Images
#Buttons
start_img = pygame.image.load('icons/start_btn.png').convert_alpha()
exit_img = pygame.image.load('icons/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('icons/restart_btn.png').convert_alpha()

# Background
pine1_img = pygame.image.load('background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('background/mountain.png').convert_alpha()
sky1_img = pygame.image.load('background/sky1.png').convert_alpha()

# Storing tiles in list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Bullets
bullet_img = pygame.image.load('icons/bullet.png').convert_alpha()
# Grenades
grenade_img = pygame.image.load('icons/grenade.png').convert_alpha()
# Pick Up Boxes
health_box_img = pygame.image.load('icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# COLORS
BG_Color = (225, 225, 225)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Font definition
font = pygame.font.SysFont('Futura', 25)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_background():
    screen.fill((BG_Color))
    for x in range(8):
        width = sky1_img.get_width()
        screen.blit(sky1_img , (x * width  - bg_scroll * 0.3, 0))
        # screen.blit(mountain_img,(0,SCREEN_HEIGHT - mountain_img.get_height()-300))
        screen.blit(pine1_img, (x * width   - bg_scroll * 0.5 , SCREEN_HEIGHT - pine1_img.get_height() - 180))
        screen.blit(pine2_img, (x * width   - bg_scroll *0.8, SCREEN_HEIGHT - pine2_img.get_height()))

#Function to reset the level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #creating empty tile lists
    data = []
    for row in range(ROWS):
        r = [-1] * COLUMNS
        data.append(r)

    return data 

class Soldier(pygame.sprite.Sprite):
    def __init__(self, type, x, y, SCALING, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)  # Inherit functionality from sprite class, some built-in code
        pygame.sprite.Sprite.__init__(self)  # Inherit functionality from sprite class
        scale_factor = 0.5
        self.alive = True
        self.type = type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_timer = 0
        self.grenades = grenades
        self.health = 100
        self.maximum_health = self.health
        self.direction = 1  # Initial state
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0 : idle
        self.update_time = pygame.time.get_ticks()
        #ai variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load all images for all players
        animation_types = ['Idle', 'Running', 'Jump', 'Dead']
        for animation in animation_types:
            # Reset temp list of all images
            temp_list = []
            # Count number of files in each folder
            num_of_frames = len(os.listdir(f'{self.type}Soldier/{animation}'))  # Creates a list of the files in a directory
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.type}Soldier/{animation}/tile{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * SCALING), int(img.get_height()) * SCALING))
                # Scale the image
                img = pygame.transform.scale(img, (int(img.get_width() * SCALING), int(img.get_height() * SCALING)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Set the image and update the rect with scaled dimensions
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()  # Takes size of the img and creates a rectangle
        self.rect.center = (x, y)

        self.rect = self.image.get_rect()  # Create the rect based on the scaled image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.center = (x, y)  # Set initial position

    def update(self):
        self.update_animation()
        self.if_alive()

        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0
            self.if_alive()
        # Updating cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def move(self, moving_left, moving_right):
        # Reset move variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # Assigning movement variables to the player
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump == True and self.in_air == False:
            self.velocity_y = -10
            self.velocity_y = -15
            self.jump = False
            self.in_air = True

        # Add gravity effect
        self.velocity_y += GRAVITY
        if self.velocity_y > 10:
            self.velocity_y = 10
        dy += self.velocity_y

        #chec for collision
        # Check collision with floor
        for tile in world.obstacle_list:
            # Check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if ai hits the wall make it turn around
                if self.type == 'Black':
                    self.direction *= -1
                    self.move_counter = 0
            # Collision y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below the ground
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top  # The distance he can move
                # Check if above the ground (falling)
                elif self.velocity_y > 0:
                    self.velocity_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #Check if player drwons
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #Check for collisions with the 'exit' (next level) sign
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #Death by falling off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off the edges of the screen
        if self.type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH :
                dx = 0

        # Updating rectangle positions
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll based on player position
        if self.type == 'Blue':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE)-SCREEN_WIDTH) \
                        or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx  # Screen moves at the opposite direction of the player

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_timer == 0 and self.ammo > 0:
            self.shoot_timer = 20

            bullet = Bullet(self.rect.centerx + (self.rect.size[0] // 1.5 * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # Reduce ammo
            self.ammo -= 1
            #Shooting sound
            shot_fx.play()
    
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #Because 0 is for idling innit
                self.idling = True
                self.idling_counter = 50
            # Check if AI near the player
            if self.vision.colliderect(player.rect):
                # Stop running and turn towards player
                self.update_action(0)
                # Shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    # Update AI vision as enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll 
        self.rect.x += screen_scroll

    def update_animation(self):
        # Update animation
        ANIMATION_TIMER = 100
        # Update images
        self.image = self.animation_list[self.action][self.frame_index]
        # If enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_TIMER:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # If animation completes, start again
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            # Update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def if_alive(self):  # Basically to check if the enemy/player is dead or not and then to play through with the animation
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)  # 3 for Death

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        #pygame.draw.rect(screen, RED, self.rect, 2)  # Draw the rectangle in red
        #screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # Player
                        player = Soldier('Blue', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # Enemy
                        enemy = Soldier('Black', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:  # Ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # Grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # Health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # Exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        #to check if box is picked up
        if pygame.sprite.collide_rect(self, player):
            #check which box
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.maximum_health:
                    player.health = player.maximum_health
            elif self.item_type == 'Ammo':
                player.ammo += 10
            elif self.item_type == 'Grenade':
                player.grenades += 5
            #to delete item box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, maximum_health):
        self.x = x
        self.y = y
        self.health = health
        self.maximum_health = maximum_health

    def draw(self, health):
        #update health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.maximum_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))

        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
       

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #moving bullets
        self.rect.x += (self.direction * self.speed) + screen_scroll

        #Checking if the bullet is still in the viewable screen or not
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check if bullets hit the wall
        for tile in world.obstacle_list :
            if tile[1].colliderect(self.rect):
                self.kill()

        #collision with things
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 10
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.fuse_timer = 100
        self.velocity_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.rect.x += screen_scroll
        self.velocity_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.velocity_y

        #check for collision level
        for tile in world.obstacle_list : 
            #Checking collisions with 'walls'/'ground'
                if tile[1].colliderect(self.rect.x + dx , self.rect.y , self.width ,self.height):
                    self.direction *= -1
                    dx = self.direction * self.speed 
                #collision y direction
                if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width,self.height):
                    #check if below the ground
                    if self.velocity_y < 0 :
                        self.velocity_y = 0
                        dy = tile[1].bottom - self.rect.top #the distance he can move
                    #check if above the ground (falling)
                    elif self.velocity_y > 0 :
                        self.velocity_y = 0
                        self.in_air = False
                        self.speed = 0
                        dy = tile[1].top - self.rect.bottom
            
            
        #Update grenade position
        self.rect.x += dx
        self.rect.y += dy

        #Countdown timer
        self.fuse_timer -= 1
        if self.fuse_timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1.5)
            explosion_group.add(explosion)

            #Damage to things in the radius
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE:
                player.health -= 75
                print(player.health)

            
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE and \
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE:
                    enemy.health -= 75
                    print(enemy.health)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6 ):
            img = pygame.image.load(f'explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #Update Explosion animation
        self.counter += 1 

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0 
            self.frame_index += 1
            #If the animation is complete, delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: #Whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: #Vertical screen fade dow
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True
        
        return fade_complete



#Creating screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

#Creating Buttons
start_button = Button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 130, start_img, 1)
exit_button = Button.Button(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 60, exit_img, 1)
restart_button = Button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#Creating sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#creating empty list
world_data = []
for row in range(ROWS):
	r = [-1] * COLUMNS
	world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()

player = Soldier('Blue', 200, 200, 3, 5, 20, 7)
health_bar = HealthBar(10, 10, player.health, player.health)

#creating empty list
world_data = []
for row in range(ROWS):
	r = [-1] * COLUMNS
	world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()

player, health_bar = world.process_data(world_data)

def congratulations():
    screen.fill((0, 0, 0))  # Fill the screen with black (or any color for the background)
    
    # Load and display the congratulatory background image
    congrats_bg = pygame.image.load('background/congratulations.png')  # Make sure to have a background image file
    congrats_bg = pygame.transform.scale(congrats_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(congrats_bg, (0, 0))  # Display the background at position (0, 0)
    
    # Display the congratulations message
    draw_text('CONGRATULATIONS!', font, WHITE, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 3)
    draw_text('You completed Level 3!', font, WHITE, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2)
    draw_text('Press Enter to exit or ESC to return to the main menu', font, WHITE, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 1.5)

    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to exit
                    pygame.quit()  # Close the game
                    return
                elif event.key == pygame.K_ESCAPE:  # Press Escape to return to the main menu
                    global start_game
                    start_game = False  # Set the flag to False to trigger the main menu
                    return



running = True
while running :
    
    clock.tick(FRAMERATE)

    if start_game == False:
        #Draw the maim menu
        screen.fill(BG_Color)
        #Adding the buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            running = False
    else:
        #Update Bg
        draw_background()

        #draw the map
        world.draw()
        #show player health
        health_bar.draw(player.health)
        #show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        #show grenades
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        player.update()
        player.draw()
        
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #Update and draw groups 
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        
        #Intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        #update player actions
        if player.alive:
            #shooting bullets
            if shoot:
                player.shoot()
            #throwing the grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                        player.rect.top, player.direction)
                grenade_group.add(grenade)
                #Using grenades
                player.grenades -= 1
                grenade_thrown = True
                
            if player.in_air:
                player.update_action(2) #2 for jump
            elif moving_left or moving_right :
                player.update_action(1) #1 is running
            else :
                player.update_action(0) #0 is idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #Checking if the player completed the level
            if level_complete:
                if level == 3:  # After completing level 3, show the congratulations screen
                    congratulations()  # Show the congratulatory screen
                    running = False  # Stop the current game loop to return to the main menu
                else:
                    # Continue to the next level
                    start_intro = True
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS:
                        # Load in the new level data and create the world for the next level
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get(): #The Events Hnadler
        #quit game
        if event.type == pygame.QUIT:
            running = False
        '''Keyboard Inputs'''
        #Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_e:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                running = False
            
            #for releasing the keyboard
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_e:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()