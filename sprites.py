#!/usr/bin/python3
# -*- coding: UTF-8 -*-

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
        # Desplazamiento de la nave en las direcciones especificadas
        self.rect.move_ip((self.x_speed, self.y_speed))
        if self.rect.left < 0:  # Preguntamos que no sobrepase los lados
            self.rect.left = 0
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

        if self.rect.top <= WINDOW_HEIGHT / 2:  # Preguntamos para que no sobrepase la mitad de la pantalla
            self.rect.top = WINDOW_HEIGHT / 2
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        # Determinamos la dirección del movimiento
        if self.x_speed < 0:  # Izquierda
            if self.y_speed < 0:  # Mover adelante a la izquierda
                self.image = self.images[5]
                motor_channel.play(motor_on_sound, loops=0,
                                 maxtime=0, fade_ms=0)
            else:  # Izquierda solamente
                self.image = self.images[4]
                motor_channel.stop()
        elif self.x_speed > 0:  # Derecha
            if self.y_speed < 0:  # Mover adelante a la derecha
                self.image = self.images[3]
                motor_channel.play(motor_on_sound, loops=0,
                                 maxtime=0, fade_ms=0)
            else:  # Derecha solamente
                self.image = self.images[2]
                motor_channel.stop()
        else:  # Moviéndose arriba/abajo
            # Arriba(acordarse que en el eje Y un número negativo indica ir arriba)
            if self.y_speed < 0:
                self.image = self.images[1]
                motor_channel.play(motor_on_sound, loops=0,
                                 maxtime=0, fade_ms=0)
            else:  # Abajo
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
        # Posicionamiento azar
        self.rect.centerx = random.randint(48, 752)
        self.rect.centery = random.randint(70, 230)
        self.x_speed = random.randint(-5, 5)
        self.y_speed = random.randint(-5, 5)
        # En caso que dé 0 le asignamos 1
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

        # Esto es para evitar que esté disparando todo el tiempo
        # disparar = True si el número aleatorio es 1
        is_shoot = random.randint(1, 80) == 1
        if is_shoot == True: # El droide dispara sólo si se le permite
            group_laser_enemy.add(LaserEnemy(self.rect.midbottom))
            laser_droid_sound.play()


# ------------------------------------------------------------------------------
#   ASTEROID sprite
# ------------------------------------------------------------------------------
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Para establecer un tamano variable de asteroides
        self.size_asteroid = random.randint(
            ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        # Para determinar al azar si el actual asteroide provee energia
        self.is_energetic = (random.random() < PROB_ENERGETIC_ASTEROID)
        self.energy_lvl = 0  # Nivel de energía que proveerá el asteroide. 0 es sin energía
        if self.is_energetic:
            self.image = self.select_image(
                os.path.join("resources", "energetic_asteroid.png"))
            # Para determinar la cantidad de energía que entrega el asteroide dependiendo su tamaño
            if self.size_asteroid <= 10:
                self.energy_lvl = 3
            elif self.size_asteroid <= 20:
                self.energy_lvl = 5
            elif self.size_asteroid <= 30:
                self.energy_lvl = 7
            elif self.size_asteroid > 30:
                self.energy_lvl = 10
        else:  # Asteroid without energy
            self.image = self.select_image(os.path.join("resources", "asteroid.png"))
        
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

    def select_image(self, archivo, is_energia_img=False):
        path_img = os.path.join('data', 'images', archivo)
        if is_energia_img is True:  # Preguntamos si es para cambiar la imagen por el de energía
            image = load_image(path_img, False, (int(
                ASTEROID_MAX_SIZE/2), int(ASTEROID_MAX_SIZE/2)))
        else:  # Entonces es una imagen de un meteorito cualquiera
            image = load_image(
                path_img, False, (self.size_asteroid, self.size_asteroid))

        return image


# ------------------------------------------------------------------------------
#   LASER sprite
# ------------------------------------------------------------------------------
class PlayerLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(os.path.join('data', 'images', 'resources', 'laser1.png'), False)
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
        self.image = load_image(os.path.join('data', 'images', 'resources', 'laser3.png'), False)
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
        self.index = 0  # Para cambiar por cada imagen de la lista
        # Trata de generar numeros grandes y simular un retraso para pasar de una imagen a otra
        self.rate_image = 0
        self.cantidad_img = 6  # Cantidad de imagenes que contiene la animación
        self.lst_img_explosion = [] # Anima los sprites que componen la explosion

        # Cargamos las imagenes dependiendo del tipo que sea
        for i in range(0, self.cantidad_img):
            path_img = os.path.join('data', 'images', 'animation', type_explosion + str(i + 1) + '.png')
            self.lst_img_explosion.append(load_image(
                path_img, False, object_rect.size))

        self.image = self.lst_img_explosion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = object_rect.x
        self.rect.y = object_rect.y

    def update(self):
        # Actualizamos el valor para cambiar de imagen
        self.rate_image += 1
        # Cambiará de imagen cada 4 frames
        if self.rate_image >= DELAY_EXPLOSION:
            self.index += 1
            self.rate_image = 0
            # Mostramos cada imagen de la animación
            if self.index < len(self.lst_img_explosion):
                self.image = self.lst_img_explosion[self.index]
            else: # En otro caso eliminamos el objeto
                self.kill()


# ================================
# We create the Sprites and the groups
# ================================
# We configure the player
player = Player()
player_team = pygame.sprite.RenderUpdates(player)
group_laser_player = pygame.sprite.RenderUpdates()

# We configure the enemies
enemy_team = pygame.sprite.RenderUpdates()
# We add 3 enemies
for i in range(3):
    enemy_team.add(Enemy())
group_laser_enemy = pygame.sprite.RenderUpdates()

# We configure the asteroids
group_asteroids = pygame.sprite.RenderUpdates()
group_energy = pygame.sprite.RenderUpdates()

# We create an object to simulate the explosion.
group_explosion = pygame.sprite.RenderUpdates()
