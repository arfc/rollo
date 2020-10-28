from collections import defaultdict

class Algorithms(): 
    """ Holds genetic algorithms 
    """
    def __init__(self, deap_toolbox, params): 
        self.toolbox = deap_toolbox
        self.params = params 
    
    def customized_algorithm():
        pop_size = self.params['pop_size']
        pop = self.toolbox.population(n=pop_size) 
        ngen, cxpb, mutpb = self.params['ngen'],
                            self.params['cxpb']
                            self.params['mutpb']
        fitnesses = self.toolbox.map(toolbox.evaluate, pop)

        return results 
