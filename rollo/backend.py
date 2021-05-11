from deap import tools
import pickle, numpy, time


class BackEnd(object):
    """This class contains and manipulates the output backend

    Parameters
    ----------
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
    input_file : str
        input file contents
    start_time : float
        time the simulation began

    Attributes
    ----------
    results : dict
        contains results from simulation
    checkpoint_file : str
        Name of checkpoint file
    creator : deap.creator object
        DEAP meta-factory allowing to create classes that will fulfill the
        needs of the evolutionary algorithms
    control_dict : OrderedDict
        Ordered dict of control variables as keys and a list of their
        solver and number of variables as each value
    output_dict : OrderedDict
        Ordered dict of output variables as keys and solvers as values
    input_file : str
        input file contents
    start_time : float
        time the simulation began

    """

    def __init__(
        self,
        checkpoint_file,
        deap_creator,
        control_dict,
        output_dict,
        input_file,
        start_time,
    ):
        self.results = {}
        self.checkpoint_file = checkpoint_file
        self.creator = deap_creator
        self.control_dict = control_dict
        self.output_dict = output_dict
        self.input_file = input_file
        self.start_time = start_time
        self.initialize_stats()

    def initialize_new_backend(self):
        """Initializes brand new backend object"""

        self.results["input_file"] = self.input_file
        self.results["start_gen"] = 0
        self.results["halloffame"] = tools.HallOfFame(maxsize=1)
        self.results["logbook"] = tools.Logbook()
        self.results["logbook"].header = "time", "gen", "evals", "oup", "ind"
        self.results["logbook"].chapters["ind"].header = "avg", "min", "max"
        self.results["logbook"].chapters["oup"].header = "avg", "std", "min", "max"
        self.results["all"] = {}
        self.results["all"]["ind_naming"] = self.ind_naming()
        self.results["all"]["oup_naming"] = self.output_naming()
        self.results["all"]["populations"] = []
        self.results["all"]["outputs"] = []
        self.checkpoint_file = "checkpoint.pkl"
        return

    def ind_naming(self):
        """Returns a dict with control variable name as key and their ordered
        position in Ind as value

        Returns
        -------
        dict
            control variable name as key and ordered position in Ind as value

        """

        names = []
        for ind in self.control_dict:
            if self.control_dict[ind][1] > 1:
                for i in range(self.control_dict[ind][1]):
                    names.append(ind + "_" + str(i))
            else:
                names.append(ind)
        names_dict = {}
        for i, n in enumerate(names):
            names_dict[n] = i
        return names_dict

    def output_naming(self):
        """Returns a dict with output parameter name as key and their ordered
        position as value

        Returns
        -------
        dict
            output parameter name as key and ordered position as value

        """
        oup_dict = {}
        for i, oup in enumerate(self.output_dict):
            oup_dict[oup] = i
        return oup_dict

    def initialize_checkpoint_backend(self):
        """Initialize backend when checkpoint is used"""

        creator = self.creator
        with open(self.checkpoint_file, "rb") as cp_file:
            cp = pickle.load(cp_file)
        self.results["population"] = cp["population"]
        self.results["start_gen"] = cp["generation"]
        self.results["halloffame"] = cp["halloffame"]
        self.results["logbook"] = cp["logbook"]
        self.results["rndstate"] = cp["rndstate"]
        self.results["all"] = cp["all"]
        return

    def initialize_stats(self):
        """Initialize DEAP statistics"""
        stats_ind = tools.Statistics(key=lambda ind: ind)
        stats_ind.register("avg", numpy.mean, axis=0)
        stats_ind.register("std", numpy.std, axis=0)
        stats_ind.register("min", numpy.min, axis=0)
        stats_ind.register("max", numpy.max, axis=0)
        stats_oup = tools.Statistics(key=lambda ind: ind.output)
        stats_oup.register("avg", numpy.mean, axis=0)
        stats_oup.register("std", numpy.std, axis=0)
        stats_oup.register("min", numpy.min, axis=0)
        stats_oup.register("max", numpy.max, axis=0)
        self.mstats = tools.MultiStatistics(ind=stats_ind, oup=stats_oup)
        return

    def update_backend(self, pop, gen, invalid_ind, rndstate):
        """Updates backend. Called after every generation

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for that generation
        gen : int
            generation number
        invalid_ind : list
            list of deap.creator.Ind whose fitnesses had to be evaluated
        rndstate : tuple
            current state of the random number generator

        """

        self.results["halloffame"].update(pop)
        record = self.mstats.compile(pop)
        self.results["logbook"].record(
            time=time.time() - self.start_time,
            gen=gen,
            evals=len(invalid_ind),
            **record
        )
        self.results["all"]["populations"].append(pop)
        pop_oup = []
        for ind in pop:
            pop_oup.append(ind.output)
        self.results["all"]["outputs"].append(pop_oup)
        evaluator_files = {}
        try:
            for solver in self.input_file["evaluators"]:
                with open(
                    self.input_file["evaluators"][solver]["input_script"], "r"
                ) as file:
                    evaluator_files[solver + "_input"] = file.read()
                try:
                    with open(
                        self.input_file["evaluators"][solver]["output_script"], "r"
                    ) as file:
                        evaluator_files[solver + "_output"] = file.read()
                except:
                    pass
        except:
            pass
        cp = dict(
            input_file=self.input_file,
            evaluator_files=evaluator_files,
            population=pop,
            generation=gen,
            halloffame=self.results["halloffame"],
            logbook=self.results["logbook"],
            rndstate=rndstate,
            all=self.results["all"],
        )
        with open(self.checkpoint_file, "wb") as cp_file:
            pickle.dump(cp, cp_file)
        return
