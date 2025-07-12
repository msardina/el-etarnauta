import pygame
import random
import math
from pygame import mixer
import os
import time
from pathlib import Path

pygame.init()
mixer.init()

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (128, 0, 0)
BLUE = (0, 0, 128)

# clock
clock = pygame.time.Clock()
FPS = 60

ASSETS_ROOT = Path("assets")
ASSETS_IMG = ASSETS_ROOT / "imgs"
ASSETS_SFX = ASSETS_ROOT / "sounds"

# setup font
font = pygame.font.SysFont("freesansbold", 50)
title_font = pygame.font.SysFont(None, 100)
medium_font = pygame.font.SysFont(None, 75)

# gun
chosen_gun = "shotgun"

# const
SCREEN_SPEED = 1
SCORE_PER_LEVEL = 300
SCALE_DECORATION_NUM = 3

# music
heart = pygame.mixer.Sound(ASSETS_SFX / "heartbeat.wav")
shot_gun = pygame.mixer.Sound(ASSETS_SFX / "gun.wav")
pistol_sfx = pygame.mixer.Sound(ASSETS_SFX / "pistol.wav")

stage_pass = pygame.mixer.Sound(ASSETS_SFX / "record.wav")
death_sfx = pygame.mixer.Sound(ASSETS_SFX / "death.mp3")
begin_sfx = pygame.mixer.Sound(ASSETS_SFX / "hover.wav")
intro_sfx = pygame.mixer.Sound(ASSETS_SFX / "lightsaber.mp3")

# images
juan_img = pygame.image.load(ASSETS_IMG / f"juan.png")
bug_img = pygame.image.load(ASSETS_IMG / f"spider.png")
blood_bug_img = pygame.image.load(ASSETS_IMG / f"blood spider.png")
explosion_img = pygame.image.load(ASSETS_IMG / f"explosion.png")
heart_img = pygame.image.load(ASSETS_IMG / f"life.png")
ground_decorations = []
train_tracks = pygame.image.load(ASSETS_IMG / "train.png")
end = pygame.image.load(ASSETS_IMG / "deathscreen.png")
title_img = pygame.image.load(ASSETS_IMG / "title.png")
arrow_img = pygame.image.load(ASSETS_IMG / "arrow.png")
gun_selection = pygame.image.load(ASSETS_IMG / "shotgun.png")
locked_gun_selection = pygame.image.load(ASSETS_IMG / "locked.png")
car_img = pygame.image.load(ASSETS_IMG / "car1.png")
car_img2 = pygame.image.load(ASSETS_IMG / "car2.png")
car_img3 = pygame.image.load(ASSETS_IMG / "car3.png")
car_imgs = [car_img, car_img2, car_img3]
pistol_gun_selection = pygame.image.load(ASSETS_IMG / "pistol.png")

# load snow asses
for img in range(1, 6):
    image = pygame.image.load(ASSETS_IMG / f"snow{img}.png")
    scale_image = pygame.transform.scale(
        image,
        (
            image.get_width() * SCALE_DECORATION_NUM,
            image.get_height() * SCALE_DECORATION_NUM,
        ),
    )

    ground_decorations.append(scale_image)

# load bush assets
for img in range(1, 3):
    image = pygame.image.load(ASSETS_IMG / f"bush{img}.png")
    scale_image = pygame.transform.scale(
        image,
        (
            image.get_width() * SCALE_DECORATION_NUM,
            image.get_height() * SCALE_DECORATION_NUM,
        ),
    )

    ground_decorations.append(scale_image)

# setup a screen
WIDTH, HEIGHT = 800, train_tracks.get_height() - 4
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Eternauta - a fan game")


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

    def is_location_free(self, x, y, otherrect):

        # check for collision
        if pygame.Rect.colliderect(
            pygame.Rect(x, y, self.width, self.height), otherrect
        ):
            return False
        return True

    def move(self, player_x, player_y, car_rect):
        self.y -= SCREEN_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # go in the direction of the player randomly

        if self.y > player_y and random.randint(1, 5) == 1:

            if self.is_location_free(self.x, self.y - 3, car_rect):
                self.y -= 3
        elif self.y < player_y and random.randint(1, 5) == 1:
            if self.is_location_free(self.x, self.y + 3, car_rect):
                self.y += 3

        if self.x > player_x and random.randint(1, 5) == 1:
            if self.is_location_free(self.x - 3, self.y, car_rect):
                self.x -= 3
        elif self.x < player_x and random.randint(1, 5) == 1:
            if self.is_location_free(self.x + 3, self.y, car_rect):
                self.x += 3

    def is_offscreen(self):
        return self.y < 0 - self.height  # check if offscreen

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 200
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = 5

    def hit(self):
        self.lives -= 1
        self.img = self.bloodimg

        if self.lives == 0:  # check if spider is dead
            self.reset()

    def collide(self, playerrect):
        return pygame.Rect.colliderect(self.rect, playerrect)  # collision detection


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

    def is_location_free(self, x, y, otherrect):

        # check for collision
        if pygame.Rect.colliderect(
            pygame.Rect(x, y, self.width, self.height), otherrect
        ):
            return False
        return True

    def move(self, keys, car_rect):
        # move player with keys
        if keys[pygame.K_RIGHT]:
            if self.x < WIDTH - self.width:
                if self.is_location_free(self.x + self.speed, self.y, car_rect):
                    self.x += self.speed

        if keys[pygame.K_LEFT]:
            if self.x > 0:

                if self.is_location_free(self.x - self.speed, self.y, car_rect):
                    self.x -= self.speed

        if keys[pygame.K_DOWN]:
            if self.y < HEIGHT - self.height:
                if self.is_location_free(self.x, self.y + self.speed, car_rect):
                    self.y += self.speed

        if keys[pygame.K_UP]:
            if self.y > 0:
                if self.is_location_free(self.x, self.y - self.speed, car_rect):
                    self.y -= self.speed
        else:
            if self.y > 0:
                self.y -= SCREEN_SPEED

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def shoot_grenade(self, keys):
        return keys[pygame.K_z]

    def is_fire(self, keys):
        if keys[pygame.K_SPACE] and not self.is_firing:  # fire shot
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
        pygame.draw.rect(SCREEN, BLACK, self.rect)

    def move(self):
        self.y += 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_offscreen(self):
        return self.y > HEIGHT

    def collide_bug(self, bugrect):
        return pygame.Rect.colliderect(self.rect, bugrect)


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


class Collectable_Life:

    def __init__(self, x, y, img):
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def reset(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.y = HEIGHT * 3

    def move(self):
        self.y -= SCREEN_SPEED

        if self.y < 0:
            self.reset()

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # update rect

    def is_collected(self, player_rect):
        return pygame.Rect.colliderect(self.rect, player_rect)


class Car:

    def __init__(self, x, y, imgs):
        self.x = x
        self.y = y
        self.imgs = imgs
        self.img = self.imgs[random.randint(0, 2)]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def move(self):
        self.y -= SCREEN_SPEED

        if self.y < 0 - self.height:
            self.y = HEIGHT + 200
            self.x = random.randint(0, WIDTH - self.width)
            self.img = self.imgs[random.randint(0, 2)]
            self.width = self.img.get_width()
            self.height = self.img.get_height()

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # update rect


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


def title():

    # variables

    title = True
    arrow_y = 375
    arrow_pressed_up = False
    arrow_pressed_down = False
    intro_x = 0
    gun_selection_on = False
    gun_selection_no = 1
    gun_selection_current_img = gun_selection
    gun_selection_changing = False
    global chosen_gun
    chosen_gun = "shotgun"

    # make screen black
    SCREEN.fill(BLACK)

    # play lightsaber sound
    intro_sfx.play()

    # title loop

    while title:

        # loop through evnets
        for event in pygame.event.get():

            # check for x button
            if event.type == pygame.QUIT:
                title = False
                pygame.quit()
                quit()

        # draw
        SCREEN.fill(BLACK)
        SCREEN.blit(title_img, (WIDTH // 2 - title_img.get_width() // 2, 0))
        SCREEN.blit(arrow_img, (345, arrow_y))
        pygame.draw.rect(SCREEN, (0, 0, 0), (intro_x, 0, WIDTH, 300))

        # move

        # keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            if not arrow_pressed_up:
                arrow_y -= 32
                arrow_pressed_up = True
                begin_sfx.play()

        else:
            arrow_pressed_up = False

        if keys[pygame.K_DOWN]:
            if not arrow_pressed_down:
                arrow_y += 32
                arrow_pressed_down = True
                begin_sfx.play()
        else:
            arrow_pressed_down = False

        # reset arrow positions

        if arrow_y < 375:
            arrow_y = 375 + 32
        if arrow_y > 375 + 32:
            arrow_y = 375
        if keys[pygame.K_RETURN]:
            if arrow_y == 375:
                title = False
                begin_sfx.play()

            elif arrow_y == 375 + 32:
                gun_selection_on = True
                begin_sfx.play()

        ##### GUN SELECTION ######

        if gun_selection_on:
            if keys[pygame.K_z]:
                gun_selection_on = False
                begin_sfx.play()

            if keys[pygame.K_RIGHT] and not gun_selection_changing:
                gun_selection_no += 1
                begin_sfx.play()
                gun_selection_changing = True
                if gun_selection_no > 2:
                    gun_selection_no = 0

            elif keys[pygame.K_LEFT] and not gun_selection_changing:
                gun_selection_no -= 1
                gun_selection_changing = True
                begin_sfx.play()

                if gun_selection_no < 0:
                    gun_selection_no = 2

            if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                gun_selection_changing = False

        if gun_selection_no == 1:
            gun_selection_current_img = gun_selection
            chosen_gun = "shotgun"
        elif gun_selection_no == 0:
            gun_selection_current_img = locked_gun_selection
            chosen_gun = "shotgun"
        else:
            gun_selection_current_img = pistol_gun_selection
            chosen_gun = "pistol"

        # move rect
        if intro_x < WIDTH:
            intro_x += 7

        # draw gun selection

        if gun_selection_on:
            SCREEN.blit(
                gun_selection_current_img,
                (WIDTH // 2 - gun_selection_current_img.get_width() // 2, 0),
            )

        # update
        pygame.display.update()
        clock.tick(FPS)


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
    difficulty = 700
    game_timer = 0
    global SCREEN_SPEED
    SCREEN_SPEED = 1
    global chosen_gun

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
    car = Car(random.randint(0, WIDTH), HEIGHT - 200, car_imgs)
    collect_heart = Collectable_Life(random.randint(0, WIDTH), HEIGHT * 3, heart_img)
    heart.play()
    grenade_y = HEIGHT
    grenade_on = False
    mirror = False

    # main loop
    while run:

        # loop through events in last frame
        for event in pygame.event.get():

            # if x button pressed then exit loop and quit python
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if random.randint(1, 1200) == 1:
            heart.play()

        # draw
        SCREEN.fill(WHITE)

        train.draw()
        train2.draw()
        car.draw()
        collect_heart.draw()

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

            if chosen_gun == "shotgun":
                shot_gun.play()
            if chosen_gun == "pistol":
                pistol_sfx.play()

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

        # check for grenades

        if player.shoot_grenade(pygame.key.get_pressed()):
            for spider in spiders:
                spider.reset()
                SCREEN.blit(
                    explosion_img,
                    (
                        WIDTH // 2 - explosion_img.get_width() // 2,
                        HEIGHT // 2 - explosion_img.get_height() // 2,
                    ),
                )

        # update blood timer
        blood_timer += 0.20

        if blood_timer == 1:  # make blood animation for spiders reset
            for spider in spiders:
                spider.img = spider.normalimg
            blood_timer = 0

        # move
        player.move(pygame.key.get_pressed(), car.rect)

        for spider in spiders:
            spider.move(player.x, player.y, car.rect)

            if spider.collide(player.rect):  # check for colliosn with player
                spider.y = HEIGHT + 200
                spider.x = random.randint(0, WIDTH)
                player.lives -= 1

                player_is_hit = True
                player_last_hit = game_timer

        train.move(0, False, train.rect, train2.rect)
        train2.move(0, False, train.rect, train2.rect)
        car.move()
        collect_heart.move()

        # add hearts

        if collect_heart.is_collected(player.rect):
            collect_heart.reset()
            player.lives += 1

        # check if spider off screen

        for spider in spiders:
            if spider.is_offscreen():
                spider.y = HEIGHT + 200
                spider.x = random.randint(0, WIDTH)

        # add spiders
        if random.randint(1, difficulty) == 1:
            spiders.append(
                Bug(random.randint(0, WIDTH), HEIGHT + 200, bug_img, blood_bug_img)
            )

        #### draw score ####

        # render text
        score_txt = title_font.render(f"{score}", True, BLACK)

        # draw score
        SCREEN.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 20))

        # check for game ending

        if player.lives == 0:
            game_over_txt = title_font.render(f"GAME OVER", True, BLACK)
            SCREEN.blit(
                game_over_txt, (WIDTH // 2 - game_over_txt.get_width() // 2, 200)
            )

            death_sfx.play()
            time.sleep(2)
            pygame.display.update()
            time.sleep(2)

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
            spiders = []  # reset spiders

            while not player.y > HEIGHT:

                player.y += 4

                # draw
                SCREEN.fill((255, 255, 255))

                for decoration in decorations:
                    decoration.draw()

                train.draw()
                train2.draw()

                player.draw(True)

                # text
                stage_pass_text = font.render(f"STAGE {stage} PASSED", True, BLACK)
                reach_text = font.render(f"Which level can you reach?", True, BLACK)

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

            if difficulty > 100:
                difficulty -= 100

            if difficulty - 100 < 100:
                difficulty = 1
                print("difficulty ramped")
            stage += 1
            SCREEN_SPEED += 0.5

        # update
        pygame.display.update()
        clock.tick(FPS)

        game_timer += 0.016
        game_flash += 0.080


# run then game

if __name__ == "__main__":

    while True:
        title()
        game()
