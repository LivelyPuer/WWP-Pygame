import numpy as np

a = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
b = np.array([[1, 1], [1, 1]])
a[1:3, 1:3] = b
print(a)
