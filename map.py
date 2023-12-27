import cv2
import numpy as np
import pygame
from perlin_numpy import (
    generate_perlin_noise_2d, generate_fractal_noise_2d
)

import config


class Map:
    mask: np.array
    back_image = np.array(0)
    image: np.array
    bul_mask: np.array
    size = (1024, 576)

    def __init__(self):
        np.random.seed = 1
        bul_mask = np.zeros(self.size)

    def draw_map(self, screen):
        # mask = (255 * self.mask / self.mask.max()).transpose()
        if self.back_image:
            invert_mask = np.invert(self.mask.astype("bool")).astype("uint8")
            masked_imp = cv2.bitwise_and(self.back_image, self.back_image, mask=invert_mask)
            masked = cv2.bitwise_and(self.image, self.image, mask=self.mask)
            res = cv2.bitwise_or(masked, masked_imp)
        else:
            res = cv2.bitwise_and(self.image, self.image, mask=self.mask)
        surf = pygame.surfarray.make_surface(res)
        # imp.blit(surf, (0, 0))
        screen.blit(surf, (0, 0))

    def set_image(self, image_path: str, color="RGB"):
        self.image = cv2.transpose(cv2.resize(cv2.imread(image_path)[..., ::-1], self.size))
        print(self.image.shape, self.mask.shape)

    def set_back_image(self, image_path: str):
        self.back_image = cv2.transpose(cv2.resize(cv2.imread(image_path)[..., ::-1], self.size))

    def remove_circle(self, x, y, radius):
        print("remove")
        xx = np.arange(self.mask.shape[0])
        yy = np.arange(self.mask.shape[1])
        val = [[x, y], radius]
        inside = (xx[:, None] - val[0][0]) ** 2 + (yy[None, :] - val[0][1]) ** 2 <= (radius ** 2)
        self.mask = self.mask & ~inside
        pygame.display.update()

    def check_on_ground(self, rect: pygame.Rect) -> bool:
        # print(np.any(self.mask[rect.left:rect.right, rect.bottom:rect.bottom + 1]))
        return np.any(self.mask[rect.left:rect.right, rect.bottom:rect.bottom + 1])

    def check_in_ground(self, rect: pygame.Rect) -> bool:
        return np.any(self.mask[rect.left:rect.right, rect.bottom - 1:rect.bottom])

    def can_move_right(self, rect: pygame.Rect, limit=0.7) -> bool:
        return np.mean(self.mask[rect.right:rect.right + 1, rect.top:rect.bottom]) < limit

    def can_move_left(self, rect: pygame.Rect, limit=0.7) -> bool:
        return np.mean(self.mask[rect.left - 1:rect.left, rect.top:rect.bottom]) < limit

    def check_ground_top(self, rect: pygame.Rect) -> bool:
        return np.any(self.mask[rect.left:rect.right, rect.top: rect.top + 1])


class GenerateMap(Map):
    types = {"perlin": generate_perlin_noise_2d,
             "fractal": generate_fractal_noise_2d}
    type_noise = generate_perlin_noise_2d

    def __init__(self, type_noise: str = "perlin"):
        super().__init__()
        self.type_noise = self.types[type_noise]
        self.mask = self.type_noise(self.size, (4, 4))
        mx, mn = np.max(self.mask), np.min(self.mask)
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                m = 1 if (self.mask[i][j] - mn) / (mx - mn) > 0.5 else 0
                self.mask[i][j] = m
        self.mask = self.mask.astype("uint8")
        print(self.mask)


class ImageMap(Map):
    def __init__(self):
        super().__init__()


game_map = GenerateMap("fractal")
game_map.set_image("data/images/img.jpg")

screen_bound = pygame.Rect(0, 0, config.height, config.height)
