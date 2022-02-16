import numpy as np
import ast 

file = open("output.txt")
contents = file.read()
ackley = ast.literal_eval(contents)
file.close()
print({"ackley":ackley})