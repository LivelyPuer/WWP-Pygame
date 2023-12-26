import pygame
from pygame import Color

import config
from map import game_map
from resources import load_image


class Object(pygame.sprite.Sprite):
    can_control = False
    is_visible = False
    image = load_image("default.png")

    def __init__(self, x, y, *group, sprite="default.png", pilot=(0, 0), can_control=False):
        super().__init__(*group)
        self.image = load_image(sprite)
        self.pilot = pilot
        self.rect = self.image.get_rect()
        self.rect.x = x - self.image.get_width() * pilot[0]
        self.rect.y = y - self.image.get_height() * pilot[1]
        self.can_control = can_control

    def moveto(self, x, y):
        self.rect.x = x - self.image.get_width() * self.pilot[0]
        self.rect.y = y - self.image.get_height() * self.pilot[1]

    def simple_move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        pass

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)


class GravityObject(Object):
    def __init__(self, x, y, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite)
        self.falling_speed = 0

    def update(self):
        self.falling()

    def falling(self):
        if not self.on_ground():
            self.falling_speed -= config.gravity / config.fps
        else:
            self.falling_speed = 0
        if game_map.check_in_ground(self.rect):
            self.falling_speed = -1
        self.simple_move(0, self.falling_speed)

    def physics_move(self, dx, dy):
        if dx > 0 and game_map.can_move_right(self.rect) or dx < 0 and game_map.can_move_left(self.rect):
            self.rect.x += dx
            if game_map.check_ground_top(self.rect):
                self.rect.x -= dx
        self.rect.y += dy


    def on_ground(self) -> bool:
        return game_map.check_on_ground(self.rect)


class Worm(Object):
    pass


class Team:
    team = []
    color = Color(255, 0, 0)

    def __init__(self, team):
        self.team = team
