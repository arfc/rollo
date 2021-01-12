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
        for gen in range(ngen):
            pop = self.apply_algorithm_ngen(pop, gen)
        print("Completed!")
        return

    def initialize_pop(self, pop):
        """ Initialize population for genetic algorithm 
        """
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

    def apply_algorithm_ngen(self, pop, gen):
        pop = self.constraint_obj.apply_constraints(pop)
        pop = self.apply_selection_operator(pop)
        pop = self.apply_mating_operator(pop)
        pop = self.apply_mutation_operator(pop)
        # define pop's gen, ind num
        for i, ind in enumerate(pop):
            ind.gen = gen + 1
            ind.num = i
        # evaluate fitness of newly created population
        fitnesses = toolbox.map(toolbox.evaluate, pop)
        # assign fitness values to individuals
        for ind, fitness in zip(pop, fitnesses):
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
        return pop

    def apply_selection_operator(self, pop): 
        pre_pop = self.toolbox.select(pop)
        pop = [toolbox.clone(ind) for ind in pre_pop]
        # extend pop length to pop_size
        while len(pop) != self.toolbox.pop_size:
            pop.append(toolbox.clone(random.choice(pre_pop)))
        return pop

    def apply_mating_operator(self, pop):
        for child1, child2 in zip(pop[::2], pop[1::2]):
            if random.random() < self.toolbox.cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        return pop

    def apply_mutation_operator(self, pop):
        for mutant in pop:
            if random.random() < self.toolbox.mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        return pop