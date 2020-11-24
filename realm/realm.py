from .evaluation import Evaluation
from deap import base, creator, tools, algorithms

class Realm(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self): 

