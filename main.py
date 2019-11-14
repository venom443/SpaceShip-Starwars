#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from game import Game

class StarWars(Game):
    def __init__(self):
        super(StarWars, self).__init__()

def main():
    game = StarWars()
    game.run()

if __name__ == '__main__':
    main()
