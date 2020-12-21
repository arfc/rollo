import realm
from realm.input_validation import InputValidation
from realm.special_variables import SpecialVariables
from deap import base, creator, tools, algorithms
import json, re
from collections import OrderedDict


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
        complete_input_dict = self.add_defaults(input_dict)
        model = self.load_model(complete_input_dict)

    def read_input_file(self):
        """This function reads a json input file and returns a dictionary"""
        with open(self.input_file) as json_file:
            data = json.load(json_file)
        return data

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

    def load_model(self, input_dict):
        """This function loads the user-defined model"""
        # organize control variables and output dict
        control_dict, output_dict = self.organize_input_output(input_dict)
        # generate evaluator function
        evaluator_fn = self.load_evaluator(control_dict, output_dict, input_dict)
        # DEAP toolbox set up
        # toolbox = self.load_toolbox(evaluator_fn)
        # load constraints if they exist
        # constraints = self.load_constraints()
        return model

    def organize_input_output(self, input_dict):
        """This function numbers the control variables and output variables
        to keep consistency between evaluation, constraints, and algorithm
        classes
        """
        input_ctrl_vars = input_dict["control_variables"]
        input_evaluators = input_dict["evaluators"]
        input_algorithm = input_dict["algorithm"]

        # define control variables dict
        control_vars = OrderedDict()
        sv = SpecialVariables()
        special_control_vars = sv.special_variables
        for solver in input_evaluators:
            for var in input_evaluators[solver]["inputs"]:
                if var in special_control_vars:
                    method = getattr(sv, var + "_naming")
                    var_list = method(input_ctrl_vars[var])
                    for v in var_list:
                        control_vars[v] = solver
                else:
                    control_vars[var] = solver

        # define output variables dict
        output_vars = OrderedDict()
        optimized_variable = input_algorithm["optimized_variable"]
        # find optimized variable
        output_list = []
        for solver in input_evaluators:
            for var in input_evaluators[solver]["outputs"]:
                if var == optimized_variable:
                    output_vars[var] = solver
        # put in the rest of the output variables
        for solver in input_evaluators:
            for var in input_evaluators[solver]["outputs"]:
                if var != optimized_variable:
                    output_vars[var] = solver

        return control_vars, output_vars

    def load_evaluator(self, control_dict, output_dict, input_dict):
        """This function creates an Evaluation function object"""
        input_evaluators = input_dict["evaluators"]
        evaluator = realm.Evaluation()
        for solver in input_evaluators:
            solver_dict = input_evaluators[solver]
            try:
                output_script = solver_dict["output_script"]
            except:
                output_script = None
            print(solver, solver_dict["input_script"], output_script)
            evaluator.add_evaluator(
                solver_name=solver,
                input_script=solver_dict["input_script"],
                output_script=output_script,
            )
        evaluator_fn = evaluator.eval_fn_generator(
            control_dict, output_dict, input_dict["evaluators"]
        )
        return evaluator_fn

    def load_toolbox(self, evaluator_fn):
        """This function creates a DEAP toolbox object based on user-defined
        parameters
        """
        input_algorithm = self.input_dict["algorithm"]
        input_ctrl_vars = self.input_dict["control_variables"]
        if input_algorithm["objective"] == "min":
            weight = -1.0
        elif input_algorithm["objective"] == "max":
            weight = +1.0
        creator.create(obj, base.fitness, weights=(weight,))
        creator.create("Ind", list, fitness=creator.obj)  # output??
        toolbox = base.Toolbox()
        # register control variables + individual

        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", evaluator_fn)
        toolbox.register(
            "mate",
        )
        return toolbox

    def load_constraints(self):
        return
