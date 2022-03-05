import numpy as np

x1 = {{x1}}
x2 = {{x2}}
ackley = (
    -20 * np.exp(-0.2 * np.sqrt(1 / 2 * (x1 ** 2 + x2 ** 2)))
    - np.exp(1 / 2 * (np.cos(2 * np.pi * x1) + np.cos(2 * np.pi * x2)))
    + 20
    + np.exp(1)
)

print(ackley)
