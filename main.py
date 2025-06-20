import pygame
import random
import math
from pygame import mixer
import os
import time

pygame.init()
mixer.init()


# clock
clock = pygame.time.Clock()
FPS = 60


# setup font
font = pygame.font.SysFont("freesansbold", 50)
title_font = pygame.font.SysFont(None, 100)
medium_font = pygame.font.SysFont(None, 75)

# const
SCREEN_SPEED = 1
SCORE_PER_LEVEL = 300

# music

shot_gun = pygame.mixer.Sound(os.path.join("sounds", "shotgun.wav"))
stage_pass = pygame.mixer.Sound(os.path.join("sounds", "record.wav"))
death_sfx = pygame.mixer.Sound(os.path.join("sounds", "death.mp3"))

# images
juan_img = pygame.image.load(os.path.join("assets", f"juan.png"))
bug_img = pygame.image.load(os.path.join("assets", f"spider.png"))
blood_bug_img = pygame.image.load(os.path.join("assets", f"blood spider.png"))
heart_img = pygame.image.load(os.path.join("assets", f"life.png"))
ground_decorations = []
train_tracks = pygame.image.load(os.path.join("assets", "train.png"))
end = pygame.image.load(os.path.join("assets", "end.png"))

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
WIDTH, HEIGHT = 800, train_tracks.get_height() - 2
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Eternauta (FAN GAME)")

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

    def move(self, player_x, player_y):
        self.y -= SCREEN_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # go in the direction of the player randomly

        if self.y > player_y:
            if random.randint(1, 5) == 1:
                self.y -= 3

        elif self.y < player_y:
            if random.randint(1, 5) == 1:
                self.y += 3

        if self.x > player_x:
            if random.randint(1, 5) == 1:
                self.x -= 3

        elif self.x < player_x:
            if random.randint(1, 5) == 1:
                self.x += 5

    def is_offscreen(self):
        if self.y < 0 - self.height:  # check if offscreen
            return True
        return False

    def hit(self):
        self.lives -= 1
        self.img = self.bloodimg

        if self.lives == 0:  # check if spider is dead
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 200
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.lives = 5

    def collide(self, playerrect):
        if pygame.Rect.colliderect(self.rect, playerrect):  # collision detection
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
        self.lives = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, shoulddraw):
        if shoulddraw:
            SCREEN.blit(self.img, (self.x, self.y))

    def move(self, keys):
        # move player with keys
        if keys[pygame.K_RIGHT]:

            if self.x < WIDTH - self.width:
                self.x += self.speed

        if keys[pygame.K_LEFT]:

            if self.x > 0:

                self.x -= self.speed

        if keys[pygame.K_DOWN]:

            if self.y < HEIGHT - self.height:
                self.y += self.speed

        if keys[pygame.K_UP]:

            if self.y > 0:
                self.y -= self.speed
        else:

            if self.y > 0:
                self.y -= SCREEN_SPEED

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_fire(self, keys):
        if keys[pygame.K_SPACE] and not self.is_firing:  # fire shot
            shot_gun.play()
            self.is_firing = True
            self.speed = 1

            if self.y > 0:
                self.y -= 3

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


class Lives:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img

    def draw(self, liveamount):

        for i in range(1, liveamount + 1):
            SCREEN.blit(
                self.img, (self.x + (20 * (i * 2)), self.y)
            )  # draw lives using maths


class Ground_Decoration:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):

        SCREEN.blit(self.img, (self.x, self.y))

    def move(self, reset, randomise_pos, trainrect1, trainrect2):
        self.y -= SCREEN_SPEED

        if self.y < 0 - self.height:
            self.y = HEIGHT + reset

            if randomise_pos:  # go to a random position
                self.x = random.randint(0, WIDTH - self.width)
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

                # dont spawn on train tracks
                while pygame.Rect.colliderect(
                    self.rect, trainrect1
                ) or pygame.Rect.colliderect(self.rect, trainrect2):

                    self.x = random.randint(0, WIDTH - self.width)
                    self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


def create_decorations():
    decorations = []

    for decoration_num in range(1, len(ground_decorations)):  # make decorations
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
    player_is_hit = False
    player_flash = True
    game_flash = 0
    player_last_hit = 0
    stage = 1

    # create objects
    player = Player(WIDTH // 2, HEIGHT // 2, juan_img)
    decorations = create_decorations()
    bullets = []
    spiders = [Bug(random.randint(0, WIDTH), HEIGHT, bug_img, blood_bug_img)]
    train = Ground_Decoration(100, 0, train_tracks)
    train2 = Ground_Decoration(100, HEIGHT, train_tracks)
    lives = Lives(
        WIDTH // 2
        - (heart_img.get_width() * player.lives + 20 * player.lives - 1) // 2
        - 10,
        80,
        heart_img,
    )

    game_timer = 0

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
                player.draw(player_flash)  # draw player before if infront of decoration
                decoration.draw()
                decoration.move(200, True, train.rect, train2.rect)
            else:
                decoration.draw()
                decoration.move(200, True, train.rect, train2.rect)

                player.draw(player_flash)  # draw player after if behind decaration

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

                for spider in spiders:  # loop through spiders to see if hit by bullet
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

        if blood_timer == 1:  # make blood animation for spiders reset
            for spider in spiders:
                spider.img = spider.normalimg
            blood_timer = 0

        # move
        player.move(pygame.key.get_pressed())

        for spider in spiders:
            spider.move(player.x, player.y)

            if spider.collide(player.rect):  # check for colliosn with player
                spider.y = HEIGHT + 200
                spider.x = random.randint(0, WIDTH)
                player.lives -= 1

                player_is_hit = True
                player_last_hit = game_timer

        train.move(0, False, train.rect, train2.rect)
        train2.move(0, False, train.rect, train2.rect)

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

        # check for game ending

        if player.lives == 0:
            game_over_txt = title_font.render(f"GAME OVER", True, (0, 0, 0))
            SCREEN.blit(
                game_over_txt, (WIDTH // 2 - game_over_txt.get_width() // 2, 200)
            )

            death_sfx.play()
            pygame.display.update()
            time.sleep(2)
            SCREEN.fill("black")

            run = False

        if player_is_hit:  # flash the player using math when hit

            if round(game_flash) % 2 == 0:
                player_flash = False
            else:
                player_flash = True

        # draw lives

        lives.draw(player.lives)

        if round(game_timer) - round(player_last_hit) == 2:
            player_is_hit = False
            player_flash = True

        # complete level 1

        if score >= SCORE_PER_LEVEL:
            stage_pass.play()

            for spider in spiders:  # hide spiders
                spider.x = 12304
                spider.y = 12345
                spider.draw()

                for decoration in decorations:
                    decoration.draw()

                train.draw()
                train2.draw()

            pygame.display.update()

            spiders = []

            while not player.y > HEIGHT:

                player.y += 4

                # draw
                SCREEN.fill("white")

                for decoration in decorations:
                    decoration.draw()

                train.draw()
                train2.draw()

                player.draw(True)

                # text
                stage_pass_text = font.render(f"STAGE {stage} PASSED", True, (0, 0, 0))
                reach_text = font.render(f"Which level can you reach?", True, (0, 0, 0))

                SCREEN.blit(
                    stage_pass_text,
                    (WIDTH // 2 - stage_pass_text.get_width() // 2, 200),
                )

                SCREEN.blit(
                    reach_text,
                    (WIDTH // 2 - reach_text.get_width() // 2, 250),
                )

                # update
                pygame.display.update()
                clock.tick(FPS)

            time.sleep(2)
            score = 0

            stage += 1

        # update
        pygame.display.update()
        clock.tick(FPS)

        game_timer += 0.016
        game_flash += 0.080


# run if file is main

if __name__ == "__main__":
    game()
