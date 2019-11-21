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


from os import path
import random
import pygame
from utils import load_image, load_sound

INIT_ENERGY = 100
LENGTH_SPACESHIP = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
DISPLAYMODE = (WINDOW_WIDTH, WINDOW_HEIGHT)
TEXTCOLOR = (255, 255, 255)
FPS = 40
# To limit the total amount of droids that can be generated without filling the screen.
MAX_NUMBER_DROIDS = 15
ASTEROID_MIN_SIZE = 10
ASTEROID_MAX_SIZE = 40
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 8
DELAY_EXPLOSION = 5  # To simulate a delay in the explosion animation
ADDNEW_ASTEROID_RATE = 7
RATE_PLAYER_SPEED = 6
# Probability that determines if it's an energetic asteroid.
PROB_ENERGETIC_ASTEROID = 0.4
OBJECTIVE_LVL = 100 # Destroy 100 enemies


pygame.init()
window = pygame.display.set_mode(DISPLAYMODE)
font1 = pygame.font.SysFont("Liberation Serif", 24)
font2 = pygame.font.SysFont("Liberation Serif", 20)
font3 = pygame.font.SysFont("Arial", 20)
font4 = pygame.font.SysFont("Times New Roman", 36)
font5 = pygame.font.SysFont("Liberation Serif", 40)  # Points
font6 = pygame.font.SysFont("Sans Serif", 23)

# Set up sounds
intro_sound = load_sound('intro.ogg', 0.3)
background_sound = load_sound('game_music.ogg', 1.0)
explosion_sound = load_sound('explosion1.ogg', 0.3)
motor_on_sound = load_sound('motor_on.ogg', 0.4)
pickup_sound = load_sound('pickup.ogg', 0.3)
game_over_sound = load_sound('game_over.ogg', 1.0)
game_lost_sound = load_sound('game_lost.ogg', 1.0)
game_won_sound = load_sound('game_won.ogg', 1.0)

# We randomly select any of these sounds for the enemy
lst_sound_laser = ["laser1.ogg", "laser2.ogg",
                   "laser3.ogg", "laser4.ogg", "laser5.ogg"]
laser_droid_sound = load_sound(
    random.choice(lst_sound_laser), 0.3)
laser_player_sound = load_sound('laser_player.ogg', 0.3)

explosion_player = load_sound("explosion3.ogg", 0.3)
explosion_droid = load_sound("explosion1.ogg", 0.3)
explosion_asteroid = load_sound("destroyed_asteroid.ogg", 0.3)
collision_asteroid = load_sound("collision_asteroid.ogg", 0.3)

motor_channel = pygame.mixer.Channel(4)
music_channel = pygame.mixer.Channel(3)
music_channel.play(intro_sound, loops=-1, maxtime=0, fade_ms=0)

# Configuramos la imagen de fondo
background = load_image(
    path.join('data', 'images', 'background', 'background_1.jpg'), True, DISPLAYMODE)

window.blit(background, (0, 0))
