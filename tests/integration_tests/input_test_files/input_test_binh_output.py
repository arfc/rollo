import numpy as np
import ast

file = open("output.txt")
contents = file.read()
binh = ast.literal_eval(contents)
file.close()
print(binh)
