import os, sys 
from jinja2 import nativetypes
sys.path.insert(1, './plugin/')
#from openmc_evaluation import OpenMCEvaluation

class Evaluation(): 
    """ This class calls various external solvers 
    
    Attributes 
    ----------
    scripts = dict 
    outputs = list of str
        list of names of output variables to return 
    """

    def __init__(self):
        self.supported_solvers = ['openmc', 'moltres']
        self.scripts = {}
        self.all_input_map = {}
        self.all_fitness_map = {} 
    
    def add_evaluator(self, solver_name, input_script, input_index, 
        fitness_index, fitness_optimizer, outputs, output_script=None):
        # create a possibility for custom output script, but there is 
        # generic outputs to use like keff etc. 
        # I need an input/output dictionary to keep track of the order 
        # of the output values 
        if solver_name not in supported_solvers: 
            raise Exception('realm does not support ' + solver_name)
        self.scripts[solver_name] = input_script
        self.all_input_map[solver_name] = input_index 
        self.all_fitness_map[solver_name] = fitness_index

    def eval_fn_generator(): 
        """ This function returns a function that accepts a DEAP individual 
        and returns a tuple of output values listed in outputs 
        """
        def eval_function(ind):
            eval_dict = {}
            output_dict = {} 
            for solver in self.scripts: 
                if solver == 'openmc': 
                    eval_dict['openmc'] = OpenMCEvaluation() 
            output_vals = []
            for solver in self.scripts:
                path = solver + '_' + str(ind.gen) + '_' + str(ind.num)
                os.mkdir(path)
                os.chdir(path)
                with open(self.scripts[solver], '') as file: 
                    script = file.read() 
                # jinja2 templating 
                env = nativetypes.NativeEnvironment()
                template = nativetypes.NativeTemplate(script)
                to_run = template.render(input=ind)
                exec(to_run)
                for oup in outputs: 
                    if oup in inputs: 
                        ## return input val
                        print('hi')
                    else: 
                        output_dict[oup] = getattr(eval_dict[solver], 
                        'evaluate_' + oup)
                os.chdir('../')
            # also add option for output script 
            # put output_dict into the right order in output_vals 
            return tuple(output_vals)
        return eval_function
