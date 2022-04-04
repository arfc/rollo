import numpy as np
import ast

with open("output.txt") as file:
    contents = file.read()
ackley = ast.literal_eval(contents)
print({"ackley": ackley})
