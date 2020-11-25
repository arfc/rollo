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
        # special input variables with a non-conforming input style defined in 
        # input*** (add file name that has this)
        # add to this list if a developer adds a special input variable 
        special_inp_vars = ['polynomial']
        
        # validate regular input variables 
        schema_inp_vars = {
            "type": "object", 
            "properties": {}
        }
        variables = []
        for var in input_inp_vars:
            if var not in special_inp_vars: 
                schema_inp_vars["properties"][var] = {"type": "object", 
                                                            "properties": {
                                                                "max": {"type": "number"}, 
                                                                "min": {"type": "number"}
                                                            }}
                variables.append(var)
        validate(instance=input_inp_vars, schema=schema_inp_vars)
        for var in variables: 
            try: 
                input_inp_vars_var_max = input_inp_vars[var]['max']
                input_inp_vars_var_min = input_inp_vars[var]['min']
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
        #validate(instance=input_inp_vars['polynomial'], schema=schema_inp_vars_polynomial)