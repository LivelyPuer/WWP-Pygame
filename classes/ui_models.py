import pygame

from classes.base import Object


class UIObject(Object):
    def __init__(self, x, y, camera_pos, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.camera_pos = camera_pos

    def update(self):
        super().update()

    def set_by_screen_pos(self, x, y):
        vect = pygame.Vector2(x, y) + self.camera_pos
        self.moveto(vect.x, vect.y)
        self.update_rect()


class WormTarget(UIObject):
    def __init__(self, x, y, camera_pos, *group, sprite="worm_arrow.png", **kwargs):
        super().__init__(x, y, camera_pos, *group, sprite=sprite, **kwargs)
        self.worm = None

    def update(self):
        super().update()

    def set_worm(self, worm: Object):
        self.worm = worm


class WormMarker(WormTarget):
    def __init__(self, x, y, camera_pos, *group, sprite="worm_arrow.png", **kwargs):
        super().__init__(x, y, camera_pos, *group, sprite=sprite, **kwargs)

    def update(self):
        if isinstance(self, WormMarker) and self.worm:
            vect = self.worm.float_position + pygame.Vector2(0, -16)
            self.set_by_screen_pos(vect.x, vect.y)
        super().update()


class ShootMarker(WormTarget):
    def __init__(self, x, y, camera_pos, *group, sprite="shoot_marker.png", **kwargs):
        super().__init__(x, y, camera_pos, *group, sprite=sprite, **kwargs)

    def update(self):
        if self.worm:
            vect = self.worm.rect.center + pygame.Vector2(-100, 0).rotate(
                180 - self.worm.get_angle())

            self.set_by_screen_pos(vect.x, vect.y)
        super().update()
