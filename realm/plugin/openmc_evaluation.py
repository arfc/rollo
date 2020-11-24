import glob
import openmc

class OpenMCEvaluation(): 
    """ This class evaluates openmc output files. 
    - To add new openmc outputs, create a function called "output_***" and 
    input *** name as a str into the openmc_output list.
    """
    
    def __init__(self):

    def evaluate_keff(): 
        """ This function analyzes the openmc output file 
        """ 
        for file in glob.glob('*.h5'): 
            h5file = file 
        sp = openmc.StatePoint(h5file)
        keff = sp.k_combined.nominal_value
        return keff  