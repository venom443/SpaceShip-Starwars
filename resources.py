#!/usr/bin/python3
# -*- coding: UTF-8 -*-

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
MAX_NUMBER_DROIDS = 15 # To limit the total amount of droids that can be generated without filling the screen.
ASTEROID_MIN_SIZE = 10
ASTEROID_MAX_SIZE = 40
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 8
DELAY_EXPLOSION = 5 # To simulate a delay in the explosion animation
ADDNEW_ASTEROID_RATE = 7
RATE_PLAYER_SPEED = 6
PROB_ENERGETIC_ASTEROID = 0.4 # Probability that determines if it's an energetic asteroid.

pygame.init()
window = pygame.display.set_mode(DISPLAYMODE)
font1 = pygame.font.SysFont("Liberation Serif", 24)
font2 = pygame.font.SysFont("Liberation Serif", 20)
font3 = pygame.font.SysFont("Arial", 20)
font4 = pygame.font.SysFont("Times New Roman", 36)
font5 = pygame.font.SysFont("Liberation Serif", 40) # Points

# Set up sounds
intro_sound = load_sound('intro.wav', 0.3)
background_sound = load_sound('game_music.wav', 1.0)
explosion_sound = load_sound('explosion1.wav', 0.3)
motor_on_sound = load_sound('motor_on.wav', 0.4)
pickup_sound = load_sound('pickup.wav', 0.3)
game_over_sound = load_sound('game_over.wav', 1.0)
game_lost_sound = load_sound('game_lost.wav', 1.0)
game_won_sound = load_sound('game_won.wav', 1.0)

# We randomly select any of these sounds for the enemy
lst_sound_laser = ["laser1.wav", "laser2.wav",
                   "laser3.wav", "laser4.wav", "laser5.wav"]
laser_droid_sound = load_sound(
    random.choice(lst_sound_laser), 0.3)
laser_player_sound = load_sound('laser_player.wav', 0.3)

explosion_player = load_sound("explosion3.wav", 0.3)
explosion_droid = load_sound("explosion1.wav", 0.3)
explosion_asteroid = load_sound("destroyed_asteroid.wav", 0.3)
collision_asteroid = load_sound("collision_asteroid.wav", 0.3)

motor_channel = pygame.mixer.Channel(4)
music_channel = pygame.mixer.Channel(3)
music_channel.play(intro_sound, loops=-1, maxtime=0, fade_ms=0)

# Configuramos la imagen de fondo
background = load_image(
    path.join('data', 'images', 'background', 'background.jpg'), True, DISPLAYMODE)

window.blit(background, (0, 0))
