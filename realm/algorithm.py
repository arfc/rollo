from .backend import BackEnd
from num2words import num2words

## GIVE CREDIT TO DEAP NOTEBOOK


class Algorithm(object):
    """Holds genetic algorithms."""

    def __init__(self, deap_toolbox, constraint_obj):
        self.toolbox = deap_toolbox  # deap toolbox object
        #self.results = BackEnd(control_dict, output_dict)
        self.constraint_obj = constraint_obj

    def generate(self):
        """Executes the genetic algorithm and outputs the summarized
        results into an output file.
        RMB: fitness[0] must be what we are minimizing/maximizing
        This is only for single variable optimization, need to edit it for
        MOOP

        """
        pop = self.toolbox.population(n=self.toolbox.pop_size)
        pop = self.initialize_pop(pop)
        for g in range(ngen):
            pop = self.apply_algorithm_ngen(pop)
        print("Completed!")
        return

    def initialize_pop(self, pop):
        for i, ind in enumerate(pop):
            ind.gen = 0
            ind.num = i
        # evaluate fitness values of initial pop
        fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
        # assign fitness values to individuals
        for ind, fitness in zip(pop, fitnesses):
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
        return pop

    def apply_algorithm_ngen(self, pop):
        # apply constaint
        pop = self.constraint_obj.apply_constraints(pop)
        # apply selection operator
        pre_pop = self.toolbox.select(pop)
        pop = [toolbox.clone(ind) for ind in pre_pop]
        # extend pop length to pop_size
        while len(pop) != self.toolbox.pop_size:
            pop.append(toolbox.clone(random.choice(pre_pop)))
        # apply mate operator
        for child1, child2 in zip(pop[::2], pop[1::2]):
            if random.random() < self.toolbox.cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        # apply mutation operator
        for mutant in pop:
            if random.random() < self.toolbox.mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # define pop's gen, ind num
        for i, ind in enumerate(pop):
            ind.gen = g + 1
            ind.num = i
        # evaluate fitness of newly created population
        fitnesses = toolbox.map(toolbox.evaluate, pop)
        # assign fitness values to individuals
        for ind, fitness in zip(pop, fitnesses):
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
        return pop