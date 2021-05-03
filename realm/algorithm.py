from .backend import BackEnd
import random
import time
import warnings
import sys

try:
    from mpi4py import MPI
    import dill

    MPI.pickle.__init__(dill.dumps, dill.loads)
    from mpi4py.futures import MPICommExecutor
except:
    warnings.warn(
        "Failed to import mpi4py. (Only important for parallel method: mpi_evals"
    )
## GIVE CREDIT TO DEAP NOTEBOOK


class Algorithm(object):
    """Builds and runs Genetic Algorithms.

    This class holds functions to generate a generic genetic algorithm.

    Parameters
    ----------
    deap_toolbox : deap.base.Toolbox
        Deap toolbox populated with genetic algorithm parameters for this
        simulation.
    constraint_obj : openmc.Constraints
    checkpoint_file : str
    deap_creator : deap.creator
    control_dict : dict
    output_dict : dict
    """

    def __init__(
        self,
        deap_toolbox,
        constraint_obj,
        checkpoint_file,
        deap_creator,
        control_dict,
        output_dict,
        input_dict,
        start_time,
        parallel_method,
    ):
        self.toolbox = deap_toolbox
        self.constraint_obj = constraint_obj
        self.cp_file = checkpoint_file
        self.backend = BackEnd(
            checkpoint_file,
            deap_creator,
            control_dict,
            output_dict,
            input_dict,
            start_time,
        )
        self.parallel_method = parallel_method

    def generate(self):
        """Executes the genetic algorithm and outputs the summarized
        results into an output file.
        RMB: fitness[0] must be what we are minimizing/maximizing
        This is only for single variable optimization, need to edit it for
        MOOP

        """
        pop = self.toolbox.population(n=self.toolbox.pop_size)
        if self.parallel_method == "multiprocessing":
            try:
                import multiprocessing_on_dill as multiprocessing

                pool = multiprocessing.Pool()
                self.toolbox.register("map", pool.map)
            except:
                warnings.warn(
                    "multiprocessing_on_dill failed to import, realm will run serially."
                )
                pass
        elif self.parallel_method == "mpi_evals":
            try:
                if MPI.COMM_WORLD.rank > 0:
                    while MPI.COMM_WORLD.bcast(None):
                        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
                            pass
                    sys.exit(0)
            except:
                warnings.warn("MPI Failed.")
                pass
        if self.cp_file:
            self.backend.initialize_checkpoint_backend()
            pop = self.backend.results["population"]
            random.setstate(self.backend.results["rndstate"])
        else:
            self.backend.initialize_new_backend()
            pop = self.initialize_pop(pop)
            self.cp_file = "checkpoint.pkl"
        print(self.backend.results["logbook"])
        for gen in range(self.backend.results["start_gen"] + 1, self.toolbox.ngen):
            pop = self.apply_algorithm_ngen(pop, gen)
            print(self.backend.results["logbook"])
        print("REALM Simulation Completed!")
        if self.parallel_method == "mpi_evals":
            try:
                MPI.COMM_WORLD.bcast(False)
            except:
                pass
        return pop

    def initialize_pop(self, pop):
        """Initialize population for genetic algorithm"""
        enter_time = time.time()
        print("Entering generation 0...")
        for i, ind in enumerate(pop):
            ind.gen = 0
            ind.num = i
        # evaluate fitness values of initial pop
        invalids = [ind for ind in pop if not ind.fitness.valid]
        copy_invalids = [self.toolbox.clone(ind) for ind in invalids]
        if self.parallel_method == "mpi_evals":
            try:
                MPI.COMM_WORLD.bcast(True)
                with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
                    fitnesses = executor.map(self.toolbox.evaluate, list(pop))
            except:
                warnings.warn("MPI Failed, realm will run serially.")
                fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
        else:
            fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
        # assign fitness values to individuals
        for ind, fitness in zip(pop, fitnesses):
            fitness_vals = []
            for i in range(self.toolbox.objs):
                fitness_vals.append(fitness[i])
            ind.fitness.values = tuple(fitness_vals)
            ind.output = fitness
        pop = self.constraint_obj.apply_constraints(pop)
        self.backend.update_backend(pop, 0, copy_invalids, random.getstate())
        return pop

    def apply_algorithm_ngen(self, pop, gen):
        print("Entering generation " + str(gen) + "...1")
        pop = self.apply_selection_operator(pop)
        pop = self.apply_mating_operator(pop)
        pop = self.apply_mutation_operator(pop)
        print("hi")
        # define pop's gen, ind num
        for i, ind in enumerate(pop):
            ind.gen = gen
            ind.num = i
        # evaluate fitness of newly created pop for inds with invalid fitness
        invalids = [ind for ind in pop if not ind.fitness.valid]
        copy_invalids = [self.toolbox.clone(ind) for ind in invalids]
        print("owo")
        if self.parallel_method == "mpi_evals":
            try:
                print("in")
                MPI.COMM_WORLD.bcast(True)
                with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
                    fitnesses = executor.map(self.toolbox.evaluate, list(invalids))
            except:
                warnings.warn("MPI Failed, realm will run serially.")
                fitnesses = self.toolbox.map(self.toolbox.evaluate, list(invalids))
        else:
            fitnesses = self.toolbox.map(self.toolbox.evaluate, list(invalids))
        # assign fitness values to individuals
        for ind, fitness in zip(invalids, fitnesses):
            fitness_vals = []
            for i in range(self.toolbox.objs):
                fitness_vals.append(fitness[i])
            ind.fitness.values = tuple(fitness_vals)
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
        final_pop = []
        for child1, child2 in zip(pop[::2], pop[1::2]):
            new_child1 = self.toolbox.clone(child1)
            new_child2 = self.toolbox.clone(child2)
            if random.random() < self.toolbox.cxpb:
                outside_bounds = True
                while outside_bounds:
                    self.toolbox.mate(new_child1, new_child2)
                    del new_child1.fitness.values, new_child2.fitness.values
                    outside_bounds = False
                    for i, val in enumerate(new_child1):
                        if val < self.toolbox.min_list[i]:
                            outside_bounds = True
                        if val > self.toolbox.max_list[i]:
                            outside_bounds = True
                    for i, val in enumerate(new_child2):
                        if val < self.toolbox.min_list[i]:
                            outside_bounds = True
                        if val > self.toolbox.max_list[i]:
                            outside_bounds = True
            final_pop.append(new_child1)
            final_pop.append(new_child2)
        return final_pop

    def apply_mutation_operator(self, pop):
        final_pop = []
        for mutant in pop:
            new_mutant = self.toolbox.clone(mutant)
            if random.random() < self.toolbox.mutpb:
                outside_bounds = True
                while outside_bounds:
                    self.toolbox.mutate(new_mutant)
                    del new_mutant.fitness.values
                    outside_bounds = False
                    for i, val in enumerate(new_mutant):
                        if val < self.toolbox.min_list[i]:
                            outside_bounds = True
                        if val > self.toolbox.max_list[i]:
                            outside_bounds = True
            final_pop.append(new_mutant)
        return final_pop
