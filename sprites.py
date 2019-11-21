#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Copyright (C) 2019 Andrés Segovia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import random
import pygame
from utils import load_image
from resources import *

# ------------------------------------------------------------------------------
#   PLAYER sprite
# ------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        dir_images = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "data", "images", "spaceship")
        for name_img in os.listdir(dir_images):
            current_img = load_image(
                os.path.join(dir_images, name_img), False, (LENGTH_SPACESHIP, LENGTH_SPACESHIP))
            self.images.append(current_img)

        assert(len(self.images) == 6)

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT)
        self.x_speed = 0  # X Displacement
        self.y_speed = 0  # Y Displacement

    def update(self):
        self.rect.move_ip((self.x_speed, self.y_speed))
        if self.rect.left < 0:  # In order not to exceed the limit of the window
            self.rect.left = 0
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

        if self.rect.top <= WINDOW_HEIGHT / 2:  # To determine that it does not exceed half of the screen
            self.rect.top = WINDOW_HEIGHT / 2
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        # To determine the direction of movement
        if self.x_speed < 0:  # LEFT
            if self.y_speed < 0:  # UP + LEFT
                self.image = self.images[5]
                motor_channel.play(motor_on_sound, loops=0,
                                   maxtime=0, fade_ms=0)
            else:  # only LEFT
                self.image = self.images[4]
                motor_channel.stop()
        elif self.x_speed > 0:  # RIGHT
            if self.y_speed < 0:  # UP + RIGHT
                self.image = self.images[3]
                motor_channel.play(motor_on_sound, loops=0,
                                   maxtime=0, fade_ms=0)
            else:  # only RIGHT
                self.image = self.images[2]
                motor_channel.stop()
        else:  # UP / DOWN
            if self.y_speed < 0:  # UP
                self.image = self.images[1]
                motor_channel.play(motor_on_sound, loops=0,
                                   maxtime=0, fade_ms=0)
            else:  # DOWN
                self.image = self.images[0]
                motor_channel.stop()


# ------------------------------------------------------------------------------
#   ENEMY sprite
# ------------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        path_img = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "data", "images", "resources", "droid.png")
        self.image = load_image(path_img, False)
        self.rect = self.image.get_rect()
        # Random positioning
        self.rect.centerx = random.randint(48, 752)
        self.rect.centery = random.randint(70, 230)
        self.x_speed = random.randint(-5, 5)
        self.y_speed = random.randint(-5, 5)
        if self.x_speed == 0:
            self.x_speed = 1
        elif self.y_speed == 0:
            self.y_speed = 1

    def update(self):
        self.rect.move_ip((self.x_speed, self.y_speed))

        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.x_speed = -(self.x_speed)

        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT/2:
            self.y_speed = -(self.y_speed)

        # This is to prevent the enemy from firing all the time.
        is_shoot = random.randint(1, 80) == 1
        if is_shoot == True:  # The droid fires only if allowed to do so.
            group_laser_enemy.add(LaserEnemy(self.rect.midbottom))
            laser_droid_sound.play()


# ------------------------------------------------------------------------------
#   ASTEROID sprite
# ------------------------------------------------------------------------------
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # To set a variable asteroid size
        self.size_asteroid = random.randint(
            ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        # To randomly determine if the current asteroid provides power
        self.is_energetic = (random.random() < PROB_ENERGETIC_ASTEROID)
        # Energy level that will be provided by the asteroid. 0 is without energy
        self.energy_lvl = 0
        if self.is_energetic:
            self.image = self.select_image(
                os.path.join("resources", "energetic_asteroid.png"))
            if self.size_asteroid <= 10:
                self.energy_lvl = 3
            elif self.size_asteroid <= 20:
                self.energy_lvl = 5
            elif self.size_asteroid <= 30:
                self.energy_lvl = 7
            elif self.size_asteroid > 30:
                self.energy_lvl = 10
        else:  # Asteroid without energy
            self.image = self.select_image(
                os.path.join("resources", "asteroid.png"))

        self.rect = pygame.Rect(random.randint(0, WINDOW_WIDTH - self.size_asteroid),
                                0 - self.size_asteroid, self.size_asteroid, self.size_asteroid)
        self.rect.centerx = random.randint(48, WINDOW_WIDTH)
        self.rect.centery = 0
        self.x_speed = random.randint(-(ASTEROID_MAX_SPEED),
                                      ASTEROID_MAX_SPEED)
        self.y_speed = random.randint(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)

    def update(self):
        self.rect.move_ip((self.x_speed, self.y_speed))

        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH or self.rect.bottom >= WINDOW_HEIGHT:
            self.kill()

    def select_image(self, archivo, is_energy_img=False):
        path_img = os.path.join('data', 'images', archivo)
        if is_energy_img is True:  # Determine if it is to change the image to energy
            image = load_image(path_img, False, (int(
                ASTEROID_MAX_SIZE/2), int(ASTEROID_MAX_SIZE/2)))
        else:
            image = load_image(
                path_img, False, (self.size_asteroid, self.size_asteroid))

        return image


# ------------------------------------------------------------------------------
#   LASER sprite
# ------------------------------------------------------------------------------
class PlayerLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(os.path.join(
            'data', 'images', 'resources', 'laser1.png'), False)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        if self.rect.bottom <= 0:
            self.kill()
        else:
            self.rect.move_ip((0, -10))


class LaserEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(os.path.join(
            'data', 'images', 'resources', 'laser3.png'), False)
        self.rect = self.image.get_rect()
        self.rect.midtop = pos

    def update(self):
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.kill()
        else:
            self.rect.move_ip((0, 6))


class TextBox(pygame.sprite.Sprite):
    def __init__(self, text, font, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.font = font
        self.text = text
        self.image = self.font.render(self.text, True, TEXTCOLOR)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        self.image = self.font.render(self.text, True, TEXTCOLOR)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, object_rect, type_explosion="explosion"):
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.rate_image = 0
        self.number_images = 6
        self.lst_img_explosion = []  # Contains the sprites that compose the explosion

        # We load the images depending on the type that is
        for i in range(0, self.number_images):
            path_img = os.path.join(
                'data', 'images', 'animation', type_explosion + str(i + 1) + '.png')
            self.lst_img_explosion.append(load_image(
                path_img, False, object_rect.size))

        self.image = self.lst_img_explosion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = object_rect.x
        self.rect.y = object_rect.y

    def update(self):
        self.rate_image += 1
        if self.rate_image >= DELAY_EXPLOSION:
            self.index += 1
            self.rate_image = 0
            # We show each image of the animation
            if self.index < len(self.lst_img_explosion):
                self.image = self.lst_img_explosion[self.index]
            else:
                self.kill()
# ------------------------------------------------------------
# I have to create it in this module because a class needs it.
# ------------------------------------------------------------
group_laser_enemy = pygame.sprite.RenderUpdates()

