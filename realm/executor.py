from realm.evaluation import Evaluation
from deap import base, creator, tools, algorithms

class Executor(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self): 
        self.hi = 'hi'
    
    def execute(self):
        print('execute realm')
