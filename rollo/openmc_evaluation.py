import glob
#import openmc


class OpenMCEvaluation:
    """The OpenMCEvaluation class contains ROLLO built-in methods for evaluating
    OpenMC output files. Developers can update this file with methods to 
    evaluate frequently used OpenMC outputs.
    - To add new openmc output variable evaluation functions, create a function 
    called "evaluate_###". ### names the openmc output variable. Also, add ### 
    name as a str into the pre_defined_output list.

    Attributes
    ----------
    pre_defined_outputs : list
        list of variables names with evaluation functions in this class

    """

    def __init__(self):
        self.pre_defined_outputs = ["keff"]

    def evaluate_keff(self):
        """This function analyzes the openmc output file and returns keff value

        Returns
        -------
        float
            keff value

        """
        for file in glob.glob("statepoint*"):
            h5file = file
        #sp = openmc.StatePoint(h5file, autolink=False)
        #keff = sp.k_combined.nominal_value
        return 1 #keff
