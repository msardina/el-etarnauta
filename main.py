import pygame
import random
import math
from pygame import mixer
import os

pygame.init()
mixer.init()

# setup a screen
WIDTH, HEIGHT = 800, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Eternauta")

# clock
clock = pygame.time.Clock()
FPS = 60

# images
juan_img = pygame.image.load(os.path.join("assets", f"juan.png"))
ground_decorations = []

for img in range(1, 6):
    image = pygame.image.load(os.path.join("assets", f"snow{img}.png"))
    scale_image = pygame.transform.scale(
        image, (image.get_width() * 3, image.get_height() * 3)
    )

    ground_decorations.append(scale_image)

for img in range(1, 3):
    image = pygame.image.load(os.path.join("assets", f"bush{img}.png"))
    scale_image = pygame.transform.scale(
        image, (image.get_width() * 3, image.get_height() * 3)
    )

    ground_decorations.append(scale_image)


# classes
class Player:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.color = (160, 32, 240)
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height() / 2 + 20
        self.speed = 3
        self.is_firing = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):

        SCREEN.blit(self.img, (self.x, self.y))

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
        else:
            self.y -= 1

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_fire(self, keys):

        if keys[pygame.K_SPACE] and not self.is_firing:
            self.is_firing = True
            self.speed = 2
            return True

        if not keys[pygame.K_SPACE]:
            self.speed = 3
            self.is_firing = False

        return False


class Bullet:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 15
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(SCREEN, (0, 0, 0), self.rect)

    def move(self):
        self.y += 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_offscreen(self):

        if self.y > HEIGHT:
            return True
        return False


class Ground_Decoration:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def draw(self):

        SCREEN.blit(self.img, (self.x, self.y))

    def move(self):
        self.y -= 1

        if self.y < 0 - self.height:
            self.y = HEIGHT + 200
            self.x = random.randint(0, WIDTH - self.width)


def create_decorations():
    decorations = []

    for decoration_num in range(1, len(ground_decorations)):
        decorations.append(
            Ground_Decoration(
                random.randint(0, WIDTH),
                0 - (decoration_num * 200) * -1,
                ground_decorations[decoration_num - 1],
            )
        )

    return decorations


def game():

    # variables
    run = True

    # create objects
    player = Player(WIDTH // 2, HEIGHT // 2, juan_img)
    decorations = create_decorations()
    bullets = []

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

        for decoration in decorations:
            if decoration.y + decoration.height > player.y + player.height:
                player.draw()  # draw player before if infront of decoration
                decoration.draw()
                decoration.move()
            else:
                decoration.draw()
                decoration.move()
                player.draw()  # draw player after if behind decaration

        # fire bulets

        if player.is_fire(pygame.key.get_pressed()):
            bullets.append(
                Bullet(player.x + player.width // 2 - 6, player.y + player.height)
            )

        # move bullets

        if len(bullets) > 0:

            for bullet in bullets:
                bullet.draw()
                bullet.move()

                if bullet.is_offscreen():
                    bullets.remove(bullet)

        # move
        player.move(pygame.key.get_pressed())

        # update
        pygame.display.update()
        clock.tick(FPS)

        print(player.is_firing)


# run if file is main

if __name__ == "__main__":
    game()
