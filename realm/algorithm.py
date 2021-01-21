from .backend import BackEnd
import random

## GIVE CREDIT TO DEAP NOTEBOOK


class Algorithm(object):
    """Holds genetic algorithms."""

    def __init__(self, deap_toolbox, constraint_obj, checkpoint_file, deap_creator):
        self.toolbox = deap_toolbox
        self.constraint_obj = constraint_obj
        self.cp_file = checkpoint_file
        self.backend = BackEnd(checkpoint_file, deap_creator)

    def generate(self):
        """Executes the genetic algorithm and outputs the summarized
        results into an output file.
        RMB: fitness[0] must be what we are minimizing/maximizing
        This is only for single variable optimization, need to edit it for
        MOOP

        """
        pop = self.toolbox.population(n=self.toolbox.pop_size)
        if self.cp_file:
            self.backend.initialize_checkpoint_backend()
            pop = self.backend.results["population"]
            random.setstate(self.backend.results["rndstate"])
        else:
            self.backend.initialize_new_backend()
            pop = self.initialize_pop(pop)
            self.cp_file = "checkpoint.pkl"
        print(self.backend.results["logbook"].stream)
        for gen in range(self.backend.results["start_gen"] + 1, self.toolbox.ngen):
            print(pop)
            pop = self.apply_algorithm_ngen(pop, gen)
            print(self.backend.results["logbook"])
        print("Completed!")
        return pop

    def initialize_pop(self, pop):
        """Initialize population for genetic algorithm"""
        print("INITIALiZE")
        for i, ind in enumerate(pop):
            ind.gen = 0
            ind.num = i
        # evaluate fitness values of initial pop
        fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
        # assign fitness values to individuals
        for ind, fitness in zip(pop, fitnesses):
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
        invalids = [ind for ind in pop if not ind.fitness.valid]
        pop = self.constraint_obj.apply_constraints(pop)
        self.backend.update_backend(pop, 0, invalids, random.getstate())
        return pop

    def apply_algorithm_ngen(self, pop, gen):
        print("APPLIED")
        pop = self.apply_selection_operator(pop)
        pop = self.apply_mating_operator(pop)
        pop = self.apply_mutation_operator(pop)
        # define pop's gen, ind num
        for i, ind in enumerate(pop):
            ind.gen = gen
            ind.num = i
        # evaluate fitness of newly created pop for inds with invalid fitness
        invalids = [ind for ind in pop if not ind.fitness.valid]
        copy_invalids = [self.toolbox.clone(ind) for ind in invalids]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalids)
        # assign fitness values to individuals
        for ind, fitness in zip(invalids, fitnesses):
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
        pop = self.constraint_obj.apply_constraints(pop)
        self.backend.update_backend(pop, gen, copy_invalids, random.getstate())
        return pop

    def apply_selection_operator(self, pop):
        pre_pop = self.toolbox.select(pop)
        select_pop = [self.toolbox.clone(ind) for ind in pre_pop]
        # extend pop length to pop_size
        while len(select_pop) != self.toolbox.pop_size:
            select_pop.append(self.toolbox.clone(random.choice(pre_pop)))
        return select_pop

    def apply_mating_operator(self, pop):
        for child1, child2 in zip(pop[::2], pop[1::2]):
            if random.random() < self.toolbox.cxpb:
                self.toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        return pop

    def apply_mutation_operator(self, pop):
        for mutant in pop:
            if random.random() < self.toolbox.mutpb:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values
        return pop
