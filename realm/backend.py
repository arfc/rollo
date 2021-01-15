from collections import defaultdict
import pandas as pd
from deap import base, creator, tools, algorithms
import pickle


class BackEnd(object):
    """This class contains and manipulates the output backend"""

    def __init__(self, checkpoint_file):
        self.backend = {}
        self.checkpoint_file = checkpoint_file

    def initialize_new_backend(self):
        self.backend["start_gen"] = 0
        self.backend["halloffame"] = tools.HallofFame(maxsize=1)
        self.backend["logbook"] = tools.LogBook()
        return

    def initialize_checkpoint_backend(self):
        with open(self.checkpoint_file, "r") as cp_file:
            cp = pickle.load(cp_file)
        self.backend["population"] = cp["population"]
        self.backend["start_gen"] = cp["generation"]
        self.backend["halloffame"] = cp["halloffame"]
        self.backend["logbook"] = cp["logbook"]
        self.backend["rndstate"] = cp["rndstate"]
        return

    def initialize_stats():
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", numpy.mean)
        self.stats.register("max", numpy.max)

    def update_backend(self, pop, gen, invalid_ind, rndstate):
        self.backend["halloffame"].update(pop)
        record = self.stats.compile(pop)
        self.backend["logbook"].record(gen=gen, evals=len(invalid_ind), **record)
        cp = dict(
            population=pop,
            generation=gen,
            halloffame=self.backend["halloffame"],
            logbook=self.backend["logbook"],
            rndstate=rndstate,
        )
        with open(self.checkpoint_file, "wb") as cp_file:
            pickle.dump(cp, cp_file)
