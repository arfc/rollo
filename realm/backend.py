from collections import defaultdict
import pandas as pd
from deap import base, creator, tools, algorithms
import pickle
import numpy 


class BackEnd(object):
    """This class contains and manipulates the output backend"""

    def __init__(self, checkpoint_file, deap_creator):
        self.results = {}
        self.checkpoint_file = checkpoint_file
        self.creator = deap_creator
        self.initialize_stats()

    def initialize_new_backend(self):
        self.results["start_gen"] = 0
        self.results["halloffame"] = tools.HallOfFame(maxsize=1)
        self.results["logbook"] = tools.Logbook()
        self.checkpoint_file = "checkpoint.pkl"
        return

    def initialize_checkpoint_backend(self):
        creator = self.creator
        with open(self.checkpoint_file, "rb") as cp_file:
            cp = pickle.load(cp_file)
        self.results["population"] = cp["population"]
        self.results["start_gen"] = cp["generation"]
        self.results["halloffame"] = cp["halloffame"]
        self.results["logbook"] = cp["logbook"]
        self.results["rndstate"] = cp["rndstate"]
        return

    def initialize_stats(self):
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", numpy.mean)
        self.stats.register("max", numpy.max)

    def update_backend(self, pop, gen, invalid_ind, rndstate):
        self.results["halloffame"].update(pop)
        record = self.stats.compile(pop)
        self.results["logbook"].record(gen=gen, evals=len(invalid_ind), **record)
        cp = dict(
            population=pop,
            generation=gen,
            halloffame=self.results["halloffame"],
            logbook=self.results["logbook"],
            rndstate=rndstate,
        )
        with open(self.checkpoint_file, "wb") as cp_file:
            pickle.dump(cp, cp_file)
