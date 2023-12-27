import pygame
from pygame import Color

import config
from map import game_map
from resources import load_image


class Object(pygame.sprite.Sprite):
    can_control = False
    is_visible = False
    image = load_image("default.png")
    float_position = [0, 0]

    def __init__(self, x, y, *group, sprite="default.png", pilot=(0, 0), can_control=False):
        super().__init__(*group)
        self.image = load_image(sprite)
        self.pilot = pilot
        self.rect = self.image.get_rect()
        self.float_position[0] = x - self.image.get_width() * pilot[0]
        self.float_position[1] = y - self.image.get_height() * pilot[1]
        self.can_control = can_control
        self.update_rect()

    def moveto(self, x, y):
        self.float_position[0] = x - self.image.get_width() * self.pilot[0]
        self.float_position[1] = y - self.image.get_height() * self.pilot[1]

    def simple_move(self, dx, dy):
        self.float_position[0] += dx
        self.float_position[1] += dy

    def update(self):
        self.update_rect()

    def update_rect(self):
        self.rect.x = round(self.float_position[0])
        self.rect.y = round(self.float_position[1])

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)


class GravityObject(Object):
    falling_speed = 0

    def __init__(self, x, y, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite)

    def update(self):
        super().update()
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
            self.float_position[0] += dx
            if game_map.check_ground_top(self.rect):
                self.float_position[0] -= dx
        self.float_position[1] += dy

    def on_ground(self) -> bool:
        return game_map.check_on_ground(self.rect)


class Worm(GravityObject):
    is_jump = False
    forward_jumping = False
    back_jumping = False
    direction = 1  # -1 - left, 1 - right
    jump_force = 2
    back_jump_force = 5

    def __init__(self, x, y, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite)

    def jump(self):
        if self.on_ground():
            self.falling_speed = -self.jump_force
            self.is_jump = True
            self.forward_jumping = True

    def back_jump(self):
        if self.on_ground():
            self.falling_speed = -self.back_jump_force
            self.is_jump = True
            self.back_jumping = True

    def falling(self):
        if not self.on_ground():
            self.falling_speed -= config.gravity / config.fps
        elif not self.is_jump and self.on_ground():
            self.falling_speed = 0

        if self.falling_speed < 0 and game_map.check_ground_top(self.rect):
            self.falling_speed = 0

        if self.falling_speed == 0:
            self.back_jumping = False
            self.forward_jumping = False

        if game_map.check_in_ground(self.rect):
            self.falling_speed = -1
        self.simple_move(0, self.falling_speed)
        self.is_jump = False

    def update(self):
        super().update()
        if self.forward_jumping:
            self.physics_move(self.direction * 2, 0, jump=True)
        print(self.direction, self.forward_jumping, self.back_jumping, self.is_jump)

    def physics_move(self, dx, dy, jump=False):
        if not self.back_jumping and not self.forward_jumping:
            self.direction = 1 if dx > 0 else -1

        if self.back_jumping:
            if dx > 0 and self.direction == 1 or dx < 0 and self.direction == -1:
                super().physics_move(dx * 0.1, dy)
                pass
            else:
                super().physics_move(dx * 0.5, dy)
        elif jump and self.forward_jumping or not jump and not self.forward_jumping:
            super().physics_move(dx, dy)



class Team:
    team = []
    color = Color(255, 0, 0)

    def __init__(self, team):
        self.team = team
