from realm.evaluation import Evaluation
from deap import base, creator, tools, algorithms
import json, re

class Executor(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self, input_file): 
        self.input_file = input_file
    
    def execute(self):
        print('execute realm')
        input_dict = self.read_input_file()
        print(input_dict)
    
    def read_input_file(self): 
        """This function reads a json input file and returns a dictionary"""
        with open(self.input_file) as json_file:
            data = json.load(json_file)
        return data
