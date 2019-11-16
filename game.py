#!/usr/bin/python3
# -*- coding: UTF-8 -*-

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
count_droids_destroyed = 0


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
        global count_droids_destroyed
        top_score = 0

        while(True):
            initial_time = time.perf_counter()
            enemy_creation_period = 2
            energy = INIT_ENERGY
            count_droids_destroyed = 0 # Reset value
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
                "Objective: {}".format(OBJECTIVE_LVL - count_droids_destroyed), font1, 10, 80)
            time_box = TextBox("Time: {0:.2f}".format(
                initial_time), font1, WINDOW_WIDTH - 150, 0)
            energy_box = TextBox("Energy: {}".format(
                energy), font1, WINDOW_WIDTH - 150, 40)
            info_box = TextBox(
                "Press: ESC-Exit     F1-Help     F2-About...", font1, 10, WINDOW_HEIGHT - 40)
            group_box = pygame.sprite.RenderUpdates(
                points_box, top_score_box, objectives_box, time_box, energy_box, info_box)

            music_channel.play(background_sound, loops=-
                               1, maxtime=0, fade_ms=0)
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
                elif count_droids_destroyed >= OBJECTIVE_LVL:
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
                    count_droids_destroyed += 1
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
                objectives_box.text = "Objective: {}".format(OBJECTIVE_LVL - count_droids_destroyed)
                time_box.text = "Time: %.2f" % (elapsed_time)
                energy_box.text = "Energy: {0}%".format(int(energy))
                info_box.text = "Press: ESC-Exit     F1-Help     F2-About..."

                # Show the energy bar
                self.show_energy_bar(energy)

                pygame.display.update()
                self.set_fps.tick(FPS)

            # Stops the game and displays the Game Over screen
            self.draw_text('GAME OVER', font1, window,
                           (WINDOW_WIDTH / 2) - 50, (WINDOW_HEIGHT / 3))
            pygame.display.update()
            time_lapse = 2000  # 2 sec
            pygame.time.delay(time_lapse)
            music_channel.stop()

            # Print the punctuation
            self.print_score(points)
            time_lapse = 4000  # 4 sec
            pygame.time.delay(time_lapse)
            self.wait_for_key_pressed()
            music_channel.stop()

    def draw_text(self, texto, fuente, surface, x, y):
        text_obj = fuente.render(texto, True, TEXTCOLOR)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(fuente.render(texto, True, TEXTCOLOR), text_rect)

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
        img_help = load_image(
            path.join('data', 'images', 'background', 'help.jpg'), True, DISPLAYMODE)
        window.blit(img_help, (0, 0))  # Image to cover the background
        pygame.display.update()

        self.draw_text('Press a key to play again',
                       font1, window, (WINDOW_WIDTH / 3), WINDOW_HEIGHT - 20)

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
        version = "0.0.2"
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
        self.draw_text("Copyright © " + time_lapse, font2,
                       window, (WINDOW_WIDTH / 3) - 100, (WINDOW_HEIGHT / 2) + 90)

        # Developers
        self.draw_text("Developers:", font2, window,
                       (WINDOW_WIDTH / 3) - 100, (WINDOW_HEIGHT / 2) + 130)
        self.draw_text("   ■ Andrés Segovia<Andy-thor>:", font3, window,
                       (WINDOW_WIDTH / 3) - 100, (WINDOW_HEIGHT / 2) + 155)

        self.draw_text('Press a key to play again',
                       font1, window, (WINDOW_WIDTH / 3) - 100, WINDOW_HEIGHT - 50)

        pygame.display.update()
        # We won't get out of the loop until we press a key.
        self.wait_for_key_pressed()

    def print_score(self, points):
        if count_droids_destroyed >= OBJECTIVE_LVL:
            image = load_image(
                path.join('data', 'images', 'background', 'game_won.jpg'), True, DISPLAYMODE)
            sound = game_won_sound
        else:
            image = load_image(
                path.join('data', 'images', 'background', 'game_lost.jpg'), True, DISPLAYMODE)
            sound = game_lost_sound
        window.blit(image, (0, 0))
        music_channel.play(sound, loops=0, maxtime=0, fade_ms=0)

        pygame.display.update()
        self.draw_text(str(points), font5, window,
                       (WINDOW_WIDTH / 2)-20, (WINDOW_HEIGHT / 2)-20)
        pygame.display.update()

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
        pausado = True
        while pausado:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_game()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.exit_game()
                    if event.key == K_p:
                        pausado = False
            self.draw_text("PAUSE", font5, window,
                           (WINDOW_WIDTH / 2)-50, (WINDOW_HEIGHT / 2))
            pygame.display.update()

    def exit_game(self):
        pygame.quit()
        sys.exit()
