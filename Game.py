import pygame

pygame.init() #initialize pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
SCALING = 2.5 #used for images

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('shooter')

class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, scale,type):
        pygame.sprite.Sprite.__init__(self) #inherit functionality from sprite class , some built in code
        image = pygame.image.load(f'{type}Soldier/Idle/tile0.png')
        self.image = pygame.transform.scale(image, (int(image.get_width() * SCALING), int(image.get_height()) * SCALING))
        self.rect = self.image.get_rect() #takes size of the img and creates a rectangle
        self.rect.center = (x,y)     


    def draw(self):
        screen.blit(self.image, self.rect)

player = Soldier(400,400,3.5,'Blue')
player1 = Soldier(600,400,3.5,'Black')



running = True
while running :

    player.draw()
    player1.draw()
    
    for event in pygame.event.get():#get all the events
        #quit game
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()