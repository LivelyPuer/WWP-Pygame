import pygame
from pygame import Color

import config
from map import game_map, screen_bound
from resources import load_image


class Object(pygame.sprite.Sprite):
    can_control = False
    is_visible = False
    image = load_image("default.png")
    float_position = [0, 0]

    def in_bounds(self):
        return screen_bound.contains(self.rect)

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


class AnimatedObject(Object):
    hash_anim = {}
    state = "default"
    animation = {"default": ["default16x16.png"]}
    cur_duration = 0
    frame_duration = 30
    state_count = 0

    def __init__(self, x, y, *group, sprite="default.png", pilot=(0, 0), can_control=False):
        super().__init__(x, y, *group, sprite="default.png", pilot=(0, 0), can_control=False)

    def animate(self):
        pass

    def get_load_sprite(self, name):
        if name not in self.hash_anim.keys():
            self.hash_anim[name] = load_image(name)
        return self.hash_anim[name]

    def update(self):
        super().update()
        self.animate()


class GravityObject(Object):
    falling_speed = 0
    is_move = False

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
        if dx > 0 and game_map.can_move_right(self.rect) or dx < 0 and game_map.can_move_left(
                self.rect) and self.in_bounds():
            self.float_position[0] += dx
            self.update_rect()
            self.is_move = True
            if game_map.check_ground_top(self.rect):
                self.float_position[0] -= dx
                self.update_rect()

        self.float_position[1] += dy

    def on_ground(self) -> bool:
        return game_map.check_on_ground(self.rect)


class Worm(AnimatedObject, GravityObject):
    is_jump = False
    forward_jumping = False
    back_jumping = False
    direction = 1  # -1 - left, 1 - right
    jump_force = 2
    back_jump_force = 5
    state = "idle"
    animation = {"idle": ["animations/idle_walk1.png"],
                 "walk": ["animations/idle_walk1.png", "animations/walk2.png"],
                 "forward_jump": ["animations/forward_jump.png"],
                 "back_jump": ["animations/back_jump1.png", "animations/back_jump2.png",
                               "animations/back_jump3.png", "animations/back_jump4.png",
                               "animations/back_jump5.png"],
                 "deathing": ["animations/deathing1.png", "animations/deathing2.png"],
                 "falling": ["animations/falling.png"],
                 "attacking": ["animations/attacking.png"],
                 "rip": ["animations/rip1.png", "animations/rip2.png",
                         "animations/rip3.png", "animations/rip4.png"]}

    def __init__(self, x, y, *group, sprite=animation["idle"][0], **kwargs):
        super(GravityObject, self).__init__(x, y, *group, sprite=sprite, **kwargs)
        self.state = "idle"

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

    def animate(self):
        self.cur_duration -= 1
        if self.state == "back_jump" and abs(self.falling_speed) >= 1:
            self.cur_duration = 0
            self.state_count = 0
            self.flip_by_direction(self.animation[self.state][0], True)
        elif self.back_jumping and self.state != "back_jump":
            self.cur_duration = 0
            self.frame_duration = 10
            self.state_count = 0
            self.state = "back_jump"

        if self.state != "walk" and self.is_move and not self.forward_jumping and not self.back_jumping:
            self.cur_duration = 0
            self.frame_duration = 30
            self.state_count = 0
            self.state = "walk"
        elif self.state != "idle" and not self.is_move and not self.forward_jumping and not self.back_jumping:
            self.state = "idle"
            self.flip_by_direction(self.animation[self.state][0])
        elif self.forward_jumping:
            self.state = "forward_jump"
            self.flip_by_direction(self.animation[self.state][0], True)
        if self.state != "falling" and self.falling_speed > 3 and not self.forward_jumping and not self.back_jumping or \
                (self.state != "falling" and self.falling_speed > 5 and (self.forward_jumping or self.back_jumping)):
            self.state = "falling"
            self.flip_by_direction(self.animation[self.state][0], True)

        if self.cur_duration <= 0:
            self.state_count += 1
            if self.state == "walk":
                self.flip_by_direction(self.animation[self.state][self.state_count % 2])
            if self.state == "back_jump" and abs(self.falling_speed) < 1:
                self.flip_by_direction(self.animation[self.state][1 + self.state_count % 3])
            self.cur_duration = self.frame_duration

        self.image = pygame.transform.flip(self.image, True, False)

    def flip_by_direction(self, name, flip=False):
        if not flip:
            if self.direction == -1:
                self.image = pygame.transform.flip(self.get_load_sprite(name), True, False)
            else:
                self.image = self.get_load_sprite(name)
        else:
            if self.direction == 1:
                self.image = pygame.transform.flip(self.get_load_sprite(name), True, False)
            else:
                self.image = self.get_load_sprite(name)

    def update(self):
        super().update()
        self.animate()
        if self.forward_jumping:
            self.physics_move(self.direction * 2, 0, jump=True)
        self.is_move = False

    def physics_move(self, dx, dy, jump=False):
        if self.state == "falling" and not self.forward_jumping:
            return
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
        print(self.direction, self.back_jumping, self.forward_jumping)


class Team:
    team = []
    color = Color(255, 0, 0)

    def __init__(self, team):
        self.team = team
