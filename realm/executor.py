import realm
from realm.input_validation import InputValidation
from realm.special_variables import SpecialVariables
from realm.deap_operators import DeapOperators
from realm.algorithm import Algorithm
from realm.constraints import Constraints
from deap import base, creator, tools, algorithms
import json, re, random
from collections import OrderedDict


class Executor(object):
    """A generalized framework to generate reactor designs
    using genetic algorithms.
    """

    def __init__(self, input_file, checkpoint_file=None):
        self.input_file = input_file
        self.checkpoint_file = checkpoint_file

    def execute(self):
        print("execute realm")
        input_dict = self.read_input_file()
        InputValidation(input_dict).validate()
        complete_input_dict = self.add_defaults(input_dict)
        # organize control variables and output dict
        control_dict, output_dict = self.organize_input_output(input_dict)
        # generate evaluator function
        evaluator_fn = self.load_evaluator(control_dict, output_dict, input_dict)
        # DEAP toolbox set up
        toolbox, creator = self.load_toolbox(
            evaluator_fn,
            input_dict["algorithm"],
            input_dict["control_variables"],
            control_dict,
            output_dict,
        )
        # load constraints if they exist
        constraints = self.load_constraints(output_dict, input_dict["constraints"], toolbox)
        alg = Algorithm(
            deap_toolbox=toolbox,
            constraint_obj=constraints,
            checkpoint_file=self.checkpoint_file,
            deap_creator=creator
        )
        alg.generate()

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
                    method = getattr(sv, var + "_num")
                    num = method(input_ctrl_vars[var])
                    control_vars[var] = [solver, num]
                else:
                    control_vars[var] = [solver, 1]

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
            evaluator.add_evaluator(
                solver_name=solver,
                input_script=solver_dict["input_script"],
                output_script=output_script,
            )
        evaluator_fn = evaluator.eval_fn_generator(
            control_dict, output_dict, input_dict["evaluators"]
        )
        return evaluator_fn

    def load_toolbox(
        self, evaluator_fn, input_algorithm, input_ctrl_vars, control_dict, output_dict
    ):
        """This function creates a DEAP toolbox object based on user-defined
        parameters
        """
        if input_algorithm["objective"] == "min":
            weight = -1.0
        elif input_algorithm["objective"] == "max":
            weight = +1.0
        creator.create("obj", base.Fitness, weights=(weight,))
        creator.create("Ind", list, fitness=creator.obj)
        toolbox = base.Toolbox()
        # register control variables + individual
        for var in input_ctrl_vars:
            var_dict = input_ctrl_vars[var]
            toolbox.register(var, random.uniform, var_dict["min"], var_dict["max"])
        toolbox.register(
            "individual", self.individual_values, input_ctrl_vars, control_dict, toolbox
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", evaluator_fn)
        min_list, max_list = self.min_max_list(control_dict, input_ctrl_vars)
        toolbox.min_list, toolbox.max_list = min_list, max_list
        do = DeapOperators()
        toolbox = do.add_toolbox_operators(
            toolbox,
            selection_dict=input_algorithm["selection_operator"],
            mutation_dict=input_algorithm["mutation_operator"],
            mating_dict=input_algorithm["mating_operator"],
            min_list=min_list,
            max_list=max_list,
        )
        toolbox.pop_size = input_algorithm["pop_size"]
        toolbox.ngen = input_algorithm["generations"]
        toolbox.mutpb = input_algorithm["mutation_probability"]
        toolbox.cxpb = input_algorithm["mating_probability"]
        return toolbox, creator

    def min_max_list(self, control_dict, input_ctrl_vars):
        """Returns an ordered list of min values and max values for the
        individual
        """
        min_list = []
        max_list = []
        for var in control_dict:
            for i in range(control_dict[var][1]):
                min_list.append(input_ctrl_vars[var]["min"])
                max_list.append(input_ctrl_vars[var]["max"])
        return min_list, max_list

    def individual_values(self, input_ctrl_vars, control_dict, toolbox):
        """This function returns an individual with ordered control variable
        values
        """
        var_dict = {}
        input_vals = []
        sv = SpecialVariables()
        special_control_vars = sv.special_variables
        for var in control_dict:
            if var in special_control_vars:
                # this func must return a list
                method = getattr(sv, var + "_values")
                result = method(input_ctrl_vars[var], toolbox, var_dict)
                input_vals += result
                var_dict[var] = result
            else:
                result = getattr(toolbox, var)()
                input_vals += [result]
                var_dict[var] = result
        return creator.Ind(input_vals)

    def load_constraints(self, output_dict, input_constraints, toolbox):
        constraint_obj = Constraints(output_dict, input_constraints, toolbox)
        return constraint_obj
