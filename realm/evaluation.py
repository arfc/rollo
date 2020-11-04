import os, sys 

class Evaluation(): 
    """ This class calls various external codes 
    
    Attributes 
    ----------
    scripts = dict 
    outputs = list of str
        list of names of output variables to return 
    """

    def __init__(self, scripts, outputs):
        self.supported_codes = ['openmc', 'moltres']
        self.all_input_map = {}
        self.all_fitness_map = {} 
    
    def add_evaluator(self, code_name, input_index, fitness_index):
        self.all_input_map[code_name] = input_index 
        self.all_fitness_map[code_name] = fitness_index

    def eval_fn_generator(): 
        """ This function returns a function that accepts a DEAP individual 
        and returns a tuple of output values listed in outputs 
        """
        def eval_function(ind):
            for code in all_input_map:
                path = code + '_' + str(ind.gen) + '_' + str(ind.num)
                os.mkdir(path)
                os.chdir(path)
                

                os.chdir('../')
            return 
        return eval_function
