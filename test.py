import numpy as np
ar1 = np.array([0, 0, 1, 0, 1, 1, 1, 1, 1]).reshape((3, 3))
ar2 = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0]).reshape((3, 3))

print(ar1 & ~ar2)