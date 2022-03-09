import numpy as np
import ast

file = open("input_script_out.txt")
contents = file.read()
binh = ast.literal_eval(contents)
file.close()
print(binh)
