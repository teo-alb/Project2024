import pygame

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

#player action variables
moving_left = False
moving_right = False

def draw_background():
    screen.fill((200,144,0))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x_coordinate, y_coordinate, scale,type ,speed):
        pygame.sprite.Sprite.__init__(self) #inherit functionality from sprite class , some built in code
        self.type = type
        self.speed = speed
        self.direction = 1 #initial state 
        self.flip = False
        image = pygame.image.load(f'{self.type}Soldier/Idle/tile0.png')
        self.image = pygame.transform.scale(image, (int(image.get_width() * SCALING), int(image.get_height()) * SCALING))
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

        self.rect.x += dx
        self.rect.y += dy


    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

player = Soldier(400,400,3.5,'Blue',4)
player1 = Soldier(600,400,3.5,'Black',4)



running = True
while running :
    draw_background()
    clock.tick(FRAMERATE)

    player.draw()
    player1.draw()
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
            if event.key == pygame.K_ESCAPE:
                paused = True
        
        #for releasinf the keyboard
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()

pygame.quit()