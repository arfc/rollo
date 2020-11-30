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

        # self.validate_constraints()
        # self.validate_algorithms()

    def validate_ctrl_vars(self, input_ctrl_vars):
        """This function validates the 'control variables' segment of the JSON
        input file.
        """
        # special control variables with a non-conforming input style defined in
        # input*** (add file name that has this)
        # add to this list if a developer adds a special input variable
        special_ctrl_vars = ["polynomial"]

        # validate regular input variables
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

        # validate special input variables
        # add validation here if developer adds new special input variable
        # polynomial
        try:
            input_ctrl_vars_poly = input_ctrl_vars["polynomial"]
        except:
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
        """This function validates the 'evaluators' segment of the JSON
        input file.
        """
        # evaluators available
        # add to this list if a developer adds a new evaluator
        available_evaluators = ["openmc"]

        # validate evaluators
        self.validate_sub_level(
            input_evaluators, available_evaluators, [], "evaluators"
        )
        return

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
                    + " not variable: "
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
