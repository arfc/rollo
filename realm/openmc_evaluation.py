import glob
import openmc
import time

class OpenMCEvaluation:
    """This class evaluates openmc output files.
    - To add new openmc outputs, create a function called "output_***" and
    input *** name as a str into the openmc_output list.
    """

    def __init__(self):
        self.pre_defined_outputs = ["keff"]

    def evaluate_keff(self):
        """This function analyzes the openmc output file"""
        start = time.time()
        print("eval_keff start", start)
        for file in glob.glob("statepoint*"):
            h5file = file
        print("in_1", time.time()-start)
        sp = openmc.StatePoint(h5file)
        print("in_2", time.time()-start)
        keff = sp.k_combined.nominal_value
        print("in_3", time.time()-start)
        return keff
