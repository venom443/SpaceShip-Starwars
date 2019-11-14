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


OBJECTIVE_LVL = 100 # Destroy 100 enemies


class Game(object):
    def __init__(self):
        super(Game, self).__init__()
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=4096)
        pygame.display.set_caption("Star Wars")
        self.set_fps = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        # Establecemos las imágenes
        logo = load_image(path.join('data', 'images', 'background', 'start_logo.png'))

        # Muestra la pantalla de bienvenida
        self.draw_text("Press a key for start", font1,
                            window, (WINDOW_WIDTH / 3), (WINDOW_HEIGHT / 3) + 100)
        window.blit(logo, (150, 100))
        pygame.display.update()
        
        self.wait_for_key_pressed()
        music_channel.stop()

    def run(self):
        global OBJECTIVE_LVL
        global player
        top_score = 0

        while(True):
            if not time.clock():
                initial_time = time.perf_counter()
            else:
                initial_time = time.clock()

            enemy_creation_period = 2
            energy = INIT_ENERGY
            points = 0
            asteroid_counter = 0

            # Configuramos las cajas que contendrán texto
            points_box = TextBox("Points: {}".format(points), font1, 10, 0)
            top_score_box = TextBox("Best score: {}".format(top_score), font1, 10, 40)
            objectives_box = TextBox("Objective: {}".format(OBJECTIVE_LVL), font1, 10, 80)
            time_box = TextBox("Time: {0:.2f}".format(initial_time), font1, WINDOW_WIDTH - 150, 0)
            energy_box = TextBox("Energy: {}".format(energy), font1, WINDOW_WIDTH - 150, 40)
            info_box = TextBox("Press: ESC-Exit     F1-Help     F2-About...", font1, 10, WINDOW_HEIGHT - 40)
            group_box = pygame.sprite.RenderUpdates(points_box, top_score_box, objectives_box, time_box, energy_box, info_box)

            music_channel.play(background_sound, loops=-1, maxtime=0, fade_ms=0)
            loop_counter = 0
            press_keys = True
            while (True):
                # Draw background
                window.blit(background, (0, 0))

                # En caso de que el jugador pierda no se le permite utilizar teclas
                if press_keys == True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            self.exit_game()
                        elif event.type == KEYDOWN:  # Preguntamos si se ha presionado una tecla
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
                        elif event.type == KEYUP:  # Preguntamos si se ha dejado de presionar cualquier tecla
                            player.x_speed, player.y_speed = 0, 0

                    # Sirve para mover a la nave del player por el espacio
                    # Con las teclas de navegación y letras.
                    key_pressed = pygame.key.get_pressed()
                    if key_pressed[K_a] or key_pressed[K_LEFT]:
                        player.x_speed = -(RATE_PLAYER_SPEED)
                    if key_pressed[K_d] or key_pressed[K_RIGHT]:
                        player.x_speed = RATE_PLAYER_SPEED
                    if key_pressed[K_w] or key_pressed[K_UP]:
                        player.y_speed = -(RATE_PLAYER_SPEED)
                    if key_pressed[K_s] or key_pressed[K_DOWN]:
                        player.y_speed = RATE_PLAYER_SPEED
                else:  # Entramos recién en el bloque luego de que la energía se agote
                    # 6 es la cantidad de imagenes de la animación * el RETRASO + 20 ciclos más para tener un momento de pausa
                    total_loops = (DELAY_EXPLOSION * 6) + 20
                    if loop_counter == total_loops:
                        break  # SALIMOS DEL CICLO WHILE

                    loop_counter = loop_counter + 1  # Aumentamos el contador

                # Pone mas asteroides en la parte alta de la pantalla, si son necesarios
                asteroid_counter += 1
                if asteroid_counter == ADDNEW_ASTEROID_RATE:
                    asteroid_counter = 0
                    group_asteroids.add(Asteroid())

                # Crear los droides enemigos
                # Sirve para agregar droides cada vez que su valor sea mayor o igual a 500
                # Luego se resetea. Es para no estar agregando droides de manera abusiva.
                enemy_creation_period += 2
                # Limitamos la cantidad maxima de droides que se crearan
                if (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period >= 450:
                    enemy_team.add(Enemy())
                    enemy_creation_period = 0
                # Limitamos la cantidad maxima de droides que se crearan
                elif (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period == 210:
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())
                # Limitamos la cantidad maxima de droides que se crearan
                elif (len(enemy_team)) <= MAX_NUMBER_DROIDS and enemy_creation_period == 50:
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())
                    enemy_team.add(Enemy())

                # Para contar el tiempo
                if not time.clock():
                    current_time = time.perf_counter()
                else:
                    current_time = time.clock()
                elapsed_time = current_time - initial_time
                elapsed_time = elapsed_time * 2

                # Muerte del personaje. Controlamos que se realice 1 vez
                if energy <= 0 and press_keys == True:
                    # Verificamos si supera el mejor puntaje
                    if points > top_score:
                        top_score = points
                    explosion_player.play()
                    press_keys = False  # Para deshabilitar el ingreso de pulsaciones
                    group_explosion.add(Explosion(player.rect))
                    player.kill()  # Matamos al personaje
                    loop_counter = 0
                # Gana el personaje
                elif OBJECTIVE_LVL <= 0:
                    # Verificamos si supera el mejor puntaje
                    if points > top_score:
                        top_score = points
                    press_keys = False  # Para deshabilitar el ingreso de pulsaciones
                    player.kill()
                    loop_counter = 0
                    break
                
                # -----------------------------------------------------------------------------------------
                # COLISIONES DE LOS SPRITES
                # =========================
                # Daño ocasionado por los láseres de los enemigos al player
                for player in pygame.sprite.groupcollide(player_team, group_laser_enemy, False, True):
                    energy = energy - 5
                # Para que el láser destruya la nave enemiga
                for droid in pygame.sprite.groupcollide(enemy_team, group_laser_player, True, True):
                    points += 15
                    group_explosion.add(Explosion(droid.rect, "explosion"))
                    explosion_droid.play()
                    OBJECTIVE_LVL -= 1
                # Para que el láser destruya los asteroides
                for asteroid in pygame.sprite.groupcollide(group_asteroids, group_laser_player, False, True):
                    points += 5
                    # En vez de una explosion el asteroide desaparece en una nube de humo
                    group_explosion.add(Explosion(asteroid.rect, "smoke"))
                    explosion_asteroid.play()
                    # Preguntamos si es un asteroide que provee energía para cambiar la imagen
                    if (asteroid.is_energetic is True):
                        asteroid.image = asteroid.select_image(
                            path.join('resources', 'energy.png'), True)
                        asteroid.x_speed = 0  # Para que caiga verticalmente
                        asteroid.y_speed = 2  # Para disminuir su velocidad
                        group_energy.add(asteroid)
                        group_asteroids.remove(asteroid)
                    else:  # Destruimos directamente al asteroide
                        asteroid.kill()
                # Cuando un asteroide choca a la nave
                for asteroid in pygame.sprite.groupcollide(group_asteroids, player_team, True, False):
                    energy = energy - 7  # Disminuye la energía que posee la nave
                    group_explosion.add(Explosion(asteroid.rect, "smoke"))
                    collision_asteroid.play()
                # Cuando un droide choca a la nave
                for droid in pygame.sprite.groupcollide(enemy_team, player_team, True, False):
                    energy = energy - 7  # Disminuyo la energía que posee la nave
                    group_explosion.add(Explosion(droid.rect, "explosion"))
                    explosion_droid.play()
                # Cuando tocamos la energía
                for e in pygame.sprite.groupcollide(group_energy, player_team, True, False):
                    if energy < 100:
                        # Proporciona energía dependiendo del asteroide
                        energy = energy + e.energy_lvl
                        # Trataremos de que no pase de los límites
                        if energy >= 100:
                            energy = 100

                    pickup_sound.play()
        # -----------------------------------------------------------------------------------------
                # Actualizamos todos los grupos
                # =============================
                player_team.update()
                group_laser_player.update()
                enemy_team.update()
                group_laser_enemy.update()
                group_asteroids.update()
                group_energy.update()
                group_box.update()
                group_explosion.update()

                # REDIBUJAMOS LOS SPRITES
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

                # Pone las puntuaciones y tiempos
                points_box.texto = "Points: {}".format(points)
                top_score_box.texto = "Best score: {}".format(top_score)
                objectives_box.texto = "Objective: {}".format(OBJECTIVE_LVL)
                # Para que lo muestre con 2 decimales
                time_box.texto = "Time: %.2f" % (elapsed_time)
                energy_box.texto = "Energy: {0}%".format(int(energy))
                info_box.texto = "Press: ESC-Exit     F1-Help     F2-About..."

                # Mostramos la barra de energía
                self.show_energy_bar(energy)

                pygame.display.update()
                self.set_fps.tick(FPS)

            # Detiene el juego y muestra la pantalla de Game Over
            self.draw_text('GAME OVER', font1, window, (WINDOW_WIDTH / 2) - 50, (WINDOW_HEIGHT / 3))
            pygame.display.update()
            time_lapse = 2000 # 2 sec
            pygame.time.delay(time_lapse)
            music_channel.stop()

            # Imprimimos el puntaje
            self.imprime_puntuacion(points)
            time_lapse = 4000 # 4 sec
            pygame.time.delay(time_lapse)
            self.wait_for_key_pressed()
            music_channel.stop()

    def draw_text(self, texto, fuente, surface, x, y):
        # Objeto temporal usado sólo para obtener luego el rectángulo(text_obj.get_rect())
        text_obj = fuente.render(texto, True, TEXTCOLOR)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(fuente.render(texto, True, TEXTCOLOR), text_rect)

    def show_energy_bar(self, energy):
        # Dibuja una barra de energy vertical coloreada. Tonos rojos para poca energia y verdes para energias altas
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
        img_help = load_image(path.join('data', 'images', 'background', 'help.jpg'), True, DISPLAYMODE)
        window.blit(img_help, (0, 0))  # Imagen para el tapar el fondo
        pygame.display.update()  # Pintamos toda la pantalla para borrar la imagen anterior

        # Mensaje de salida
        self.draw_text('Press a key to play again',
                        font1, window, (WINDOW_WIDTH / 3), WINDOW_HEIGHT - 20)

        pygame.display.update()
        # No saldremos del bucle hasta no presionar alguna tecla
        self.wait_for_key_pressed()

    def show_about(self):
        """
        Pausará el juego y mostrará información acerca de los desarrolladores, versi+on, etc.
        """
        window.blit(background, (0, 0))  # Imagen para el tapar el fondo
        pygame.display.update()  # Pintamos toda la pantalla para borrar la imagen anterior

        # La imágen
        size_image = 96  # Seleccionamos un tamaño grande
        image = load_image(path.join('data', 'images', 'spaceship', 'ship_center_motor_on.png'),
                               False, (size_image, size_image))
        window.blit(image, ((WINDOW_WIDTH / 2) - 25, (WINDOW_HEIGHT / 4)))

        # El título
        version = "0.0.1a"
        self.draw_text("Star Wars " + version, font4,
                            window, (WINDOW_WIDTH / 2) - 100, (WINDOW_HEIGHT / 2))

        # Descripción
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
        self.draw_text("   ■ Andrés Segovia:", font3, window,
                        (WINDOW_WIDTH / 3) - 100, (WINDOW_HEIGHT / 2) + 155)
        # Mensaje de salida
        self.draw_text('Press a key to play again',
                        font1, window, (WINDOW_WIDTH / 3) - 100, WINDOW_HEIGHT - 50)

        pygame.display.update()
        # No saldremos del bucle hasta no presionar alguna tecla
        self.wait_for_key_pressed()

    def imprime_puntuacion(self, points):
        if OBJECTIVE_LVL <= 0:
            image = load_image(path.join('data', 'images', 'background', 'game_won.jpg'), True, DISPLAYMODE)
            sound = game_won_sound
        else:
            image = load_image(path.join('data', 'images', 'background', 'game_lost.jpg'), True, DISPLAYMODE)
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
                    if event.key == K_ESCAPE: # Al pulsar la tecla esc salimos del juego
                        self.exit_game()
                    return  # Al presionar cualquier tecla salimos y comienza el juego

    def pause_game(self):
        pausado = True
        while pausado:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_game()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # Al pulsar la tecla esc salimos del juego
                        self.exit_game()
                    if event.key == K_p:
                        pausado = False
            self.draw_text("PAUSE", font5, window,
                                (WINDOW_WIDTH / 2)-50, (WINDOW_HEIGHT / 2))
            pygame.display.update()

    def exit_game(self):
        pygame.quit()
        sys.exit()
