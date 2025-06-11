import pygame
import random
import math
from pygame import mixer
import os

pygame.init()
mixer.init()


# clock
clock = pygame.time.Clock()
FPS = 60


# setup font
font = pygame.font.SysFont(None, 50)
title_font = pygame.font.SysFont(None, 100)
medium_font = pygame.font.SysFont(None, 75)

# const
SCREEN_SPEED = 1

# music

shot_gun = pygame.mixer.Sound(os.path.join("sounds", "shotgun.wav"))

# images
juan_img = pygame.image.load(os.path.join("assets", f"juan.png"))
bug_img = pygame.image.load(os.path.join("assets", f"spider.png"))
blood_bug_img = pygame.image.load(os.path.join("assets", f"blood spider.png"))
ground_decorations = []
train_tracks = pygame.image.load(os.path.join("assets", "train.png"))

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

# setup a screen
WIDTH, HEIGHT = 800, train_tracks.get_height()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Eternauta")

# classes


class Bug:

    def __init__(self, x, y, normalimg, bloodimg):
        self.x = x
        self.y = y
        self.normalimg = normalimg
        self.bloodimg = bloodimg
        self.img = self.normalimg

        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = 5

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def move(self, playerx, playery):
        self.y -= SCREEN_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.y > playery:
            if random.randint(1, 5) == 1:
                self.y -= 3

        if self.y < playery:
            if random.randint(1, 5) == 1:
                self.y += 3

        if self.x > playerx:
            if random.randint(1, 5) == 1:
                self.x -= 3

        if self.x < playerx:
            if random.randint(1, 5) == 1:
                self.x += 3

    def is_offscreen(self):

        if self.y < 0 - self.height:
            return True
        return False

    def hit(self):

        self.lives -= 1
        self.img = self.bloodimg

        if self.lives == 0:
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 200
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.lives = 5

    def collide(self, playerrect):

        if pygame.Rect.colliderect(self.rect, playerrect):
            return True
        return False


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
            self.y -= SCREEN_SPEED

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_fire(self, keys):

        if keys[pygame.K_SPACE] and not self.is_firing:
            shot_gun.play()
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

    def collide_bug(self, bugrect):

        if pygame.Rect.colliderect(self.rect, bugrect):
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

    def move(self, reset, randomise_pos):
        self.y -= SCREEN_SPEED

        if self.y < 0 - self.height:
            self.y = HEIGHT + reset

            if randomise_pos:
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
    blood_timer = 0
    score = 0

    # create objects
    player = Player(WIDTH // 2, HEIGHT // 2, juan_img)
    decorations = create_decorations()
    bullets = []
    spiders = [Bug(random.randint(0, WIDTH), HEIGHT, bug_img, blood_bug_img)]
    train = Ground_Decoration(100, 0, train_tracks)
    train2 = Ground_Decoration(100, HEIGHT, train_tracks)

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

        train.draw()
        train2.draw()

        for decoration in decorations:
            if decoration.y + decoration.height > player.y + player.height:
                player.draw()  # draw player before if infront of decoration
                decoration.draw()
                decoration.move(200, True)
            else:
                decoration.draw()
                decoration.move(200, True)
                player.draw()  # draw player after if behind decaration

        for spider in spiders:
            spider.draw()

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

                for spider in spiders:
                    if bullet.collide_bug(spider.rect):
                        spider.hit()

                        score += 1

                        if bullet in bullets:
                            bullets.remove(bullet)
                        break

                    elif bullet.is_offscreen():
                        if bullet in bullets:
                            bullets.remove(bullet)

        # update blood timer
        blood_timer += 0.20

        if blood_timer == 1:
            for spider in spiders:
                spider.img = spider.normalimg
            blood_timer = 0

        # move
        player.move(pygame.key.get_pressed())

        for spider in spiders:
            spider.move(player.x, player.y)

            if spider.collide(player.rect):
                spider.y = HEIGHT + 200
                spider.x = random.randint(0, WIDTH)

        train.move(0, False)
        train2.move(0, False)

        # check if spider off screen

        for spider in spiders:
            if spider.is_offscreen():
                spider.y = HEIGHT + 200
                spider.x = random.randint(0, WIDTH)

        # add spiders

        if random.randint(1, 1200) == 120:
            spiders.append(
                Bug(random.randint(0, WIDTH), HEIGHT, bug_img, blood_bug_img)
            )

        #### draw score ####

        # render text
        score_txt = title_font.render(f"{score}", True, (0, 0, 0))

        # draw score
        SCREEN.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 20))

        # update
        pygame.display.update()
        clock.tick(FPS)


# run if file is main

if __name__ == "__main__":
    game()
