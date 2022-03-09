import numpy as np
import ast

file = open("input_script_out.txt")
contents = file.read()
ackley = ast.literal_eval(contents)
file.close()
print({"ackley": ackley})
