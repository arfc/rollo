import numpy as np
import ast

file = open("evaluator_1_input_script_out.txt")
contents = file.read()
binh = ast.literal_eval(contents)
file.close()
print(binh)
