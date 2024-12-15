import pygame
import os

pygame.init() #initialize pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
SCALING = 2.5 #used for images

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('shooter')

#game variables
paused = False

#framerate
clock = pygame.time.Clock()
FRAMERATE = 60

#game variables
GRAVITY = 0.6

#player action variables
moving_left = False
moving_right = False

#COLORS
BLUE = (0,0,255)

def draw_background():
    screen.fill((200,144,0))
    pygame.draw.line(screen,BLUE,(0,300),(SCREEN_WIDTH,300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x_coordinate, y_coordinate, scale,type ,speed):
        pygame.sprite.Sprite.__init__(self) #inherit functionality from sprite class , some built in code
        self.alive = True
        self.type = type
        self.speed = speed
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
        animation_types = ['Idle','Running','Jump']
        for animation in animation_types:
            #reset temp list of all images
            temp_list = []
            #count number of files in each folder
            num_of_frames = len(os.listdir(f'{self.type}Soldier/{animation}')) #creates a list of the files in a directory
            for i in range(num_of_frames):
                image = pygame.image.load(f'{self.type}Soldier/{animation}/tile{i}.png')
                img = pygame.transform.scale(image, (int(image.get_width() * SCALING), int(image.get_height()) * SCALING))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() #takes size of the img and creates a rectangle
        self.rect.center = (x_coordinate,y_coordinate)     

    def move(self, moving_right , moving_left):
        #reset variables
        dx = 0
        dy = 0

        if moving_left:
            self.flip = True
            dx = -self.speed
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
            self.velocity_y = 10
        dy += self.velocity_y

        #Check Collision with floor
        if self.rect.bottom + dy > 300 :
            dy = 300 - self.rect.bottom
            self.in_air = False



        #updating rectangle positions
        self.rect.x += dx
        self.rect.y += dy



    def update_animation(self):
        #update animation
        ANIMATION_TIMER = 100
        #update images
        self.image = self.animation_list[self.action][self.frame_index]
        #if enough time has passed
        if pygame.time.get_ticks() - self.update_time >= ANIMATION_TIMER :
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        #if animation completes start again
        if self.frame_index >= len(self.animation_list[self.action]) : 
            self.frame_index = 0

    def update_action(self , new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

player = Soldier(400,400,3.5,'Blue',4)
player1 = Soldier(600,400,3.5,'Black',4)



running = True
while running :
    draw_background()
    clock.tick(FRAMERATE)

    player.update_animation()

    player.draw()
    player1.draw()
    
    #update player actions
    if player.alive == True:
        if player.in_air:
            player.update_action(2) #2 for jumo
        elif moving_left or moving_right :
            player.update_action(1) #1 is running
        else :
            player.update_action(0) #0 is idle
        player.move(moving_right,moving_left)

        for event in pygame.event.get():#get all the events
            #quit game
            if event.type == pygame.QUIT:
                running = False

            #for keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_w:
                    player.jump = True
                if event.key == pygame.K_ESCAPE:
                    paused = True
                
                
            
            #for releasing the keyboard
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False

    pygame.display.update()

pygame.quit()