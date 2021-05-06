import rollo
from rollo.input_validation import InputValidation
from rollo.special_variables import SpecialVariables
from rollo.algorithm import Algorithm
from rollo.constraints import Constraints
from rollo.toolbox_generator import ToolboxGenerator
import json, time
from collections import OrderedDict


class Executor(object):
    """Executes rollo simulation from start to finish.

    Instances of this class can be used to perform a rollo run.

    Parameters
    ----------
    input_file : str
        Name of input file
    checkpoint_file : str, optional
        Name of checkpoint file

    Attributes
    ----------
    input_file : str
        Name of input file
    checkpoint_file : str
        Name of checkpoint file

    """

    def __init__(self, input_file, checkpoint_file=None):
        self.input_file = input_file
        self.checkpoint_file = checkpoint_file

    def execute(self):
        """Executes rollo simulation to generate reactor designs. \n
        1) Read and validate input file
        2) Initialize evaluator
        3) Initialize DEAP toolbox
        4) Initialize constraints
        5) Run genetic algorithm

        """
        t0 = time.time()
        input_dict = self.read_input_file()
        iv = InputValidation(input_dict)
        iv.validate()
        complete_input_dict = iv.add_defaults(input_dict)
        # organize control variables and output dict
        control_dict, output_dict = self.organize_input_output(complete_input_dict)
        # generate evaluator function
        evaluator_fn = self.load_evaluator(
            control_dict, output_dict, complete_input_dict
        )
        # DEAP toolbox set up
        toolbox, creator = self.load_toolbox(
            evaluator_fn,
            complete_input_dict["algorithm"],
            complete_input_dict["control_variables"],
            control_dict,
        )
        # load constraints if they exist
        constraints = self.load_constraints(
            output_dict, complete_input_dict["constraints"], toolbox
        )
        alg = Algorithm(
            deap_toolbox=toolbox,
            constraint_obj=constraints,
            checkpoint_file=self.checkpoint_file,
            deap_creator=creator,
            control_dict=control_dict,
            output_dict=output_dict,
            input_dict=complete_input_dict,
            start_time=t0,
            parallel_method=complete_input_dict["algorithm"]["parallel"],
        )
        alg.generate()
        t1 = time.time()
        print("Total time in simulation " + str(t1 - t0) + " seconds")
        return

    def read_input_file(self):
        """Reads a json input file and returns a dictionary

        Returns
        -------
        data : dict
            json input file converted into a dict

        """

        with open(self.input_file) as json_file:
            data = json.load(json_file)
        return data

    def organize_input_output(self, input_dict):
        """Numbers the control variables and output variables
        to keep consistency between evaluation, constraints, and algorithm
        classes

        Parameters
        ----------
        input_dict : dict
            input file dict

        Returns
        -------
        control_vars : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        output_vars : OrderedDict
            Ordered dict of output variables as keys and solvers as values

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
        var_to_solver = {}
        for solver in input_evaluators:
            for var in input_evaluators[solver]["outputs"]:
                var_to_solver[var] = solver
        for opt_var in optimized_variable:
            output_vars[opt_var] = var_to_solver[opt_var]
        # put in the rest of the output variables
        for solver in input_evaluators:
            for var in input_evaluators[solver]["outputs"]:
                if var not in optimized_variable:
                    output_vars[var] = solver

        return control_vars, output_vars

    def load_evaluator(self, control_dict, output_dict, input_dict):
        """Creates an Evaluation function object

        Parameters
        ----------
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        input_dict : dict
            input file dict with default values filled

        Returns
        -------
        evaluator_fn : function
            function that runs the evaluation software and returns output values
            output by the software

        """
        input_evaluators = input_dict["evaluators"]
        evaluator = rollo.Evaluation()
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
        self, evaluator_fn, input_algorithm, input_ctrl_vars, control_dict
    ):
        """Creates a DEAP toolbox object based on user-defined
        parameters.

        Parameters
        ----------
        evaluator_fn : function
            function that runs the evaluation software and returns output values
            output by the software
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
        toolbox_generator = ToolboxGenerator()
        toolbox, creator = toolbox_generator.setup(
            evaluator_fn, input_algorithm, input_ctrl_vars, control_dict
        )
        return toolbox, creator

    def load_constraints(self, output_dict, input_constraints, toolbox):
        """Creates a Constraints object loaded with user-defined
        constraints information.

        Parameters
        ----------
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        input_constraints : dict
            constraints sub-dictionary from input file
        toolbox : deap.base.Toolbox object
            DEAP toolbox populated with genetic algorithm parameters for this
            creator

        Returns
        -------
        constraints_obj : rollo.Constraints object
            Constraints object loaded with constraint information from the
            input file

        """

        constraint_obj = Constraints(output_dict, input_constraints, toolbox)
        return constraint_obj
