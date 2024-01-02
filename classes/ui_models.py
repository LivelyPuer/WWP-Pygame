import pygame

from classes.base import Object


class UIObject(Object):
    def __init__(self, x, y, camera_pos, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.camera_pos = camera_pos

    def update(self):
        super().update()

    def set_by_screen_pos(self, x, y):
        self.float_position = pygame.Vector2(x, y) + self.camera_pos
        self.update_rect()


class WormMarker(UIObject):
    def __init__(self, x, y, camera_pos, *group, sprite="worm_arrow.png", **kwargs):
        super().__init__(x, y, camera_pos, *group, sprite=sprite, **kwargs)
        self.worm = None

    def update(self):
        if self.worm:
            vect = self.worm.float_position + pygame.Vector2(0, -16)
            self.set_by_screen_pos(vect.x, vect.y)
        super().update()

    def set_worm(self, worm: Object):
        self.worm = worm

