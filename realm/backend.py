from collections import defaultdict
import pandas as pd
from deap import base, creator, tools, algorithms
import pickle
import numpy


class BackEnd(object):
    """This class contains and manipulates the output backend"""

    def __init__(
        self, checkpoint_file, deap_creator, control_dict, output_dict, input_file
    ):
        self.results = {}
        self.checkpoint_file = checkpoint_file
        self.creator = deap_creator
        self.control_dict = control_dict
        self.output_dict = output_dict
        self.input_file = input_file
        self.initialize_stats()

    def initialize_new_backend(self):
        self.results["input_file"] = self.input_file
        self.results["start_gen"] = 0
        self.results["halloffame"] = tools.HallOfFame(maxsize=1)
        self.results["logbook"] = tools.Logbook()
        self.results["logbook"].header = "gen", "evals", "ind", "oup"
        self.results["logbook"].chapters["ind"].header = "avg", "std", "min", "max"
        self.results["logbook"].chapters["oup"].header = "avg", "std", "min", "max"
        self.results["all"] = {}
        self.results["all"]["ind_naming"] = self.ind_naming()
        self.results["all"]["oup_naming"] = self.output_naming()
        self.results["all"]["populations"] = []
        self.results["all"]["outputs"] = []
        self.checkpoint_file = "checkpoint.pkl"

        return

    def ind_naming(self):
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
        oup_dict = {}
        for i, oup in enumerate(self.output_dict):
            oup_dict[oup] = i
        return oup_dict

    def initialize_checkpoint_backend(self):
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

    def update_backend(self, pop, gen, invalid_ind, rndstate):
        self.results["halloffame"].update(pop)
        record = self.mstats.compile(pop)
        self.results["logbook"].record(gen=gen, evals=len(invalid_ind), **record)
        self.results["all"]["populations"].append(pop)
        pop_oup = []
        for ind in pop:
            pop_oup.append(ind.output)
        self.results["all"]["outputs"].append(pop_oup)
        cp = dict(
            input_file=self.input_file,
            population=pop,
            generation=gen,
            halloffame=self.results["halloffame"],
            logbook=self.results["logbook"],
            rndstate=rndstate,
            all=self.results["all"],
        )
        with open(self.checkpoint_file, "wb") as cp_file:
            pickle.dump(cp, cp_file)
