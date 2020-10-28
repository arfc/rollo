from .backend import BackEnd 

class GenerateReactor(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self, deap_toolbox, params): 
        self.deap_toolbox = deap_toolbox # deap toolbox object 
        self.params = params # dict 

    def generate(self): 
        """ Executes the genetic algorithm and outputs the summarized 
        results into an output file. 
        """
    