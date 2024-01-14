import math

import numpy as np
import pygame

import config
from classes.base import Object, GravityObject
from map import game_map, screen_bound
from resources import load_image

tmp_group = pygame.sprite.Group()


class Bullet(GravityObject):
    def __init__(self, x, y, *group, sprite="default.png", radius=25, ground_contact=True, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.radius = radius
        self.weapon = None
        self.is_visible = True
        self.ground_contact = ground_contact
        self.source_image = load_image(sprite)
        self.active = False
        self.horizontal_speed = 5
        self.direction = 1

    def update(self):
        if self.is_visible:
            self.physics_move(self.horizontal_speed, 0)
            if self.ground_contact and self.check_ground_contact():
                self.explosion()
            self.angle_bullet()
            super().update()
        if not self.in_bounds():
            self.kill()
            del self

    def shoot(self, speed, angle, weapon=None):
        self.is_visible = True
        self.active = True
        self.falling_speed = -speed * math.sin(math.radians(angle))
        self.horizontal_speed = speed * math.cos(math.radians(angle))
        # print(self.falling_speed, self.horizontal_speed)

    def angle_bullet(self):
        vect = pygame.Vector2(self.horizontal_speed, self.falling_speed)
        self.image = pygame.transform.rotate(self.source_image,
                                             -np.sign(self.falling_speed) * math.degrees(math.acos(
                                                 (vect.x ** 2) / (math.sqrt(vect.x ** 2 + vect.y ** 2) * vect.x))))

    def explosion(self):
        print("Expolosion")
        game_map.remove_circle(*self.rect.center, self.radius)
        self.kill()
        del self


class RayCastBullet(Bullet):
    def __init__(self, x, y, *group, sprite="default.png", radius=25, ground_contact=True, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, radius=radius, ground_contact=ground_contact, kinematic=True,
                         **kwargs)

    def update(self):
        pass

    def shoot(self, speed, angle, weapon=None):
        self.is_visible = True
        self.active = True
        # self.nearest_point_m(*self.rect.topleft, angle)
        self.nearest_point_(*weapon.worm.rect.center, angle)
        # if coords:
        #     game_map.remove_circle(*coords, radius=self.radius)

    def nearest_point_(self, x0, y0, angle):
        x1, y1 = 0, 0
        # print(np.tan(np.radians(angle)))
        b = y0 - np.tan(np.radians(-angle)) * x0
        x_m = False
        if 270 >= angle > 90 or angle == -90:
            x1 = 0
            y1 = b
        elif -90 < angle < 90:
            x1 = config.map_width
            y1 = int(np.tan(np.radians(-angle)) * x1 + b)
            x_m = True
            print(angle, x0, y0, x1, y1)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        n = 1 + dx + dy
        x_inc = 1 if (x1 > x0) else -1
        y_inc = 1 if (y1 > y0) else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        while n > 0:
            if 0 < x < screen_bound.width and 0 < y < screen_bound.height:
                if game_map.check_block(x, y):
                    game_map.remove_circle(x, y, self.radius)
                    break
                if error > 0:
                    x += x_inc
                    error -= dy
                else:
                    y += y_inc
                    error += dx
            else:
                break

    def nearest_point_wiki(self, x0, y0, angle):
        x1, y1 = 0, 0
        # print(np.tan(np.radians(angle)))
        b = y0 + np.tan(np.radians(angle)) * x0
        if 270 > angle > 90:
            x1 = x0
            y1 = b
        elif -90 < angle < 90:
            x1 = config.map_width
            y1 = int(np.tan(np.radians(angle)) * x1)
        print(x0, y0, x1, y1)
        deltax = abs(x1 - x0)
        deltay = abs(y1 - y0)
        error, deltaerr = 0, (deltay + 1)
        y = y0
        diry = y1 - y0
        if diry > 0:
            diry -= 1
        if diry < 0:
            diry = -1
        for x in range(min(x0, x1), max(x0, x1)):

            if 0 < x < screen_bound.width and 0 < y < screen_bound.height:
                # game_map.remove_circle(x, y, 3)
                print(screen_bound.size, x, y)
                error = error + deltaerr
                if error >= (deltax + 1):
                    y = y + diry
                    error = error - (deltax + 1)
            else:
                print(screen_bound.size, x, y, 0 < x < screen_bound.width, 0 < y < screen_bound.height)
                break
        return None


class GrenadeBullet(Bullet):
    def __init__(self, x, y, *group, sprite="default.png", radius=25, ground_contact=False, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, radius=radius, ground_contact=ground_contact,
                         **kwargs)
        print(self.kinematic)

    def update(self):
        if game_map.check_on_ground_around(self.rect):
            game_map.get_tan_on_ground(self.rect)
            pass
            # print("grenade")
        super().update()


class Weapon(Object):
    def __init__(self, x, y, worm, bullet, *group, duration=True, sprite="default.png", pilot=(0, 0),
                 pilot_pixel=False, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, pilot=pilot, pilot_pixel=pilot_pixel)
        self.bullet = bullet
        self.source_image = load_image(sprite)
        self.worm = worm
        self.duration = duration
        self.worm.weapon = self

    def set_bullet(self, bullet):
        self.bullet = bullet
        self.moveto(self.worm.float_position.x + self.worm.weapon_pilot[0],
                    self.worm.float_position.y + self.worm.weapon_pilot[1])
        self.bullet.update_rect()

    def update(self):
        # print(self.worm.rect.x)
        self.moveto(self.worm.float_position.x + self.worm.weapon_pilot[0],
                    self.worm.float_position.y + self.worm.weapon_pilot[1])
        if self.worm.direction == 1:
            self.image = pygame.transform.rotate(self.source_image, angle=self.worm.angle)
        else:
            self.image = pygame.transform.flip(self.source_image, True, False)
            self.image = pygame.transform.rotate(self.image, angle=self.worm.direction * self.worm.angle)
        super().update()

    def shoot(self, speed):
        if self.worm.direction == 1:
            self.bullet.moveto(
                self.rect.x + self.image.get_width() * self.pilot[0] + ((self.image.get_width() / 2) + 2) * math.cos(
                    math.radians(self.worm.angle)),
                self.rect.y + self.image.get_height() * self.pilot[1] - ((self.image.get_width() / 2) + 2) * math.sin(
                    math.radians(self.worm.angle)))
            self.bullet.shoot(speed, self.worm.angle, self)
        else:
            self.bullet.moveto(
                self.rect.x + self.image.get_width() * self.pilot[0] + ((self.image.get_width() / 2) + 2) * math.cos(
                    math.radians(180 - self.worm.angle)),
                self.rect.y + self.image.get_height() * self.pilot[1] - ((self.image.get_width() / 2) + 2) * math.sin(
                    math.radians(180 - self.worm.angle)))
            self.bullet.shoot(speed, 180 - self.worm.angle, self)


weapons = {"bazooka": {"class": Weapon,
                       "radius": 30,
                       "duration": True,
                       "sprite": "guns/bazooka.png",
                       "pilot": (0.5, 0.5),
                       "pilot_pixel": False,
                       "bullet_info": {"class": Bullet,
                                       "sprite": "bullet/bazooka.png",
                                       "radius": 30,
                                       "pilot": [0.5, 0.5],
                                       "pixel_pilot": False,
                                       "ground_contact": True
                                       }},
           "shotgun": {"class": Weapon,
                       "duration": False,
                       "sprite": "guns/shotgun.png",
                       "pilot": (0.5, 0.5),
                       "pilot_pixel": False,
                       "bullet_info": {"class": RayCastBullet,
                                       "sprite": "transparent_image5x5.png",
                                       "radius": 15,
                                       "ground_contact": True}},
           "grenade": {"class": Weapon,
                       "duration": True,
                       "sprite": "guns/grenade.png",
                       "pilot": (0.5, 0.5),
                       "pilot_pixel": False,
                       "bullet_info": {"class": GrenadeBullet,
                                       "sprite": "guns/grenade.png",
                                       "radius": 20,
                                       "pilot": [0.5, 0.5],
                                       "pixel_pilot": False,
                                       "kinematic": False,
                                       "ground_contact": False}},
           }
