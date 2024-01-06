import numpy as np


class Noise:
    def __init__(self, width, height, func=lambda x: x):
        self.width = width
        self.height = height
        self.array = np.zeros((self.width, self.height))
        self.generate()

    def generate(self):
        pass

print(Sin(100, 100, 5).array)
