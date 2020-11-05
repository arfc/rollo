import os, sys 
from jinja2 import nativetypes

class Evaluation(): 
    """ This class calls various external codes 
    
    Attributes 
    ----------
    scripts = dict 
    outputs = list of str
        list of names of output variables to return 
    """

    def __init__(self):
        self.supported_codes = ['openmc', 'moltres']
        self.scripts = {}
        self.all_input_map = {}
        self.all_fitness_map = {} 
    
    def add_evaluator(self, code_name, script, input_index, fitness_index):
        if code_name not in supported_codes: 
            raise Exception('REALM does not support ' + code_name)
        self.scripts[code_name] = script
        self.all_input_map[code_name] = input_index 
        self.all_fitness_map[code_name] = fitness_index

    def eval_fn_generator(): 
        """ This function returns a function that accepts a DEAP individual 
        and returns a tuple of output values listed in outputs 
        """
        def eval_function(ind):
            for code in self.scripts:
                path = code + '_' + str(ind.gen) + '_' + str(ind.num)
                os.mkdir(path)
                os.chdir(path)
                with open(self.scripts[code], '') as file: 
                    script = file.read() 
                # jinja2 templating 
                env = nativetypes.NativeEnvironment()
                template = nativetypes.NativeTemplate(script)
                to_run = template.render(input=ind)
                exec(to_run)
                os.chdir('../')
            return 
        return eval_function
