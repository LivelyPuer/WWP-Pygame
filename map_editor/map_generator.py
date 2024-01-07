import random
import sys
from functools import lru_cache

import numpy as np
from scipy import ndimage
from skimage.transform import resize

sys.setrecursionlimit(10000)
funcs = {
    "small-island": lambda x, y, gen_size: y > gen_size[1] * 1.7 - (
            (gen_size[1]) * np.sin(2 * x * np.pi / (gen_size[0] * 2))),
    "two-islands": lambda x, y, gen_size: y > gen_size[1] * 1.5 - (
            (gen_size[1]) * np.sin((x - gen_size[0] / 8) * np.pi / (gen_size[0] / 4))),
    "box-island": lambda x, y, gen_size: y > gen_size[1] * 0.7 and gen_size[1] * 0.25 < x < gen_size[1] * 1.5,
}


def generate_perlin_noise_2d(shape, res_):
    def f(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    delta = (res_[0] / shape[0], res_[1] / shape[1])
    d = (shape[0] // res_[0], shape[1] // res_[1])
    grid = np.mgrid[0:res_[0]:delta[0], 0:res_[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res_[0] + 1, res_[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


def generate_fractal_noise_2d(shape, res_, octaves=1, persistence=0.5):
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * generate_perlin_noise_2d(shape, (frequency * res_[0], frequency * res_[1]))
        frequency *= 2
        amplitude *= persistence

    return noise


class Noise:

    def __init__(self, width=1, height=1, func=lambda x, y, gen_size: x):
        self.width = width
        self.height = height
        self.func = func
        self.gen_size = (1, 1)
        self.noise = np.zeros((self.gen_size[1], self.gen_size[0]))
        self.res = np.zeros((self.gen_size[1], self.gen_size[0]))

    def generate(self, width, height, seed=None):
        self.width = width
        self.height = height
        if seed is not None:
            random.seed(seed)

        self.gen_size = width // 4, height // 4
        self.noise = generate_fractal_noise_2d((self.gen_size[0], self.gen_size[1]),
                                               (self.gen_size[0] // 16, self.gen_size[1] // 16), octaves=1)

        self.res = np.zeros((self.gen_size[0], self.gen_size[1]))

        for i in range(self.noise.shape[0]):
            for j in range(self.noise.shape[1]):
                if self.noise[i][j] < -0.2 or self.noise[i][j] > 0.2:
                    if self.func(i, j, self.gen_size):
                        self.noise[i][j] = 0.2
                    else:
                        self.noise[i][j] = 1
                else:
                    self.noise[i][j] = 0

        for i in range(self.noise.shape[0]):
            for j in range(self.noise.shape[1]):

                if self.res[i][j] == 0 and self.noise[i][j] == 0.2:
                    try:
                        self.paint_n(i, j)
                    except:
                        continue
                if self.func(i, j, self.gen_size):
                    self.res[i][j] = 1

        struct1 = ndimage.generate_binary_structure(2, 1)
        structure = ndimage.generate_binary_structure(2, 2)
        self.res = ndimage.binary_dilation(self.res, structure=struct1, iterations=5)
        self.res = resize(self.res, (self.width, self.height))
        self.res = ndimage.median_filter(self.res, size=8)
        return self.res

    def get_noise(self):
        return self.res

    @lru_cache(maxsize=1024)
    def paint_n(self, x, y):
        if x < 0 or y < 0 or x >= self.noise.shape[0] or y >= self.noise.shape[1]:
            return
        if self.res[x][y] != 0 or self.noise[x][y] == 0:
            return
        self.res[x][y] = 1
        self.paint_n(x, y - 1)
        self.paint_n(x - 1, y)
        self.paint_n(x + 1, y)
        self.paint_n(x, y + 1)


small_island = Noise(func=funcs["small-island"])
two_islands = Noise(func=funcs["two-islands"])
box_island = Noise(func=funcs["box-island"])
