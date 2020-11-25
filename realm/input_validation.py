from jsonschema import validate


class InputValidation():
    """ This class does the initial validation of the *.rlm input file and
    and solver's templated input scripts
    """

    def __init__(self, input_dict):
        self.input = input_dict

    def validate(self):
        """ This function validates the input dictionary and throws errors if
        the input file does not meet realm input file rules.
        """
        print('INPUT', self.input)
        # validate top layer of JSON input
        schema_top_layer = {
            "type": "object",
            "properties": {
                "control_variables": {"type": "object"},
                "evaluators": {"type": "object"},
                "constraints": {"type": "object"},
                "algorithms": {"type": "object"}
            }
        }
        validate(instance=self.input, schema=schema_top_layer)

        # validate input variables
        try:
            input_ctrl_vars = self.input["control_variables"]
        except KeyError as error:
            print("<Input Validation Error> At least 1 input variable must be defined.")
        else:
            self.validate_ctrl_vars(input_ctrl_vars)

        # validate evaluators

        # self.validate_evaluators()
        # self.validate_constraints()
        # self.validate_algorithms()

    def validate_ctrl_vars(self, input_ctrl_vars):
        """ This function validates the 'input variables' segment of the JSON
        input file.
        """
        # special input variables with a non-conforming input style defined in
        # input*** (add file name that has this)
        # add to this list if a developer adds a special input variable
        special_ctrl_vars = ['polynomial']

        # validate regular input variables
        schema_ctrl_vars = {
            "type": "object",
            "properties": {}
        }
        variables = []
        for var in input_ctrl_vars:
            if var not in special_ctrl_vars:
                schema_ctrl_vars["properties"][var] = {
                    "type": "object", "properties": {
                        "max": {
                            "type": "number"}, "min": {
                            "type": "number"}}}
                variables.append(var)
        validate(instance=input_ctrl_vars, schema=schema_ctrl_vars)
        for var in variables:
            try:
                input_ctrl_vars_var_max = input_ctrl_vars[var]['max']
                input_ctrl_vars_var_min = input_ctrl_vars[var]['min']
                for i in input_ctrl_vars[var]:
                    assert (
                        i in [
                            'max', 'min']), "Only 'max' and 'min' inputs are accepted for control variable: " + str(var)
            except KeyError as error:
                print(
                    "<Input Validation Error> min and max values must be defined for the input variable: '" +
                    var +
                    "'.")
            except AssertionError as error:
                print(error)
        print('out')
        # validate special input variables
        # add validation here if developer adds new special input variable
        # polynomial
