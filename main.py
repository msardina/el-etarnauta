import pygame
import random
import math
from pygame import mixer
import os

pygame.init()
mixer.init()

# setup a screen
WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Eternauta")

# images

snow_imgs = []

for img in range(1, 6):
    snow_imgs.append(pygame.image.load(os.path.join("assets", f"snow{img}.png")))


# classes
class Player:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.color = (160, 32, 240)
        self.img = img
        self.width = 50  # self.img.get_width()
        self.height = 100  # self.img.get_height()
        self.speed = 1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect)

    def move(self, keys):

        # move player with keys
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


class Ground_Snow:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def move(self):
        self.y += 0.50

        if self.y > HEIGHT:
            self.y = 0 - 200
            self.x = random.randint(0, WIDTH - self.width)


def create_snow():
    ground_snow = []

    for snow_num in range(1, 6):
        ground_snow.append(
            Ground_Snow(
                random.randint(0, WIDTH),
                0 - (snow_num * 200) * -1,
                snow_imgs[snow_num - 1],
            )
        )

    return ground_snow


def game():

    # variables
    run = True

    # create objects
    player = Player(WIDTH // 2, HEIGHT // 2, None)
    ground_snow = create_snow()

    # main loop
    while run:

        # loop through events in last frame
        for event in pygame.event.get():

            # if x button pressed then exit loop and quit python
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # draw
        SCREEN.fill("white")

        for snow in ground_snow:
            snow.draw()
            snow.move()

        player.draw()

        # move
        player.move(pygame.key.get_pressed())

        # update
        pygame.display.update()


# run if file is main

if __name__ == "__main__":
    game()
