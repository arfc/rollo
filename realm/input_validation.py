from jsonschema import validate

class InputValidation():
    """ This class does the initial validation of the *.rlm input file and 
    and solver's templated input scripts 
    """

    def __init__(self, input_dict):
        self.input = input_dict
        self.validation_details()
    
    def validation_details(self): 
        """ This function defines the acceptable inputs for some input layers. 
        """
        # special input variables with a non-conforming input style defined in 
        # input*** (add file that has this)
        # add to this list if a developer adds a special input variable 
        self.special_input_variables = ['polynomial']
        return 
    
    def validate(self): 
        """ This function validates the input dictionary and throws errors if 
        the input file does not meet realm input file rules. 
        """
        print('INPUT',self.input)
        # validate top layer of JSON input
        schema_top_layer= {
            "type": "object", 
            "properties": {
                "input_variables": {"type": "object"}, 
                "evaluators": {"type": "object"}, 
                "constraints": {"type": "object"},
                "algorithms": {"type": "object"}
            }
        }
        validate(instance=self.input, schema=schema_top_layer)
        try:
            input_inp_vars = self.input["input_variables"]
        except KeyError as error: 
            print("<Input Validation Error> At least 1 input variable must be defined.")
        else: 
            self.validate_inp_vars(input_inp_vars)
        #self.validate_evaluators() 
        #self.validate_constraints() 
        #self.validate_algorithms()

    def validate_inp_vars(self, input_inp_vars): 
        """ This function validates the 'input variables' segment of the JSON
        input file. 
        """
        # validate regular input variables 
        schema_inp_vars = {
            "type": "object", 
            "properties": {}
        }
        variables = []
        for var in input_inp_vars:
            if var not in self.special_input_variables: 
                schema_inp_vars["properties"][var] = {"type": "object", 
                                                            "properties": {
                                                                "max": {"type": "number"}, 
                                                                "min": {"type": "number"}
                                                            }}
                variables.append(var)
        validate(instance=input_dict_input_variables, schema=schema_inp_vars)
        for var in variables: 
            try: 
                input_dict_input_variables_var_max = input_dict_input_variables[var]['max']
                input_dict_input_variables_var_min = input_dict_input_variables[var]['min']
            except KeyError as error: 
                print("<Input Validation Error> min and max values must be defined for the input variable: '"
                        + var + "'.")
        # validate special input variables 
        # add validation here if developer adds new special input variable 
        # polynomial 
        """
        try: 
            
            schema_inp_vars_polynomial = {
                "type": "object", 
                "properties": {
                    "order": {"type": "number"}, 
                    "min": {"type": "number"}, 
                    "max": {"type": "number"}, 
                    "above_x_axis": {"type": "boolean"}
                }
            }"""
        #validate(instance=input_dict_input_variables['polynomial'], schema=schema_inp_vars_polynomial)