from deap import base, creator, tools
from rollo.special_variables import SpecialVariables
import random


class ToolboxGenerator(object):
    """A class that initializes the DEAP toolbox."""

    def setup(self, evaluator_fn, input_algorithm, input_ctrl_vars, control_dict):
        """sets up DEAP toolbox with user-defined inputs

        Parameters
        ----------
        evaluator_fn : function
            function that runs the evaluation software and returns output values
        input_algorithm : dict
            algorithm sub-dictionary from input file
        input_ctrl_vars : dict
            control variables sub-dictionary from input file
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value

        Returns
        -------
        toolbox : deap.base.Toolbox object
            DEAP toolbox populated with user-defined genetic algorithm parameters
        creator : deap.creator object
            DEAP meta-factory allowing to create classes that will fulfill the
            needs of the evolutionary algorithms

        """

        weight_list = []
        for obj in input_algorithm["objective"]:
            if obj == "min":
                weight_list.append(-1.0)
            elif obj == "max":
                weight_list.append(+1.0)
        creator.create("obj", base.Fitness, weights=tuple(weight_list))
        creator.create("Ind", list, fitness=creator.obj)
        toolbox = base.Toolbox()
        # register control variables + individual
        sv = SpecialVariables()
        special_control_vars = sv.special_variables
        for var in input_ctrl_vars:
            if var not in special_control_vars:
                var_dict = input_ctrl_vars[var]
                toolbox.register(var, random.uniform, var_dict["min"], var_dict["max"])
        toolbox.register(
            "individual", self.individual_values, input_ctrl_vars, control_dict, toolbox
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", evaluator_fn)
        min_list, max_list = self.min_max_list(control_dict, input_ctrl_vars)
        toolbox.min_list, toolbox.max_list = min_list, max_list
        toolbox = self.add_toolbox_operators(
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
        toolbox.objs = len(input_algorithm["objective"])
        return toolbox, creator

    def individual_values(self, input_ctrl_vars, control_dict, toolbox):
        """Returns an individual with ordered control variable values

        Parameters
        ----------
        input_ctrl_vars : dict
            control variables sub-dictionary from input file
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        toolbox : deap.base.Toolbox object
            DEAP toolbox populated with user-defined genetic algorithm parameters

        Returns
        -------
        deap.creator.Ind
            Created in `rollo.toolbox_generator.ToolboxGenerator`. It is
            a list with special attributes.

        """

        var_dict = {}
        input_vals = []
        sv = SpecialVariables()
        special_control_vars = sv.special_variables
        for var in control_dict:
            if var in special_control_vars:
                # this func must return a list
                method = getattr(sv, var + "_values")
                result = method(input_ctrl_vars[var], var_dict)
                input_vals += result
                var_dict[var] = result
            else:
                result = getattr(toolbox, var)()
                input_vals += [result]
                var_dict[var] = result
        return creator.Ind(input_vals)

    def min_max_list(self, control_dict, input_ctrl_vars):
        """Returns an ordered list of min values and max values for the
        individual

        Parameters
        ----------
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        input_ctrl_vars : dict
            control variables sub-dictionary from input file

        Returns
        -------
        min_list : list
            ordered list of minimum values for individual variables
        max_list : list
            ordered list of maximum values for individual variables

        """

        min_list = []
        max_list = []
        for var in control_dict:
            for i in range(control_dict[var][1]):
                min_list.append(input_ctrl_vars[var]["min"])
                max_list.append(input_ctrl_vars[var]["max"])
        return min_list, max_list

    def add_toolbox_operators(
        self, toolbox, selection_dict, mutation_dict, mating_dict, min_list, max_list
    ):
        """Adds selection, mutation, and mating operators to the deap toolbox

        Parameters
        ----------
        toolbox : deap.base.Toolbox object
            initialized DEAP toolbox
        selection_dict : dict
            selection_operator sub-sub-directory from input file
        mutation_dict : dict
            mutation_operator sub-sub-directory from input file
        mating_dict : dict
            mating_operator sub-sub-directory from input file
        min_list : list
            ordered list of minimum values for individual variables
        max_list : list
            ordered list of maximum values for individual variables

        Returns
        -------
        deap.base.Toolbox object
            DEAP toolbox populated with user-defined genetic algorithm parameters

        """

        toolbox = self.add_selection_operators(toolbox, selection_dict)
        toolbox = self.add_mutation_operators(
            toolbox, mutation_dict, min_list, max_list
        )
        toolbox = self.add_mating_operators(toolbox, mating_dict)
        return toolbox

    def add_selection_operators(self, toolbox, selection_dict):
        """Adds selection operator to the deap toolbox

        Parameters
        ----------
        toolbox : deap.base.Toolbox object
            initialized DEAP toolbox
        selection_dict : dict
            selection_operator sub-sub-directory from input file

        Returns
        -------
        deap.base.Toolbox object
            DEAP toolbox populated with user-defined selection operator genetic
            algorithm parameters

        """

        operator = selection_dict["operator"]
        if operator == "selTournament":
            toolbox.register(
                "select",
                tools.selTournament,
                k=selection_dict["inds"],
                tournsize=selection_dict["tournsize"],
            )
        elif operator == "selNSGA2":
            toolbox.register("select", tools.selNSGA2, k=selection_dict["inds"])
        elif operator == "selBest":
            toolbox.register("select", tools.selBest, k=selection_dict["inds"])
        return toolbox

    def add_mutation_operators(self, toolbox, mutation_dict, min_list, max_list):
        """Adds mutation operator to the deap toolbox

        Parameters
        ----------
        toolbox : deap.base.Toolbox object
            initialized DEAP toolbox
        mutation_dict : dict
            mutation_operator sub-sub-directory from input file

        Returns
        -------
        deap.base.Toolbox object
            DEAP toolbox populated with user-defined mutation operator genetic
            algorithm parameters

        """

        operator = mutation_dict["operator"]
        if operator == "mutPolynomialBounded":
            toolbox.register(
                "mutate",
                tools.mutPolynomialBounded,
                eta=mutation_dict["eta"],
                indpb=mutation_dict["indpb"],
                low=min_list,
                up=max_list,
            )
        return toolbox

    def add_mating_operators(self, toolbox, mating_dict):
        """Adds mating operator to the deap toolbox

        Parameters
        ----------
        toolbox : deap.base.Toolbox object
            initialized DEAP toolbox
        mating_dict : dict
            mating_operator sub-sub-directory from input file

        Returns
        -------
        deap.base.Toolbox object
            DEAP toolbox populated with user-defined mating operator genetic
            algorithm parameters

        """

        operator = mating_dict["operator"]
        if operator == "cxOnePoint":
            toolbox.register("mate", tools.cxOnePoint)
        elif operator == "cxUniform":
            toolbox.register("mate", tools.cxUniform, indpb=mating_dict["indpb"])
        elif operator == "cxBlend":
            toolbox.register("mate", tools.cxBlend, alpha=mating_dict["alpha"])
        return toolbox
