

class GenerateReactor(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self, deap_toolbox): 
        self.deap_toolbox = deap_toolbox

    def generate(self): 
        """ Executes the genetic algorithm and outputs the summarized 
        results into an output file. 
        """
    