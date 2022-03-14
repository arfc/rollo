import numpy as np
import ast

file = open("openmc_input_script_out.txt")
contents = file.read()
ackley = ast.literal_eval(contents)
file.close()
print({"ackley": ackley})
