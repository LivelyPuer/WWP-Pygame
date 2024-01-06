import sys
from functools import lru_cache

from skimage.transform import resize
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage

import config

sys.setrecursionlimit(10000)


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


def scale_range(input, min, max):
    input += -(np.min(input))
    input /= np.max(input) / (max - min)
    input += min
    return input


@lru_cache(maxsize=10024)
def paint_n(x, y):
    global noise, res
    if x < 0 or y < 0 or x >= noise.shape[0] or y >= noise.shape[1]:
        return
    if res[x][y] != 0 or noise[x][y] == 0:
        return
    res[x][y] = 1
    paint_n(x, y - 1)
    paint_n(x - 1, y)
    paint_n(x + 1, y)
    paint_n(x, y + 1)


# np.random.seed(0)
gen_size = config.gen_map_size[0] // 4, config.gen_map_size[1] // 4
noise = generate_fractal_noise_2d((gen_size[1], gen_size[0]),
                                  (gen_size[1] // 16, gen_size[0] // 16), octaves=1)

res = np.zeros((gen_size[1], gen_size[0]))
funcs = [
    lambda y, x: y > gen_size[1] * 1.7 - ((gen_size[1]) * np.sin(2 * x * np.pi / (gen_size[0] * 2))),
    lambda y, x: y > gen_size[1] * 1.5 - ((gen_size[1]) * np.sin((x - gen_size[0] / 8) * np.pi / (gen_size[0] / 4))),
    lambda y, x: y > gen_size[1] * 0.7 and gen_size[1] * 0.25 < x < gen_size[1] * 1.5,

]
for i in range(noise.shape[0]):
    for j in range(noise.shape[1]):
        # if i - 10 < 50 + ((j - gen_size[0] / 2) ** 2) / (gen_size[1] / 2) < i + 10:
        #     noise[i][j] = 0
        if noise[i][j] < -0.2 or noise[i][j] > 0.2:
            if funcs[1](i, j):
                noise[i][j] = 0.2
            else:
                noise[i][j] = 1
        else:
            noise[i][j] = 0

fig = plt.figure()
ax1 = fig.add_subplot(2, 1, 1)
ax1.imshow(noise, cmap='gray', interpolation='lanczos')

for i in range(noise.shape[0]):
    for j in range(0, noise.shape[1]):

        if res[i][j] == 0 and noise[i][j] == 0.2:
            try:
                paint_n(i, j)
            except:
                continue
        if funcs[1](i, j):
            res[i][j] = 1

struct1 = ndimage.generate_binary_structure(2, 1)
res = ndimage.binary_dilation(res, structure=struct1, iterations=5)
res = resize(res, (config.gen_map_size[1], config.gen_map_size[0]))
ax2 = fig.add_subplot(2, 1, 2)
ax2.imshow(res, cmap='gray', interpolation='lanczos')

plt.show()
