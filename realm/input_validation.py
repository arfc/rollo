from jsonschema import validate


class InputValidation:
    """This class does the initial validation of the *.rlm input file and
    and solver's templated input scripts
    """

    def __init__(self, input_dict):
        self.input = input_dict

    def validate(self):
        """This function validates the input dictionary and throws errors if
        the input file does not meet realm input file rules.
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
        self.validate_sub_level(
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
            self.validate_algorithm(input_algorithm, input_ctrl_vars)
        return

    def validate_algorithm(self, input_algorithm, input_ctrl_vars):
        """This function validates the "algorithm" segment of the JSON input
        file.
        """
        schema_algorithm = {
            "type": "object",
            "properties": {
                "objective": {"type": "string"},
                "optimized_variable": {"type": "string"},
                "pop_size": {"type": "number"},
                "generations": {"type": "number"},
                "selection_operator": {"type": "object"},
                "mutation_operator": {"type": "object"},
                "mating_operator": {"type": "object"},
            },
        }
        validate(instance=input_algorithm, schema=schema_algorithm)
        # validation for objective and optimized variable
        self.validate_in_list(input_algorithm["objective"], ["min", "max"], "objective")
        self.validate_in_list(
            input_algorithm["optimized_variable"],
            list(input_ctrl_vars.keys()),
            "optimized_variable",
        )
        return

    def validate_in_list(self, variable, accepted_variables, name):
        """This function checks if a variable is in a list of accepted variables"""
        assert variable in accepted_variables, (
            "<Input Validation Error> variable: "
            + name
            + ", only accepts: "
            + str(accepted_variables)
        )
        return

    def validate_constraints(self, input_constraints, input_evaluators):
        """This function validates the "constraints" segment of the JSON input
        file.
        """
        allowed_constraints = []
        for evaluator in input_evaluators:
            allowed_constraints += input_evaluators[evaluator]["outputs"]
        schema_constraints = {"type": "object", "properties": {}}
        for constraint in input_constraints:
            assert constraint in allowed_constraints, (
                "<Input Validation Error> constraint: "
                + constraint
                + " is not an output variable of any evaluator."
            )
            schema_constraints["properties"][constraint] = {
                "type": "object",
                "properties": {
                    "operator": {"type": "string"},
                    "constrained_val": {"type": "number"},
                },
            }
        validate(instance=input_constraints, schema=schema_constraints)
        for constraint in input_constraints:
            self.validate_sub_level(
                input_constraints[constraint],
                ["operator", "constrained_val"],
                [],
                "constraint: " + constraint,
            )
        return

    def validate_ctrl_vars(self, input_ctrl_vars):
        """This function validates the "control variables" segment of the JSON
        input file.
        """
        # special control variables with a non-conforming input style defined in
        # input*** (add file name that has this)
        # add to this list if a developer adds a special control variable
        special_ctrl_vars = ["polynomial"]

        # validate regular control variables
        schema_ctrl_vars = {"type": "object", "properties": {}}
        variables = []
        for var in input_ctrl_vars:
            if var not in special_ctrl_vars:
                schema_ctrl_vars["properties"][var] = {
                    "type": "object",
                    "properties": {
                        "max": {"type": "number"},
                        "min": {"type": "number"},
                    },
                }
                variables.append(var)
        validate(instance=input_ctrl_vars, schema=schema_ctrl_vars)
        for var in variables:
            self.validate_sub_level(
                input_ctrl_vars[var], ["min", "max"], [], "control variable: " + var
            )

        # validate special control variables
        # add validation here if developer adds new special input variable
        # polynomial
        try:
            input_ctrl_vars_poly = input_ctrl_vars["polynomial"]
        except KeyError:
            pass
        else:
            schema_ctrl_vars_poly = {
                "type": "object",
                "properties": {
                    "order": {"type": "number"},
                    "min": {"type": "number"},
                    "max": {"type": "number"},
                    "above_x_axis": {"type": "boolean"},
                },
            }
            validate(instance=input_ctrl_vars_poly, schema=schema_ctrl_vars_poly)
            self.validate_sub_level(
                input_ctrl_vars_poly,
                ["order", "min", "max", "above_x_axis"],
                [],
                "control variable: polynomial",
            )
        return

    def validate_evaluators(self, input_evaluators):
        """This function validates the "evaluators" segment of the JSON
        input file.
        """
        # evaluators available
        # add to this list if a developer adds a new evaluator
        available_evaluators = ["openmc"]
        # add to this dict if a developers adds a new predefined output
        # for an evaluator
        pre_defined_outputs = {"openmc": ["keff"]}

        # validate evaluators
        self.validate_sub_level(
            input_evaluators, available_evaluators, [], "evaluators"
        )
        schema_evaluators = {"type": "object", "properties": {}}

        # validate each evaluator
        for evaluator in input_evaluators:
            schema_evaluators["properties"][evaluator] = {
                "type": "object",
                "properties": {
                    "input_script": {"type": "string"},
                    "inputs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "output_script": {"type": "string"},
                },
            }
        validate(instance=input_evaluators, schema=schema_evaluators)
        for evaluator in input_evaluators:
            self.validate_sub_level(
                input_evaluators[evaluator],
                ["input_script", "inputs", "outputs"],
                ["output_script"],
                "evaluator: " + evaluator,
            )

            not_in_list, which_strings = self.validate_if_not_in_list(
                input_evaluators[evaluator]["outputs"],
                pre_defined_outputs[evaluator] + input_evaluators[evaluator]["inputs"],
            )
            if not_in_list:
                try:
                    a = input_evaluators[evaluator]["output_script"]
                except KeyError:
                    print(
                        "<Input Validation Error> You must define an output_script for evaluator: "
                        + evaluator
                        + " since the outputs: "
                        + str(which_strings)
                        + " are not inputs or pre-defined outputs."
                    )
                    raise
        return

    def validate_if_not_in_list(self, input_string, accepted_strings):
        """This function checks if string is not in a defined list of strings
        and returns a boolean.
        """
        not_in_list = False
        which_strings = []
        for string in input_string:
            if string not in accepted_strings:
                not_in_list = True
                which_strings.append(string)
        return not_in_list, which_strings

    def validate_sub_level(
        self, dict_to_validate, key_names, optional_key_names, variable_type
    ):
        """This function runs a try except routine for to check if all key
        names are in the dict_to_validate and ensure no unwanted keys are
        defined."""
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
