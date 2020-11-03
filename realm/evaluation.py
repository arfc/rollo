class Evaluation(): 
    """ This class calls various external codes 
    
    Attributes 
    ----------
    scripts = dict 
    outputs = list of str
        list of names of output variables to return 
    """

    def __init__(self, scripts, outputs):
        self.openmc_script = scripts.get('openmc',False)
        #self.openmc_outputs = outputs.get('openmc',False)
        self.moltres_script = scripts.get('moltres',False)
        #self.moltres_outputs = outputs.get('moltres',False)
        ### If a user adds a new code to couple with, they should add 
        ### it here too. 

    def eval_fn_generator(): 
        """ This function returns a function that accepts a DEAP individual 
        and returns a tuple of output values listed in outputs 
        """
        def eval_function():
            
            return 
        return eval_function
