from realm.input_validation import InputValidation
from deap import base, creator, tools, algorithms
import json, re


class Executor(object):
    """A generalized framework to generate reactor designs
    using genetic algorithms.
    """

    def __init__(self, input_file):
        self.input_file = input_file

    def execute(self):
        print("execute realm")
        input_dict = self.read_input_file()
        InputValidation(input_dict).validate()
        self.input_dict = self.add_defaults(input_dict)
        model = self.load_model()

    def add_defaults(self, input_dict):
        """This function adds default inputs if they are missing from
        the input_dict
        """
        input_algorithm = input_dict["algorithm"]
        input_algorithm = self.default_check(input_algorithm, "objective", "min")
        input_algorithm = self.default_check(input_algorithm, "pop_size", 100)
        input_algorithm = self.default_check(input_algorithm, "generations", 10)
        input_algorithm = self.default_check(
            input_algorithm, "selection_operator", {"operator": "selBest", "k": 1}
        )
        input_algorithm = self.default_check(
            input_algorithm,
            "mutation_operator",
            {"operator": "mutGaussian", "indpb": 0.5, "mu": 0.5, "sigma": 0.5},
        )
        input_algorithm = self.default_check(
            input_algorithm, "mating_operator", {"operator": "cxOnePoint"}
        )
        reloaded_input_dict = input_dict.copy()
        reloaded_input_dict["algorithm"] = input_algorithm
        return reloaded_input_dict

    def default_check(self, input_dict, variable, default_val):
        """This function checks if a variable is missing from a dict, and
        adds a default value if it is
        """
        try:
            a = input_dict[variable]
        except KeyError:
            input_dict[variable] = default_val
        return input_dict

    def read_input_file(self):
        """This function reads a json input file and returns a dictionary"""
        with open(self.input_file) as json_file:
            data = json.load(json_file)
        return data

    def load_model(self):
        """This function loads the user-defined model"""
        # generate evaluator function
        evaluator_fn = self.load_evaluator()
        # DEAP toolbox set up
        toolbox = self.load_toolbox()
        # load constraints if they exist

        return model

    def load_evaluator(self):
        """This function creates an Evaluation function object"""
        input_evaluators = self.input_dict["evaluators"]
        evaluator = realm.Evaluation()
        for solver in input_evaluators:
            solver_dict = input_evaluators[solver]
            evaluator.add_evaluator(
                solver_name=solver,
                input_script=solver_dict["input_script"],
            )
        return evaluator_fn

    def load_toolbox(self):
        """This function creates a DEAP toolbox object based on user-defined
        parameters
        """
        input_algorithm = self.input_dict["algorithm"]
        if input_algorithm["objective"] == "min":
            weight = -1.0
        elif input_algorithm["objective"] == "max":
            weight = +1.0
        creator.create(obj, base.fitness, weights=(weight,))
        creator.create("Ind", list, fitness=creator.obj)
