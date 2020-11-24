from .backend import BackEnd 
from num2words import num2words

## GIVE CREDIT TO DEAP NOTEBOOK 

class Algorithm(object): 
    """ Holds genetic algorithms. 
    """

    def __init__(self, deap_toolbox, constraint_obj): 
        self.toolbox = deap_toolbox # deap toolbox object 
        self.results = BackEnd() 
        self.constraint_obj = constraint_obj

    def generate(self): 
        """ Executes the genetic algorithm and outputs the summarized 
        results into an output file. 
        RMB: fitness[0] must be what we are minimizing/maximizing 
        This is only for single variable optimization, need to edit it for 
        MOOP 

        """
        # initialize the algorithm's parameters 
        pop_size = self.toolbox.pop_size
        pop = self.toolbox.population(n=pop_size) 
        ngen, cxpb, mutpb = self.toolbox.ngen, self.toolbox.cxpb, self.toolbox.mutpb
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
            ind.output = fitness
            self.results.add_ind(ind)
        # start working on each generation 
        for g in range(ngen):
            # apply constaint
            pop = self.constraint_obj.apply_constraints(pop)
            # apply selection operator 
            pop = self.toolbox.select(pop, k=pop_size)
            pop = [toolbox.clone(ind) for ind in pop]
            # apply mate operator 
            for child1, child2 in zip(pop[::2], pop[1::2]):
                if random.random() < cxpb:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values, child2.fitness.values
            # apply mutation operator 
            for mutant in pop:
                if random.random() < mutpb:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            # define pop's gen, ind num 
            ind_count = 0 
            for ind in pop: 
                ind.gen = g+1
                ind.num = ind_count
                ind_count += 1 
            # evaluate fitness of newly created population 
            fitnesses = toolbox.map(toolbox.evaluate, pop)
            # assign fitness values to individuals 
            for ind, fitness in zip(pop,fitnesses): 
                ind.fitness.values = (fitness[0],)
                ind.output = fitness
                self.results.add_ind(ind)
        print('Completed!')
        return 
    