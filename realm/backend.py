from collections import defaultdict
import pandas as pd
from deap import base, creator, tools, algorithms


class BackEnd(object):
    """This class contains and manipulates the output results"""

    def __init__(self):
        self.results = {}


    def initialize_new_backend(self):
        self.results["start_gen"] = 0 
        self.results["halloffame"] = tools.HallofFame(maxsize=1)
        self.results["logbook"] = tools.LogBook()
        return 

    def initialize_checkpoint_backend(self, cp_file):
        with open(checkpoint, "r") as cp_file:
            cp = pickle.load(cp_file)
        self.results["population"] = cp["population"]
        self.results["start_gen"] = cp["generation"]
        self.results["halloffame"] = cp["halloffame"]
        self.results["logbook"] = cp["logbook"]
        self.results["rndstate"] = cp["rndstate"]
        return