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
import pygame
import random
import sys
import time
from pygame.locals import *
from utils import load_image
from sprites import *
from resources import *


# It will increase as we destroy droids until we reach the goal
count_destroyed_droids = 0


class Game(object):
    def __init__(self):
        super(Game, self).__init__()
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=4096)
        pygame.display.set_caption("Star Wars")
        self.set_fps = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        # We establish the images
        logo = load_image(path.join('data', 'images',
                                    'background', 'start_logo.png'))
        # Displays the start screen
        self.draw_text("Press a key for start", font1,
                       window, (WINDOW_WIDTH / 3), (WINDOW_HEIGHT / 3) + 100)
        window.blit(logo, (150, 100))
        pygame.display.update()

        self.wait_for_key_pressed()
        music_channel.stop()

    def run(self):
        global count_destroyed_droids
        top_score = 0

        while(True):
            initial_time = time.perf_counter()
            enemy_creation_period = 2
            energy = INIT_ENERGY
            count_destroyed_droids = 0 # Reset value
            points = 0
            asteroid_counter = 0
            
            # ====================================
            # We create the Sprites and the groups
            # ====================================
            # We configure the player
            player = Player()
            player_team = pygame.sprite.RenderUpdates(player)
            group_laser_player = pygame.sprite.RenderUpdates()
            
            # We configure the enemies
            enemy_team = pygame.sprite.RenderUpdates()
            # We add 3 enemies
            for i in range(3):
                enemy_team.add(Enemy())

            # We configure the asteroids
            group_asteroids = pygame.sprite.RenderUpdates()
            group_energy = pygame.sprite.RenderUpdates()

            # We create an object to simulate the explosion.
            group_explosion = pygame.sprite.RenderUpdates()
            # Configure the boxes that will contain text
            points_box = TextBox("Points: {}".format(points), font1, 10, 0)
            top_score_box = TextBox(
                "Best score: {}".format(top_score), font1, 10, 40)
            objectives_box = TextBox(
                "Objective: {}".format(OBJECTIVE_LVL - count_destroyed_droids), font1, 10, 80)
            time_box = TextBox("Time: {0:.2f}".format(
                initial_time), font1, WINDOW_WIDTH - 150, 0)
            energy_box = TextBox("Energy: {}".format(
                energy), font1, WINDOW_WIDTH - 150, 40)
            info_box = TextBox(
                "Press: ESC-Exit     F1-Help     F2-About...", font1, 10, WINDOW_HEIGHT - 40)
            group_box = pygame.sprite.RenderUpdates(
                points_box, top_score_box, objectives_box, time_box, energy_box, info_box)

            music_channel.play(background_sound, loops=-1, maxtime=0, fade_ms=0)
            loop_counter = 0
            press_keys = True
            
            while (True):
                # Draw background
                window.blit(background, (0, 0))

                # In case the player loses, he is not allowed to use keys.
                if press_keys == True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            self.exit_game()
                        elif event.type == KEYDOWN:  # We ask if a key has been pressed
                            if event.key == K_F1:
                                self.show_help()
                            if event.key == K_F2:
                                self.show_about()
                            if event.key == K_p:
                                self.pause_game()
                            if event.key == K_ESCAPE:
                                self.exit_game()
                            if event.key == K_SPACE:
                                laser_player_sound.play()
                                group_laser_player.add(
                                    PlayerLaser(player.rect.midtop))
                        elif event.type == KEYUP:  # We ask if you have stopped pressing any key
                            player.x_speed, player.y_speed = (0, 0)

                    # Basic controls for driving the spaceship
                    key_pressed = pygame.key.get_pressed()
                    if key_pressed[K_a] or key_pressed[K_LEFT]:
                        player.x_speed = -(RATE_PLAYER_SPEED)
                    if key_pressed[K_d] or key_pressed[K_RIGHT]:
                        player.x_speed = RATE_PLAYER_SPEED
                    if key_pressed[K_w] or key_pressed[K_UP]:
                        player.y_speed = -(RATE_PLAYER_SPEED)
                    if key_pressed[K_s] or key_pressed[K_DOWN]:
                        player.y_speed = RATE_PLAYER_SPEED
                else:  # In case we run out of power.
                    # 6 is the number of images of the animation * the DELAY + 20 more cycles to have a moment of pause
                    total_loops = (DELAY_EXPLOSION * 6) + 20
                    if loop_counter == total_loops:
                        break

                    loop_counter = loop_counter + 1

                # Put more asteroids at the top of the screen, if necessary.
                asteroid_counter += 1
                if asteroid_counter == ADDNEW_ASTEROID_RATE:
                    asteroid_counter = 0
                    group_asteroids.add(Asteroid())

                # Creating droids
                # It is not to overload droids on the screen.
                enemy_creation_period += 2
                if (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period >= 450:
                    enemy_team.add(Enemy())
                    enemy_creation_period = 0
                elif (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period == 210:
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())
                elif (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period == 50:
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())

                # To determine the elapsed time
                current_time = time.perf_counter()
                elapsed_time = current_time - initial_time
                elapsed_time = elapsed_time * 2

                # Death of the character. We control that it is carried out 1 time
                if energy <= 0 and press_keys == True:
                    if points > top_score:
                        top_score = points
                    explosion_player.play()
                    press_keys = False  # To disabled pulse input
                    group_explosion.add(Explosion(player.rect))
                    player.kill()
                    loop_counter = 0
                # Player wins
                elif count_destroyed_droids >= OBJECTIVE_LVL:
                    if points > top_score:
                        top_score = points
                    press_keys = False  # To disabled pulse input
                    player.kill()
                    loop_counter = 0
                    break

                # -----------------------------------------------------------------------------------------
                # COLLISIONS OF SPRITES
                # =========================
                # Collision with enemy laser and player
                for player in pygame.sprite.groupcollide(player_team, group_laser_enemy, False, True):
                    energy = energy - 5
                # Collision with laser and enemy
                for droid in pygame.sprite.groupcollide(enemy_team, group_laser_player, True, True):
                    points += 15
                    group_explosion.add(Explosion(droid.rect, "explosion"))
                    explosion_droid.play()
                    count_destroyed_droids += 1
                # Collision with laser and asteroids
                for asteroid in pygame.sprite.groupcollide(group_asteroids, group_laser_player, False, True):
                    points += 5
                    group_explosion.add(Explosion(asteroid.rect, "smoke"))
                    explosion_asteroid.play()
                    # We ask if it's an asteroid that provides energy to change the image.
                    if (asteroid.is_energetic):
                        asteroid.image = asteroid.select_image(
                            path.join('resources', 'energy.png'), True)
                        asteroid.x_speed = 0  # To make it fall vertically
                        asteroid.y_speed = 2  # To slow down
                        group_energy.add(asteroid)
                        group_asteroids.remove(asteroid)
                    else:
                        asteroid.kill()
                # Collision with asteroid and player
                for asteroid in pygame.sprite.groupcollide(group_asteroids, player_team, True, False):
                    energy = energy - 7  # Decreases the ship's energy
                    group_explosion.add(Explosion(asteroid.rect, "smoke"))
                    collision_asteroid.play()
                # Collision with enemy and player
                for droid in pygame.sprite.groupcollide(enemy_team, player_team, True, False):
                    energy = energy - 7
                    group_explosion.add(Explosion(droid.rect, "explosion"))
                    explosion_droid.play()
                # Collision with energy and player
                for e in pygame.sprite.groupcollide(group_energy, player_team, True, False):
                    if energy < 100:
                        # Provides energy depending on asteroid
                        energy = energy + e.energy_lvl
                        if energy >= 100:
                            energy = 100

                    pickup_sound.play()
                # -----------------------------------------------------------------------------------------
                # Update all groups
                # =============================
                player_team.update()
                group_laser_player.update()
                enemy_team.update()
                group_laser_enemy.update()
                group_asteroids.update()
                group_energy.update()
                group_box.update()
                group_explosion.update()

                # -----------------------------------------------------------------------------------------
                # REDRAW SPRITES
                # =======================
                player_team.clear(window, background)
                group_laser_player.clear(window, background)
                enemy_team.clear(window, background)
                group_laser_enemy.clear(window, background)
                group_asteroids.clear(window, background)
                group_energy.clear(window, background)
                group_box.clear(window, background)
                group_explosion.clear(window, background)
                player_team.draw(window)
                group_laser_player.draw(window)
                enemy_team.draw(window)
                group_laser_enemy.draw(window)
                group_asteroids.draw(window)
                group_energy.draw(window)
                group_box.draw(window)
                group_explosion.draw(window)

                points_box.text = "Points: {}".format(points)
                top_score_box.text = "Best score: {}".format(top_score)
                objectives_box.text = "Objective: {}".format(OBJECTIVE_LVL - count_destroyed_droids)
                time_box.text = "Time: %.2f" % (elapsed_time)
                energy_box.text = "Energy: {0}%".format(int(energy))
                info_box.text = "Press: ESC-Exit     F1-Help     F2-About..."

                # Show the energy bar
                self.show_energy_bar(energy)

                pygame.display.update()
                self.set_fps.tick(FPS)

            # -----------------------------------
            # Stops the game and prints the score
            # ===================================
            self.print_score(points)
            time_lapse = 3000  # 3 sec
            pygame.time.delay(time_lapse)
            self.wait_for_key_pressed()
            music_channel.stop()

    def draw_text(self, text, font, surface, x, y):
        text_obj = font.render(text, True, TEXTCOLOR)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(font.render(text, True, TEXTCOLOR), text_rect)

    def show_energy_bar(self, energy):
        # Draw a colored vertical energy bar. Red tones for low energy and green tones for high energy.
        red_lvl = 255 - ((energy * 2) + 55)
        if red_lvl < 0:
            red_lvl = 0
        elif red_lvl > 255:
            red_lvl = 255

        green_lvl = ((energy * 2) + 55)
        if green_lvl < 0:
            green_lvl = 0
        elif green_lvl > 255:
            green_lvl = 255

        color_rgb = (red_lvl, green_lvl, 0)
        pygame.draw.rect(window, color_rgb,
                         (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30, 20, -1 * energy))

    def show_help(self):
        # Let's update the screen
        window.blit(background, (0, 0))
        pygame.display.update()

        # PLAYER AND DROIDS
        # =================
        size_image = 50
        # Player
        image = load_image(path.join('data', 'images', 'spaceship', 'ship_center_motor_on.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.5 - 25, WINDOW_HEIGHT * 0.75))
        # Droid
        image = load_image(path.join('data', 'images', 'resources', 'droid.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.78 - 25, WINDOW_HEIGHT * 0.16))
        # LASERS
        # ======
        # Player laser
        width_laser = 3
        height_laser = 30
        image = load_image(path.join('data', 'images', 'resources', 'laser1.png'),
                           False, (width_laser, height_laser))
        window.blit(image, (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5))
        # Enemy laser
        image = load_image(path.join('data', 'images', 'resources', 'laser3.png'),
                           False, (width_laser, height_laser))
        window.blit(image, (WINDOW_WIDTH * 0.78, WINDOW_HEIGHT * 0.25))
        # ASTEROIDS AND ENERGY
        # ====================
        # Asteroids
        size_image = 45
        image = load_image(path.join('data', 'images', 'resources', 'asteroid.png'),
                           False, (size_image, size_image - 5))
        window.blit(image, (WINDOW_WIDTH * 0.3, WINDOW_HEIGHT * 0.16))
        # Energetic asteroid
        image = load_image(path.join('data', 'images', 'resources', 'energetic_asteroid.png'),
                           False, (size_image, size_image - 5))
        window.blit(image, (WINDOW_WIDTH * 0.1, WINDOW_HEIGHT * 0.16))
        # Energy
        size_image = 30
        image = load_image(path.join('data', 'images', 'resources', 'energy.png'),
                           False, (size_image, size_image - 5))
        window.blit(image, (WINDOW_WIDTH * 0.2, WINDOW_HEIGHT * 0.5))
        # KEYS
        size_image = 32
        image = load_image(path.join('data', 'images', 'resources', 'K_w.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.48, WINDOW_HEIGHT * 0.66))
        image = load_image(path.join('data', 'images', 'resources', 'K_a.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.4, WINDOW_HEIGHT * 0.78))
        image = load_image(path.join('data', 'images', 'resources', 'K_s.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.48, WINDOW_HEIGHT * 0.87))
        image = load_image(path.join('data', 'images', 'resources', 'K_d.png'),
                           False, (size_image, size_image))
        window.blit(image, (WINDOW_WIDTH * 0.57, WINDOW_HEIGHT * 0.78))
        width_img = 128
        height_img = 28
        image = load_image(path.join('data', 'images', 'resources', 'K_SPACE.png'),
                           False, (width_img, height_img))
        window.blit(image, (WINDOW_WIDTH * 0.42, WINDOW_HEIGHT * 0.96))

        # COMMENTS
        # ========
        # Asteroids
        text1 = "Asteroids"
        text2 = "Destroy them and you'll earn points."
        text3 = "If you get hit, you lose energy."
        self.draw_text(text1, font3, window, WINDOW_WIDTH * 0.2, WINDOW_HEIGHT * 0.06)
        self.draw_text(text2, font2, window, WINDOW_WIDTH * 0.1, WINDOW_HEIGHT * 0.09)
        self.draw_text(text3, font2, window, WINDOW_WIDTH * 0.1, WINDOW_HEIGHT * 0.11)
        text1 = "Energetic asteroids release"
        text2 = "energy. Capture them!"
        self.draw_text(text1, font6, window, WINDOW_WIDTH * 0.02, WINDOW_HEIGHT * 0.25)
        self.draw_text(text2, font6, window, WINDOW_WIDTH * 0.04, WINDOW_HEIGHT * 0.28)
        
        # Energy
        text1 = "Energy"
        text2 = "Recovers energy. Capture them!"
        self.draw_text(text1, font3, window, WINDOW_WIDTH * 0.18, WINDOW_HEIGHT * 0.45)
        self.draw_text(text2, font2, window, WINDOW_WIDTH * 0.08, WINDOW_HEIGHT * 0.55)

        # Droid
        text1 = "Droid"
        text2 = "Destroy them and you'll earn points."
        self.draw_text(text1, font3, window, WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.06)
        self.draw_text(text2, font2, window, WINDOW_WIDTH * 0.6, WINDOW_HEIGHT * 0.09)
        text1 = "Avoid lasers or you'll lose energy."
        self.draw_text(text1, font6, window, WINDOW_WIDTH * 0.65, WINDOW_HEIGHT * 0.3)

        # Keys
        self.draw_text("Move up", font6, window, WINDOW_WIDTH * 0.46, WINDOW_HEIGHT * 0.63)
        self.draw_text("Move to the left", font6, window, WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.795)
        self.draw_text("Move to the right", font6, window, WINDOW_WIDTH * 0.62, WINDOW_HEIGHT * 0.795)
        self.draw_text("Move down", font6, window, WINDOW_WIDTH * 0.45, WINDOW_HEIGHT * 0.93)
        self.draw_text("Fire!", font6, window, WINDOW_WIDTH * 0.60, WINDOW_HEIGHT * 0.97)

        pygame.display.update()
        # We won't get out of the loop until we press a key.
        self.wait_for_key_pressed()

    def show_about(self):
        """
        It will pause the game and display information about developers, version, etc.
        """
        window.blit(background, (0, 0))
        pygame.display.update()

        # Logo
        size_image = 96
        image = load_image(path.join('data', 'images', 'spaceship', 'ship_center_motor_on.png'),
                           False, (size_image, size_image))
        window.blit(image, ((WINDOW_WIDTH / 2) - 25, (WINDOW_HEIGHT / 4)))

        # Title
        version = "0.1.0"
        self.draw_text("Star Wars " + version, font4,
                       window, (WINDOW_WIDTH / 2) - 100, (WINDOW_HEIGHT / 2))

        # Description
        self.draw_text('Space shooter game inspired by the Star Wars movie',
                       font2, window, (WINDOW_WIDTH / 3) - 100, (WINDOW_HEIGHT / 2) + 50)

        # Copyright
        dev_year = "2018"
        current_year = time.strftime("%Y")
        if dev_year == current_year:
            time_lapse = dev_year
        else:
            time_lapse = dev_year + " - " + current_year
        self.draw_text("Copyright © " + time_lapse, font2, window, 
                       WINDOW_WIDTH / 3 - 100, WINDOW_HEIGHT / 2 + 90)

        # Developers
        self.draw_text("Developers:", font2, window,
                       WINDOW_WIDTH / 3 - 100, WINDOW_HEIGHT / 2 + 130)
        self.draw_text("   ■ Andrés Segovia<Andy-thor>:", font3, window,
                       WINDOW_WIDTH / 3 - 100, WINDOW_HEIGHT / 2 + 155)

        self.draw_text('Press a key to play again', font3, 
                        window, WINDOW_WIDTH * 0.38, WINDOW_HEIGHT - 50)

        pygame.display.update()
        # We won't get out of the loop until we press a key.
        self.wait_for_key_pressed()

    def print_score(self, points):
        if count_destroyed_droids >= OBJECTIVE_LVL:
            msg = "You have won!"
            sound = game_won_sound
        else:
            msg = "You have lost!"
            sound = game_lost_sound
        # Prints obtained score
        self.draw_text(str(points), font5, window,
                       WINDOW_WIDTH * 0.5, WINDOW_HEIGHT / 2 - 50)
        # Prints custom message
        self.draw_text(msg, font1, window,
                       WINDOW_WIDTH * 0.42, WINDOW_HEIGHT / 2)

        self.draw_text('Press a key to play again', font3, 
                        window, WINDOW_WIDTH * 0.38, WINDOW_HEIGHT - 50)

        pygame.display.update()
        music_channel.play(sound, loops=0, maxtime=0, fade_ms=0)

    def wait_for_key_pressed(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_game()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # When we press the "esc" key we're out of the game
                        self.exit_game()
                    # When we press any key we leave the loop and the game continues.
                    return

    def pause_game(self):
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_game()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.exit_game()
                    if event.key == K_p:
                        paused = False
            self.draw_text("PAUSE", font5, window,
                           (WINDOW_WIDTH / 2)-50, (WINDOW_HEIGHT / 2))
            pygame.display.update()

    def exit_game(self):
        pygame.quit()
        sys.exit()
