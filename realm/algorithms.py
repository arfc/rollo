from collections import defaultdict
from num2words import num2words

class Algorithms(): 
    """ Holds genetic algorithms 
    """
    def __init__(self, deap_toolbox, params, constraint_obj, eval_obj):
        self.toolbox = deap_toolbox
        self.params = params 
    
    def customized_algorithm():
        # initialize the algorithm's parameters 
        pop_size = self.params['pop_size']
        pop = self.toolbox.population(n=pop_size) 
        ngen, cxpb, mutpb = self.params['ngen'],
                            self.params['cxpb']
                            self.params['mutpb']
        # initialize first pop's gen, ind num 
        ind_count = 0
        for ind in pop: 
            ind.gen = 0 
            ind.num = ind_count 
            ind_count += 1
        # evaluate fitness values of initial pop 
        fitnesses = self.toolbox.map(toolbox.evaluate, pop)
        # assign fitness values to individuals 
        for ind, fitness in zip(pop,fitnesses): 
            ind.fitness.values = (fitness[0],)
            # naming fitness values by position 
            for i in range(len(fitness)): 
                if i != 0: 
                    setattr(ind, num2words(i), fitness[i])
        return results 
