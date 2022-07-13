from jsonschema import validate
import logging


class InputValidation:
    """The InputValidation class contains methods to read and validate the JSON
    ROLLO input file to ensure the user defined all key parameters. If the
    user did not, ROLLO raises an exception to tell the user which
    parameters are missing.

    Attributes
    ----------
    input : dict
        rollo json input file as a dict

    """

    def __init__(self, input_dict):
        self.input = input_dict

    def add_all_defaults(self):
        """Goes through the entire input_dict and adds default inputs if they
        are missing from the input_dict

        Parameters
        ----------
        input_dict: dict
            input file dict

        Returns
        -------
        reloaded_input_dict: dict
            input file dict with additional missing default inputs

        """
        input_dict = self.input.copy()
        input_algorithm = input_dict["algorithm"]
        input_algorithm = self.default_check(
            input_algorithm, "objective", "min")
        input_algorithm = self.default_check(
            input_algorithm, "keep_files", "all")
        input_algorithm = self.default_check(input_algorithm, "weight", [1.0])
        input_algorithm = self.default_check(input_algorithm, "pop_size", 60)
        input_algorithm = self.default_check(
            input_algorithm, "generations", 10)
        input_algorithm = self.default_check(
            input_algorithm, "mutation_probability", 0.23
        )
        input_algorithm = self.default_check(
            input_algorithm, "mating_probability", 0.47
        )
        input_algorithm = self.default_check(
            input_algorithm,
            "selection_operator",
            {"operator": "selTournament", "tournsize": 5},
        )
        input_algorithm = self.default_check(
            input_algorithm,
            "mutation_operator",
            {"operator": "mutPolynomialBounded", "eta": 0.23, "indpb": 0.23},
        )
        input_algorithm = self.default_check(
            input_algorithm,
            "mating_operator",
            {"operator": "cxBlend", "alpha": 0.46},
        )
        reloaded_input_dict = input_dict.copy()
        reloaded_input_dict["algorithm"] = input_algorithm
        self.input = reloaded_input_dict.copy()
        return

    def default_check(self, input_dict, variable, default_val):
        """Checks if a single variable is missing from a dict, and adds a
        default value if it is

        Parameters
        ----------
        input_dict: dict
            input file dict
        variable: str
            variable name
        default_val: any type accepted
            default input for that variable (can be str, float, dict, etc.)

        Returns
        -------
        input_dict: dict
            input file dict with additional missing default input defined by
            parameters of this function

        """
        try:
            a = input_dict[variable]
        except KeyError:
            input_dict[variable] = default_val
            logging.warning(
                " ROLLO added default for variable: " +
                str(variable) +
                ", default value = " +
                str(default_val))
        return input_dict

    def validate(self):
        """Validates the input dictionary and throws errors if the input file
        does not meet rollo input file rules.

        """

        # validate top layer of JSON input
        schema_top_layer = {
            "type": "object",
            "properties": {
                "control_variables": {"type": "object"},
                "evaluators": {"type": "object"},
                "constraints": {"type": "object"},
                "algorithm": {"type": "object"},
            },
        }
        validate(instance=self.input, schema=schema_top_layer)
        self.validate_correct_keys(
            self.input,
            ["control_variables", "evaluators", "algorithm"],
            ["constraints"],
            "top level",
        )

        # validate control variables
        try:
            input_ctrl_vars = self.input["control_variables"]
        except KeyError:
            print(
                "<Input Validation Error> At least 1 control variable must \
            be defined."
            )
        else:
            self.validate_ctrl_vars(input_ctrl_vars)

        # validate evaluators
        try:
            input_evaluators = self.input["evaluators"]
        except KeyError:
            print(
                "<Input Validation Error> At least 1 evaluator must be \
            defined."
            )
        else:
            self.validate_evaluators(input_evaluators)

        # validate constraints
        try:
            input_constraints = self.input["constraints"]
        except KeyError:
            pass
        else:
            self.validate_constraints(input_constraints, input_evaluators)

        # validate algorithm
        try:
            input_algorithm = self.input["algorithm"]
        except KeyError:
            print("<Input Validation Error> The algorithm must be defined.")
        else:
            self.validate_algorithm(input_algorithm, input_evaluators)
        return

    def validate_algorithm(self, input_algorithm, input_evaluators):
        """Validates the "algorithm" segment of the JSON input file"""

        # schema validation
        schema_algorithm = {
            "type": "object",
            "properties": {
                "parallel": {"type": "string"},
                "keep_files": {"type": "string"},
                "objective": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "weight": {
                    "type": "array",
                    "items": {"type": "number"},
                },
                "optimized_variable": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "pop_size": {"type": "number"},
                "generations": {"type": "number"},
                "mutation_probability": {"type": "number"},
                "mating_probability": {"type": "number"},
                "selection_operator": {"type": "object"},
                "mutation_operator": {"type": "object"},
                "mating_operator": {"type": "object"},
            },
        }
        validate(instance=input_algorithm, schema=schema_algorithm)
        # key validation
        self.validate_correct_keys(
            input_algorithm,
            ["optimized_variable"],
            [
                "parallel",
                "keep_files",
                "objective",
                "weight",
                "pop_size",
                "generations",
                "mutation_probability",
                "mating_probability",
                "selection_operator",
                "mutation_operator",
                "mating_operator",
            ],
            "algorithm",
        )
        self.validate_in_list(
            input_algorithm["parallel"],
            ["none", "multiprocessing", "job_control"],
            "parallel",
        )
        self.validate_in_list(
            input_algorithm["keep_files"],
            ["none", "all", "only_final"],
            "keep_files",
        )
        for obj in input_algorithm["objective"]:
            self.validate_in_list(obj, ["min", "max"], "objective")
        output_list = []
        for solver in input_evaluators:
            output_list += input_evaluators[solver]["outputs"]
        for opt_var in input_algorithm["optimized_variable"]:
            self.validate_in_list(
                opt_var,
                output_list,
                "optimized_variable",
            )

        # validation for operator sections
        self.validate_algorithm_operators("selection", input_algorithm)
        self.validate_algorithm_operators("mutation", input_algorithm)
        self.validate_algorithm_operators("mating", input_algorithm)

    def validate_algorithm_operators(self, operator_type, input_algorithm):
        """Validates the genetic algorithm operators

        Parameters
        ----------
        operator_type : str
            types are selection, mutation, and mating
        input_algorithm : dict
            algorithm sub-dictionary from input file

        """

        deap_operators = {
            "selection": {
                "selTournament": ["tournsize"],
                "selNSGA2": [],
                "selBest": [],
            },
            "mutation": {
                "mutPolynomialBounded": [
                    "eta", "indpb"], },
            "mating": {
                "cxOnePoint": [],
                "cxUniform": ["indpb"],
                "cxBlend": ["alpha"]},
        }

        try:
            op = input_algorithm[operator_type + "_operator"]
        except KeyError:
            pass
        else:
            # first check for operator
            try:
                op_op = op["operator"]
            except KeyError:
                print(
                    "<Input Validation Error> You must define an operator for "
                    + operator_type
                    + "_operator"
                )
                raise
            else:
                self.validate_in_list(
                    op_op,
                    list(deap_operators[operator_type].keys()),
                    operator_type + "_operator's operator",
                )
                schema_op = {"type": "object", "properties": {}}
                schema_op["operator"] = {"type": "string"}
                for var in deap_operators[operator_type][op_op]:
                    schema_op["properties"][var] = {"type": "number"}
                validate(
                    instance=input_algorithm[operator_type + "_operator"],
                    schema=schema_op,
                )
                self.validate_correct_keys(
                    input_algorithm[operator_type + "_operator"],
                    deap_operators[operator_type][op_op] + ["operator"],
                    [],
                    operator_type + " operator: " + op_op,
                )
        return

    def validate_constraints(self, input_constraints, input_evaluators):
        """Validates the constraints segment of the JSON input file

        Parameters
        ----------
        input_constraints : dict
            constraints sub-dictionary from input file
        input_evaluators : dict
            evaluators sub-dictionary from input file

        """

        # check if constraints are in evaluators outputs
        allowed_constraints = []
        for evaluator in input_evaluators:
            allowed_constraints += input_evaluators[evaluator]["outputs"]
        for constraint in input_constraints:
            self.validate_in_list(
                constraint,
                allowed_constraints,
                "Constraints")
        # schema validation
        schema_constraints = {"type": "object", "properties": {}}
        for constraint in input_constraints:
            schema_constraints["properties"][constraint] = {
                "type": "object",
                "properties": {
                    "operator": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "constrained_val": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                },
            }
        validate(instance=input_constraints, schema=schema_constraints)
        # key validation
        for constraint in input_constraints:
            self.validate_correct_keys(
                input_constraints[constraint],
                ["operator", "constrained_val"],
                [],
                "constraint: " + constraint,
            )
            for op in input_constraints[constraint]["operator"]:
                self.validate_in_list(
                    op,
                    [">", ">=", "=", "<", "<="],
                    constraint + "'s operator variable",
                )
        return

    def validate_ctrl_vars(self, input_ctrl_vars):
        """Validates the control variables segment of the JSON input file

        Parameters
        ----------
        input_ctrl_vars : dict
            control variables sub-dictionary from input file

        """
        # validate regular control variables
        # schema validation
        schema_ctrl_vars = {"type": "object", "properties": {}}
        variables = []
        for var in input_ctrl_vars:
            schema_ctrl_vars["properties"][var] = {
                "type": "object",
                "properties": {
                    "max": {"type": "number"},
                    "min": {"type": "number"},
                },
            }
            variables.append(var)
        validate(instance=input_ctrl_vars, schema=schema_ctrl_vars)
        # key validation
        for var in variables:
            self.validate_correct_keys(
                input_ctrl_vars[var], [
                    "min", "max"], [], "control variable: " + var)

    def validate_evaluators(self, input_evaluators):
        """Validates the evaluators segment of the JSON input file

        Parameters
        ----------
        input_evaluators : dict
            evaluators sub-dictionary from input file

        """

        schema_evaluators = {"type": "object", "properties": {}}
        # validate each evaluator
        for evaluator in input_evaluators:
            schema_evaluators["properties"][evaluator] = {
                "type": "object",
                "properties": {
                    "order": {"type": "number"},
                    "input_script": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "execute": {
                        "type": "array",
                        "items": {"type": "array"},
                    },
                    "inputs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "output_script": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
            }
        validate(instance=input_evaluators, schema=schema_evaluators)
        for evaluator in input_evaluators:
            self.validate_correct_keys(
                input_evaluators[evaluator],
                ["input_script", "inputs", "outputs", "order"],
                ["output_script", "execute"],
                "evaluator: " + evaluator,
            )
            # check if outputs are in predefined outputs or inputs, and if not
            # output_script must be defined

            in_list, which_strings = self.validate_if_in_list(
                input_evaluators[evaluator]["outputs"],
                input_evaluators[evaluator]["inputs"],
            )
            if not in_list:
                try:
                    a = input_evaluators[evaluator]["output_script"]
                except KeyError:
                    print(
                        "<Input Validation Error>"
                        + "You must define an output_script for evaluator: "
                        + evaluator
                        + " since the outputs: "
                        + str(which_strings)
                        + " are not inputs or pre-defined outputs."
                    )
                    raise
        return

    def validate_if_in_list(self, input_strings, accepted_strings):
        """Checks if strings are in a defined list of strings and returns a
        boolean

        Parameters
        ----------
        input_strings : list of str
            list of variable names to check
        accepted_strings : list of str
            list of variable names to check against

        Returns
        -------
        in_list : bool
            boolean indicating if all input_strings are in accepted_strings
        which_strings : list
            list of variables from input_strings that are not in accepted_strings

        """
        in_list = True
        which_strings = []
        for string in input_strings:
            if string not in accepted_strings:
                in_list = False
                which_strings.append(string)
        return in_list, which_strings

    def validate_in_list(self, variable, accepted_variables, name):
        """Checks if a variable is in a list of accepted variables

        Parameters
        ----------
        variable : str
            name of variable to check
        accepted_variables : list of str
            name of variables to check against
        name : str
            parameter name

        """
        assert variable in accepted_variables, (
            "<Input Validation Error> variable: "
            + name
            + ", only accepts: "
            + str(accepted_variables)
            + " not variable: "
            + variable
        )
        return

    def validate_correct_keys(
        self, dict_to_validate, key_names, optional_key_names, variable_type
    ):
        """Runs a try except routine for to check if all key names are in the
        dict_to_validate and ensure no unwanted keys are defined

        Parameters
        ----------
        dict_to_validate : dict
            dict to validate
        key_names : list of str
            names of required keys
        optional_key_names : list of str
            names of optional keys
        variable_type : str
            parameter name

        """
        try:
            combined_key_names = key_names + optional_key_names
            for key in key_names:
                a = dict_to_validate[key]
            for key in dict_to_validate:
                assert key in combined_key_names, (
                    "<Input Validation Error> Only "
                    + str(combined_key_names)
                    + " are accepted for "
                    + variable_type
                    + ", not variable: "
                    + key
                )
        except KeyError:
            print(
                "<Input Validation Error> "
                + str(key_names)
                + " variables must be defined for "
                + variable_type
            )
            raise
        except AssertionError as error:
            print(error)
            raise
        return
