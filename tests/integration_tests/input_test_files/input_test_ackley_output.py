import numpy as np
import ast

file = open("evaluator_1_input_script_out.txt")
contents = file.read()
ackley = ast.literal_eval(contents)
print({"ackley": ackley})
