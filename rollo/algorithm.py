from .backend import BackEnd
import random
import sys
import logging
import time


class Algorithm(object):
    """The Algorithm class contains methods to initialize and execute the genetic
    algorithm. It executes a general genetic algorithm framework that uses the
    hyperparameters defined in the deap_toolbox, applies constraints defined
    in the constraints_obj, evaluates fitness values using the evaluation
    function produced by Evaluation contained in the deap_toolbox, and saves
    all the results with BackEnd.

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
    parallel_method : {'none', 'multiprocessing', 'job_control'}
        parallelization method

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
            except BaseException:
                logging.warning(
                    " multiprocessing_on_dill failed to import, rollo will" +
                    " run serially. parallel method = none"
                )
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
        for gen in range(
                self.backend.results["start_gen"] + 1,
                self.toolbox.ngen):
            pop = self.apply_algorithm_ngen(pop, gen)
            print(self.backend.results["logbook"])
        print("rollo Simulation Completed!")
        return pop

    def initialize_pop(self, pop):
        """Initialize population for genetic algorithm

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for previous generation

        Returns
        -------
        pop : list
            list of deap.creator.Ind with fitnesses evaluated

        """

        print("Entering generation 0...")
        for i, ind in enumerate(pop):
            ind.gen = 0
            ind.num = i
        # evaluate fitness values of initial pop
        invalids = [ind for ind in pop if not ind.fitness.valid]
        copy_invalids = [self.toolbox.clone(ind) for ind in invalids]
        if self.parallel_method == "job_control":
            logging.warning(" parallel method = job_control")
            fitnesses = self.toolbox.evaluate(pop)
        else:
            logging.warning(" parallel method = none")
            start_time = time.time()
            fitnesses = list(self.toolbox.map(self.toolbox.evaluate, pop))
            end_time = time.time()
            logging.info(" Generation: " +
                         str(0) +
                         ", Evaluation Total Runtime: " +
                         str(round(end_time -
                                   start_time, 2)) +
                         " seconds")
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
        pop : list
            list of deap.creator.Ind for new generation

        """
        print("Entering generation " + str(gen) + "...")
        offspring = self.apply_mating_operator(pop)
        offspring = self.apply_mutation_operator(offspring)
        # define offspring's gen, ind num
        for i, ind in enumerate(offspring):
            ind.gen = gen
            ind.num = i
        # evaluate fitness of newly created inds in offspring
        invalids = [ind for ind in offspring if not ind.fitness.valid]
        copy_invalids = [self.toolbox.clone(ind) for ind in invalids]
        if self.parallel_method == "job_control":
            fitnesses = self.toolbox.evaluate(list(invalids))
        else:
            start_time = time.time()
            fitnesses = list(
                self.toolbox.map(
                    self.toolbox.evaluate,
                    list(invalids)))
            end_time = time.time()
            logging.info(" Generation: " +
                         str(gen) +
                         ", Evaluation Total Runtime: " +
                         str(round(end_time -
                                   start_time, 2)) +
                         " seconds")
        # assign fitness values to individuals
        for ind, fitness in zip(invalids, fitnesses):
            fitness_vals = []
            for i in range(self.toolbox.objs):
                fitness_vals.append(fitness[i])
            ind.fitness.values = tuple(fitness_vals)
            ind.output = fitness
        # expand population before applying selection operator
        pop = self.apply_selection_operator(pop + offspring)
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

        pop = self.toolbox.select(individuals=pop, k=self.toolbox.pop_size)
        return pop

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
