import pygame #Importing the pygame module
import os

pygame.init() #initialize pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
SCALING = 2.5 #used for images

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('3 Bytes - SHOOTER')

#game variables
paused = False

#framerate
clock = pygame.time.Clock()
FRAMERATE = 60

#game variables
GRAVITY = 0.6
TILE_SIZE = 40

#player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#Load Images
#Bullets
bullet_img = pygame.image.load('icons/bullet.png').convert_alpha()
#Grenades
grenade_img = pygame.image.load('icons/grenade.png').convert_alpha()
#Pick Up Boxes
health_box_img = pygame.image.load('icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'
}

#COLORS
BG_Color = (225, 225, 225)
RED = (255, 0, 0)

def draw_background():
    screen.fill((BG_Color))
    pygame.draw.line(screen, RED, (0,300), (SCREEN_WIDTH, 300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, type, x, y, SCALING, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self) #inherit functionality from sprite class , some built in code
        self.alive = True
        self.type = type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_timer = 0
        self.grenades = grenades
        self.health = 100
        self.maximum_health = self.health
        self.direction = 1 #initial state 
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 #0 : idle
        self.update_time = pygame.time.get_ticks()

        #load all images for all players
        animation_types = ['Idle','Running','Jump', 'Dead']
        for animation in animation_types:
            #reset temp list of all images
            temp_list = []
            #count number of files in each folder
            num_of_frames = len(os.listdir(f'{self.type}Soldier/{animation}')) #creates a list of the files in a directory
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.type}Soldier/{animation}/tile{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * SCALING), int(img.get_height()) * SCALING))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() #takes size of the img and creates a rectangle
        self.rect.center = (x, y)     

    def update(self):
        self.update_animation()
        self.if_alive()
        #updating cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
   
    def move(self, moving_left , moving_right):
        #reset move variables
        dx = 0
        dy = 0

        #assigning movement variables to the player
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump 
        if self.jump ==True and self.in_air == False:
            self.velocity_y = -11
            self.jump = False
            self.in_air = True
        
        #add gravity effect
        self.velocity_y += GRAVITY
        if self.velocity_y > 10:
            self.velocity_y
        dy += self.velocity_y

        #Check Collision with floor
        if self.rect.bottom + dy > 300 :
            dy = 300 - self.rect.bottom
            self.in_air = False

        #updating rectangle positions
        self.rect.x += dx
        self.rect.y += dy


    def shoot(self):
        if self.shoot_timer == 0 and self.ammo > 0:
            self.shoot_timer = 20
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] //2 * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1


    def update_animation(self):
        #update animation
        ANIMATION_TIMER = 100
        #update images
        self.image = self.animation_list[self.action][self.frame_index]
        #if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_TIMER :
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation completes, start again
        if self.frame_index >= len(self.animation_list[self.action]) : 
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self , new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def if_alive(self): #Basically to check if the enemy/player is dead or not and then to play through with the animation
        if self.health <= 0:
            self.health = 0 
            self.speed = 0
            self.alive = False
            self.update_action(3) # 3 for Death




    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class item_box(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

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
        self.rect.x += (self.direction * self.speed)

        #Checking if the bullet is still in the viewable screen or not
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill
            #As soon as the bullets go off the screen, they die

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
        self.direction = direction


    def update(self):
        self.velocity_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.velocity_y

         #Check Collision with floor
        if self.rect.bottom + dy > 300 :
            dy = 300 - self.rect.bottom
            self.speed = 0

        #Checking collisions with 'walls'/'ground'
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed
            
        #Update grenade position
        self.rect.x += dx
        self.rect.y += dy

        #Countdown timer
        self.fuse_timer -= 1
        if self.fuse_timer <= 0:
            self.kill()
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


#Creating sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()



player = Soldier('Blue', 200, 200, 3, 5, 20, 7)
enemy = Soldier('Black', 400, 200, 3, 5, 20, 0)
enemy_group.add(enemy)


running = True
while running :
    
    clock.tick(FRAMERATE)

    draw_background()

    player.update()
    player.draw()
    
    for enemy in enemy_group:
        enemy.update()
        enemy.draw()

    #Update and draw groups 
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)

    
    
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
        player.move(moving_left, moving_right)

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