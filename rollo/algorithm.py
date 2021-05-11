from .backend import BackEnd
import random, warnings, sys

try:
    from mpi4py import MPI
    import dill

    MPI.pickle.__init__(dill.dumps, dill.loads)
    from mpi4py.futures import MPICommExecutor
except:
    warnings.warn(
        "Failed to import mpi4py. (Only important for parallel method: mpi_evals)"
    )


class Algorithm(object):
    """Builds and runs Genetic Algorithms.

    This class holds functions to generate a generic genetic algorithm.

    Parameters
    ----------
    deap_toolbox : deap.base.Toolbox object
        DEAP toolbox populated with user-defined genetic algorithm parameters
    constraint_obj : rollo.constraints.Constraints
        Holds information about constraints for the problem and functions to
        apply the constraints
    checkpoint_file : str
        Name of checkpoint file
    deap_creator : deap.creator object
        DEAP meta-factory allowing to create classes that will fulfill the
        needs of the evolutionary algorithms
    control_dict : OrderedDict
        Ordered dict of control variables as keys and a list of their
        solver and number of variables as each value
    output_dict : OrderedDict
        Ordered dict of output variables as keys and solvers as values

    Attributes
    ----------
    toolbox : deap.base.Toolbox object
        DEAP toolbox populated with user-defined genetic algorithm parameters
    constraint_obj : rollo.constraints.Constraints
        Holds information about constraints for the problem and functions to
        apply the constraints
    cp_file : str
        Name of checkpoint file
    backend : rollo.backend.Backend
        Contains and manipulates the output backend
    parallel_method : str
        parallelization method (none, multiprocessing, mpi_evals)

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
        """Executes the genetic algorithm and outputs the summarized results
        into an output file

        Returns
        -------
        list
            list of deap.creator.Ind for final generation

        """

        pop = self.toolbox.population(n=self.toolbox.pop_size)
        if self.parallel_method == "multiprocessing":
            try:
                import multiprocessing_on_dill as multiprocessing

                pool = multiprocessing.Pool()
                self.toolbox.register("map", pool.map)
            except:
                warnings.warn(
                    "multiprocessing_on_dill failed to import, rollo will run serially."
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
        print("rollo Simulation Completed!")
        if self.parallel_method == "mpi_evals":
            try:
                MPI.COMM_WORLD.bcast(False)
            except:
                pass
        return pop

    def initialize_pop(self, pop):
        """Initialize population for genetic algorithm

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for previous generation

        Returns
        -------
        list
            list of deap.creator.Ind with fitnesses evaluated

        """

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
                warnings.warn("MPI Failed, rollo will run serially.")
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
        """Apply genetic algorithm to a population

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for previous generation
        gen: int
            generation number

        Returns
        -------
        list
            list of deap.creator.Ind for new generation

        """
        print("Entering generation " + str(gen) + "...")
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
        if self.parallel_method == "mpi_evals":
            try:
                MPI.COMM_WORLD.bcast(True)
                with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
                    fitnesses = executor.map(self.toolbox.evaluate, list(invalids))
            except:
                warnings.warn("MPI Failed, rollo will run serially.")
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
        """Applies selection operator to population

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for that generation

        Returns
        -------
        list
            new list of deap.creator.Ind after selection operator application

        """

        pre_pop = self.toolbox.select(pop)
        select_pop = [self.toolbox.clone(ind) for ind in pre_pop]
        # extend pop length to pop_size
        while len(select_pop) != self.toolbox.pop_size:
            select_pop.append(self.toolbox.clone(random.choice(pre_pop)))
        return select_pop

    def apply_mating_operator(self, pop):
        """Applies mating operator to population

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for that generation

        Returns
        -------
        list
            new list of deap.creator.Ind after mating operator application

        """

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
        """Applies mutation operator to population

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for that generation

        Returns
        -------
        list
            new list of deap.creator.Ind after mutation operator application

        """

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
