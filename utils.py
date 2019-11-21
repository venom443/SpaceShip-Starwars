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
import pygame


def load_image(path, use_transparency=False, rect_img=(0, 0)):
    width, height = rect_img

    # Loading image
    try:
        image = pygame.image.load(path)
    except (pygame.error):
        print("Could not load the image: ", path)
        raise (SystemExit)

    # Verify if we add transparency
    if use_transparency:
        image = image.convert()
    else:
        image = image.convert_alpha()

    # Scale the image to the specified size, if required
    if width >= 1 and height >= 1:
        image = scale_image(image, (width, height))
    else:  # There will be no changes, it will keep its original size
        pass

    return image


def scale_image(image, size_required):
    scaled_img = pygame.transform.scale(image, size_required)
    return scaled_img


def load_sound(filename, sound_lvl=1.0):
    class WithoutSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return WithoutSound()

    path = os.path.join('data', 'sounds', filename)
    try:
        sound = pygame.mixer.Sound(path)
    except (pygame.error):
        print("Could not load the sound: ", path)
        raise (SystemExit)
    sound.set_volume(sound_lvl)  # Setting the sound volume
    return sound
